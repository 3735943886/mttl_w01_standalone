"""Pinned upstream downloads into the application folder; no system install."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,shutil,tarfile,urllib.request,uuid
from core import require

OPENOCD_URL='https://github.com/openocd-org/openocd/releases/download/v0.12.0/openocd-v0.12.0-i686-w64-mingw32.tar.gz'
OPENOCD_SHA='d7168545a6d5df4772b6090d470650f3eb8c9732dbd19b1f9027824c7f4a6fa3'
FWR_SHA='d780b578af69d52f3a05191a8e7d91a20e05085a912722327481cd5663682c04'

def download(url,sha,target,limit):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==sha:return
    temporary=target.with_suffix('.partial')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MTTL-Recovery/1.1'}),timeout=30) as response,temporary.open('wb') as out:
        total=0
        while True:
            chunk=response.read(65536)
            if not chunk:break
            total+=len(chunk);require(total<=limit,'Download exceeds size limit');out.write(chunk)
        out.flush();os.fsync(out.fileno())
    require(hashlib.sha256(temporary.read_bytes()).hexdigest()==sha,'Download SHA-256 mismatch')
    os.replace(temporary,target)

def extract_archive(archive,destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=False);total=0
    with tarfile.open(archive,'r:gz') as tar:
        for member in tar:
            name=PurePosixPath(member.name);path=(destination/member.name).resolve()
            require(not name.is_absolute() and '..' not in name.parts and path.is_relative_to(destination.resolve()),'Invalid archive path')
            if member.isdir():path.mkdir(parents=True,exist_ok=True);continue
            require(member.isfile() and 0<=member.size<=32*1024*1024,'Archive links/special files are not supported')
            total+=member.size;require(total<=64*1024*1024,'Archive too large')
            path.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(member) as src,path.open('xb') as out:shutil.copyfileobj(src,out)

def ensure_dependencies(home,log):
    home=Path(home);manifest=json.loads((home/'runtime-manifest.json').read_text(encoding='utf-8'))['files']
    firmware=home/'firmware/comMTTL-W01_1.0.66.fwr'
    require(firmware.is_file() and hashlib.sha256(firmware.read_bytes()).hexdigest()==FWR_SHA,'Included stock firmware missing or corrupted; extract the complete recovery ZIP again')
    runtime={p:d for p,d in manifest.items() if p.startswith('tools/openocd/')}
    require(bool(runtime),'Missing pinned runtime files')
    if not all((home/p).is_file() and hashlib.sha256((home/p).read_bytes()).hexdigest()==d for p,d in runtime.items()):
        log('PREPARE OPENOCD');cache=home/'.downloads/openocd-0.12.0.tar.gz';download(OPENOCD_URL,OPENOCD_SHA,cache,16*1024*1024)
        stage=home/'tools'/('openocd-stage-'+uuid.uuid4().hex);extract_archive(cache,stage)
        for rel,digest in runtime.items():require(hashlib.sha256((stage/rel.removeprefix('tools/openocd/')).read_bytes()).hexdigest()==digest,'OpenOCD extracted file mismatch')
        target=home/'tools/openocd'
        if target.exists():os.replace(target,home/'tools'/('openocd-previous-'+uuid.uuid4().hex))
        os.replace(stage,target)
