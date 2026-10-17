"""Local test package, explicit allowlists; never includes sessions or device dumps."""
from pathlib import Path
import shutil,subprocess,sys,os,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent
PYTHON=Path(sys.executable)

def main():
    env=os.environ.copy();env['PYTHONPATH']=str(PROJECT/'.tools/builder-packaging')
    subprocess.run([str(PYTHON),'-m','PyInstaller','--noconfirm','--onedir','--windowed','--name','MTTL-Recovery','--distpath',str(ROOT/'dist'),'--workpath',str(ROOT/'build'),'--specpath',str(ROOT),str(ROOT/'app.py')],check=True,cwd=ROOT,env=env)
    dist=ROOT/'dist/MTTL-Recovery';(dist/'tools').mkdir(exist_ok=True)
    shutil.copytree(PROJECT/'tools/openocd-legacy',dist/'tools/openocd',dirs_exist_ok=True)
    rtl=dist/'tools/rtl8711af';rtl.mkdir(exist_ok=True)
    for name in ('rtl8710-legacy.ocd','LICENSE'):shutil.copy2(PROJECT/'tools/rtl8711af'/name,rtl/name)
    (dist/'firmware').mkdir(exist_ok=True);shutil.copy2(PROJECT/'work/firmware/1.0.66/comMTTL-W01_1.0.66.fwr',dist/'firmware/comMTTL-W01_1.0.66.fwr')
    for name in ('README.md','README_EN.md','THIRD_PARTY_NOTICES.md','TEST_RESULT.md','LICENSE'):shutil.copy2(ROOT/name,dist/name)
    source=dist/'recovery-source';source.mkdir(exist_ok=True)
    for name in ('app.py','core.py','backend.py','engine.py','runtime.py','prepare.py','package.py'):shutil.copy2(ROOT/name,source/name)
    shutil.copytree(ROOT/'third_party',dist/'third_party',dirs_exist_ok=True)
    shutil.copytree(ROOT/'docs',dist/'docs',dirs_exist_ok=True)
    licenses=dist/'licenses';licenses.mkdir(exist_ok=True)
    for file,name in ((PYTHON.parent/'LICENSE.txt','Python-LICENSE.txt'),(PYTHON.parent/'tcl/tk8.6/license.terms','Tk-license.terms'),(PROJECT/'.tools/builder-packaging/pyinstaller-6.16.0.dist-info/licenses/COPYING.txt','PyInstaller-COPYING.txt'),(PROJECT/'tools/rtl8711af/LICENSE','GPL-2.0.txt')):shutil.copy2(file,licenses/name)
    shutil.copytree(ROOT/'licenses',licenses,dirs_exist_ok=True)
    files={}
    for p in sorted(dist.rglob('*')):
        if p.is_file() and (p.relative_to(dist).parts[0] in ('tools','firmware','_internal') or p.name=='MTTL-Recovery.exe'):
            files[p.relative_to(dist).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    (dist/'runtime-manifest.json').write_text(json.dumps({'schema':1,'files':files},indent=2),encoding='utf-8')
    subprocess.run([str(dist/'MTTL-Recovery.exe'),'--self-test'],check=True,cwd=dist,timeout=60)
    test=json.loads((dist/'self-test.json').read_text(encoding='utf-8'));assert test['self_test']=='passed' and not test['usb_accessed']
    out=ROOT/'packages';out.mkdir(exist_ok=True);archive=out/'MTTL-Recovery-1.0.0-Windows-x64.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(dist.rglob('*')):
            rel=p.relative_to(dist)
            if p.is_file() and rel.parts[0] not in ('sessions','preferences.json','self-test.json','.downloads') and not rel.as_posix().startswith('tools/openocd/'):z.write(p,Path('MTTL-Recovery')/rel)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report={'zip':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'prepared_bytes':sum(p.stat().st_size for p in dist.rglob('*') if p.is_file()),'device_accessed':False,'external_runtime_bundled':False,'physical_validation_pending':True}
    (out/'package.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
