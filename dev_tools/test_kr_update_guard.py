import pathlib
import subprocess
import tempfile
import unittest
import stat

from deploy.kr_update import fast_forward
from unittest.mock import patch


class Guard(unittest.TestCase):
    def test_real_git_update_and_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = pathlib.Path(tmp)
            src, dst = r/'src', r/'dst'
            branch = 'codex/kr-fixture'
            def git(*args):
                subprocess.check_output(['git', *map(str,args)], stderr=subprocess.STDOUT)
            def commit(path):
                git('-C',path,'add','a')
                git('-C',path,'-c','user.name=test','-c','user.email=test@localhost','commit','-qm','fixture')
            git('init','-q',src)
            git('-C',src,'checkout','-qb',branch)
            (src/'a').write_text('one')
            commit(src)
            git('clone','-q',src,dst)
            remote = subprocess.check_output(['git','-C',str(dst),'remote','get-url','origin']).decode().strip()
            (src/'a').write_text('two')
            commit(src)
            original = subprocess.check_output
            with patch('deploy.kr_update.subprocess.check_output',side_effect=lambda *a,**kw:original(*a,cwd=str(dst),**kw)):
                fast_forward('git',branch,remote)
                self.assertEqual((dst/'a').read_text(),'two')
                with self.assertRaises(RuntimeError): fast_forward('git','master',remote)
                (dst/'a').write_text('local')
                with self.assertRaises(RuntimeError): fast_forward('git',branch,remote)
                commit(dst)
                with self.assertRaises(subprocess.CalledProcessError): fast_forward('git',branch,remote)
                self.assertEqual((dst/'a').read_text(),'local')
            # Python 3.7 cannot clean up read-only Git objects on Windows.
            for item in r.rglob('*'):
                if item.is_file():
                    item.chmod(stat.S_IREAD | stat.S_IWRITE)
