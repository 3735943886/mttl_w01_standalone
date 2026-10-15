from pathlib import Path
import hashlib,io,json,os,tempfile,threading,unittest,zipfile
from unittest.mock import patch
from engine import Engine,Cancelled
from i18n import translate,MESSAGES

class Tests(unittest.TestCase):
    def test_languages(self):
        for ko,en in MESSAGES.items():
            with self.subTest(message=ko):
                self.assertEqual(translate(ko,'ko'),ko)
                self.assertEqual(translate(ko,'en'),en)
        self.assertEqual(translate('빌드 성공: C:/Temp/output.fwr','en'),'Build succeeded: C:/Temp/output.fwr')
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.engine=Engine(self.root,{'artifacts':[]},log=lambda s:None)
    def tearDown(self):self.temp.cleanup()
    def test_paths(self):
        for name in ('../bad','/bad','C:/bad','a/../../bad','a\\..\\bad'):
            with self.subTest(name=name),self.assertRaises(RuntimeError):self.engine.safe_name(name)
    def test_safe_archive(self):
        archive=self.root/'test.zip'
        with zipfile.ZipFile(archive,'w') as z:z.writestr('source/file.txt','test')
        self.engine.extract(archive,self.root/'out','source')
        self.assertEqual((self.root/'out/source/file.txt').read_text(),'test')
    def test_traversal(self):
        archive=self.root/'test.zip'
        with zipfile.ZipFile(archive,'w') as z:z.writestr('../escape','test')
        with self.assertRaises(RuntimeError):self.engine.extract(archive,self.root/'out','source')
    def test_archive_symlink(self):
        archive=self.root/'test.zip';info=zipfile.ZipInfo('link');info.create_system=3;info.external_attr=0o120777<<16
        with zipfile.ZipFile(archive,'w') as z:z.writestr(info,'outside')
        with self.assertRaises(RuntimeError):self.engine.extract(archive,self.root/'out','source')
    def test_cancel(self):
        self.engine.cancel.set()
        with self.assertRaises(Cancelled):self.engine.check_cancel()
    def test_env(self):
        before=dict(os.environ)
        env=self.engine.env(self.root,self.root/'temp')
        self.assertEqual(dict(os.environ),before)
        self.assertNotIn('GCC_EXEC_PREFIX',env);self.assertNotIn('NODE_PATH',env)
        self.assertTrue(env['PYTHONHOME'].startswith(str(self.root)))
    def test_cache(self):
        self.engine.cache.mkdir();p=self.engine.cache/'item';p.write_bytes(b'abc')
        item={'file':'item','name':'test','sha256':hashlib.sha256(b'abc').hexdigest()}
        with patch('urllib.request.urlopen',side_effect=AssertionError('Network should not run')):
            self.assertEqual(self.engine.download(item),p)
    def test_wrong_hash(self):
        item={'file':'item','name':'test','url':'https://example.invalid/item','bytes':3,'sha256':'0'*64}
        with patch('urllib.request.urlopen',side_effect=lambda *a,**k:io.BytesIO(b'abc')):
            with self.assertRaises(RuntimeError):self.engine.download(item)
        self.assertFalse((self.engine.cache/'item').exists())
    def test_lock(self):
        with self.engine.exclusive():
            with self.assertRaises(RuntimeError):
                with Engine(self.root,{'artifacts':[]}).exclusive():pass
    def test_failed_build_no_output(self):
        source=self.root/'source';source.mkdir();(source/'mttl-source.json').write_text('{}')
        (self.engine.environment/'sdk').mkdir(parents=True)
        with patch.object(self.engine,'ready',return_value=True),patch.object(self.engine,'run',side_effect=RuntimeError('compile failed')):
            with self.assertRaises(RuntimeError):self.engine.build(source)
        self.assertFalse((self.root/'output').exists())
    def test_manifest_validation(self):
        self.assertFalse(self.engine.ready())
        with self.assertRaises(RuntimeError):self.engine.build(self.root/'no-source')
if __name__=='__main__':unittest.main(verbosity=2)
