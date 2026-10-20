"""Offline tests only. Never calls OpenOCD or accesses USB."""
from pathlib import Path
import tempfile,unittest,json,sys
from core import *
from engine import recover
from runtime import verify_runtime
from prepare import extract_archive,download

ROOT=Path(__file__).resolve().parents[1]
FWR=ROOT/'work/firmware/1.0.66/comMTTL-W01_1.0.66.fwr'
DUMP=ROOT/'artifacts/flash-dump-20261003/continuous-20261003-132059-1.bin'

class Fake:
    def __init__(self,data,fail=None):self.flash=bytearray(data);self.writes=[];self.reset_count=0;self.closed=False;self.reads=0;self.fail=fail
    def connect(self):return {'capacity':SIZE,'cpuid':'mock'}
    def dump(self,path,progress):
        self.reads+=1;data=bytes(self.flash)
        if self.fail=='backup' and self.reads==2:data=data[:-1]+bytes([data[-1]^1])
        if self.fail=='readback' and self.reads==3:data=data[:-1]+bytes([data[-1]^1])
        Path(path).write_bytes(data);progress(len(data),len(data));return data
    def write(self,step):
        assert allowed(step)
        if self.fail=='write' and len(self.writes)==2:raise RecoveryError('Injected write failure')
        if not step.erase:
            prior=self.flash[step.address:step.address+len(step.data)]
            assert all(a&b==b for a,b in zip(prior,step.data))
        self.flash[step.address:step.address+len(step.data)]=step.data;self.writes.append(step)
    def reset(self):self.reset_count+=1
    def close(self):self.closed=True

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.dump=DUMP.read_bytes();cls.fwr=FWR.read_bytes()
    def test_decode(self):
        raw=decode_fwr(self.fwr);self.assertEqual(len(raw),len(self.fwr));self.assertEqual(raw[101988:101995],b'1.0.66\0')
        for broken in (self.fwr[:100],raw,self.dump,b'\x00'*len(self.fwr),self.fwr[:-1]+bytes([self.fwr[-1]^1])):
            with self.assertRaises(RecoveryError):decode_fwr(broken)
    def test_backup(self):
        verify_backup(self.dump,self.dump)
        for broken in (self.dump[:-1],self.dump[:-1]+bytes([self.dump[-1]^1])):
            with self.assertRaises(RecoveryError):verify_backup(self.dump,broken)
    def test_unknown_layout(self):
        for offset in (0x18,0x9000,32):
            bad=bytearray(self.dump);bad[offset]^=1
            with self.assertRaises(RecoveryError):make_plan(bytes(bad),self.fwr)
    def test_plan(self):
        p=make_plan(self.dump,self.fwr);self.assertTrue(all(allowed(s) for s in p.steps))
        self.assertEqual(p.expected[:FIRST],self.dump[:FIRST]);self.assertEqual(p.expected[FACTORY:],self.dump[FACTORY:])
        self.assertEqual(p.expected[SETTINGS:FACTORY],b'\xff'*(FACTORY-SETTINGS))
        self.assertEqual(p.expected[FIRST+8:FIRST+16],NEW);self.assertEqual(p.expected[SECOND+8:SECOND+16],OLD)
        raw=decode_fwr(self.fwr)
        for start in (FIRST,SECOND):self.assertEqual(p.expected[start+16:start+len(raw)],raw[16:])
        phases=[s.phase for s in p.steps];self.assertLess(phases.index('activate'),phases.index('slot1'))
        self.assertFalse(allowed(Step(0,bytes(SECTOR),True,'bad')))
        self.assertFalse(allowed(Step(FACTORY,bytes(SECTOR),True,'bad')))
        self.assertFalse(allowed(Step(FIRST+1,bytes(SECTOR),True,'bad')))
    def test_all_storage_formats(self):
        for style in ('legacy','journal','torn','arbitrary'):
            data=bytearray(self.dump)
            for start,end in ((0x70000,SECOND),(0xe0000,FACTORY)):
                data[start:end]=bytes([0xa5])*(end-start)
                if style=='journal':
                    for address in range(start,end,1024):data[address:address+4]=b'J210'
                elif style=='legacy':data[start:start+4]=b'MT02'
                elif style=='torn':data[start:start+4]=b'J2\xff\xff'
            original=bytes(data);p=make_plan(original,self.fwr)
            self.assertEqual(p.expected[:FIRST],original[:FIRST])
            self.assertEqual(p.expected[FACTORY:],original[FACTORY:])
            for start,end in ((0x70000,SECOND),(0xe0000,FACTORY)):
                self.assertEqual(p.expected[start:end],b'\xff'*(end-start))
            backend=Fake(original)
            for step in p.steps:backend.write(step)
            self.assertEqual(bytes(backend.flash),p.expected)
    def run_mode(self,write,fail=None):
        with tempfile.TemporaryDirectory(prefix='recovery test 한글 ') as folder:
            b=Fake(self.dump,fail)
            if fail:
                with self.assertRaises(RecoveryError):recover(b,folder,FWR,write,lambda s:None,lambda *x:None)
            else:r=recover(b,folder,FWR,write,lambda s:None,lambda *x:None);self.assertTrue(r['completed'])
            self.assertTrue(b.closed);self.assertEqual(b.reset_count,1 if write and not fail else 0)
            result=json.loads((Path(folder)/'result.json').read_text());self.assertEqual(result['completed'],not bool(fail))
            if not write or fail=='backup':self.assertEqual(b.writes,[])
            if write and not fail:self.assertEqual(bytes(b.flash),make_plan(self.dump,self.fwr).expected)
    def test_diagnose_only(self):self.run_mode(False)
    def test_restore(self):self.run_mode(True)
    def test_bad_backup_stops_before_write(self):self.run_mode(True,'backup')
    def test_bad_readback_no_reset(self):self.run_mode(True,'readback')
    def test_write_failure_no_reset(self):self.run_mode(True,'write')
    def test_runtime_integrity(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);files={}
            for name in ('tools/openocd/bin/openocd.exe','tools/rtl8711af/rtl8710-legacy.ocd','firmware/comMTTL-W01_1.0.66.fwr'):
                path=base/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'fixture');files[name]=sha(b'fixture')
            (base/'runtime-manifest.json').write_text(json.dumps({'schema':1,'files':files}))
            self.assertEqual(verify_runtime(base),3)
            path.write_bytes(b'changed')
            with self.assertRaises(RecoveryError):verify_runtime(base)
            files['../escape']=sha(b'fixture');(base/'runtime-manifest.json').write_text(json.dumps({'schema':1,'files':files}))
            with self.assertRaises(RecoveryError):verify_runtime(base)
    def test_archive_traversal(self):
        import tarfile,io
        for name,kind in (('../escape',tarfile.REGTYPE),('/absolute',tarfile.REGTYPE),('link',tarfile.SYMTYPE)):
            with tempfile.TemporaryDirectory() as folder:
                archive=Path(folder)/'bad.tar.gz'
                with tarfile.open(archive,'w:gz') as tar:
                    member=tarfile.TarInfo(name);member.type=kind;member.size=1 if kind==tarfile.REGTYPE else 0
                    tar.addfile(member,io.BytesIO(b'x') if member.size else None)
                with self.assertRaises(RecoveryError):extract_archive(archive,Path(folder)/'out')
    def test_cached_download(self):
        with tempfile.TemporaryDirectory() as folder:
            cache=Path(folder)/'cache';cache.write_bytes(b'cached')
            download('https://invalid.example',sha(b'cached'),cache,100)
            self.assertEqual(cache.read_bytes(),b'cached')

if __name__=='__main__':unittest.main(verbosity=2)
