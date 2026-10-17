"""Portable runtime integrity checks, no adapter access or system changes."""
from pathlib import Path,PurePosixPath
import json,hashlib
from core import require

def verify_runtime(home):
    home=Path(home).resolve()
    manifest=json.loads((home/'runtime-manifest.json').read_text(encoding='utf-8'))
    require(manifest.get('schema')==1 and isinstance(manifest.get('files'),dict),'Invalid runtime manifest')
    required={'tools/openocd/bin/openocd.exe','tools/rtl8711af/rtl8710-legacy.ocd','firmware/comMTTL-W01_1.0.66.fwr'}
    require(required.issubset(manifest['files']),'Incomplete runtime manifest')
    for rel,digest in manifest['files'].items():
        name=PurePosixPath(rel);path=(home/rel).resolve()
        require(not name.is_absolute() and '..' not in name.parts and path.is_relative_to(home),'Invalid runtime path')
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Runtime file missing or changed: '+rel)
    return len(manifest['files'])
