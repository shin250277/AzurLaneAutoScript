"""Offline regression: one-hit mode must not override assist opt-out."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class MetaRequestAssistTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/os_ash/meta.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body
                   if isinstance(n, ast.ClassDef) and n.name == 'OpsiAshBeacon')
        tree.body = [next(n for n in cls.body
                          if isinstance(n, ast.FunctionDef) and n.name == '_pre_attack')]
        self.scope = dict(BEACON_LIST='beacon', DOSSIER_LIST='dossier',
                          META_AUTO_ATTACK_START='auto', logger=Mock(),
                          _server_support_dossier_auto_attack=lambda: True)
        exec(compile(tree, str(path), 'exec'), self.scope)
        self.instance = SimpleNamespace(
            config=SimpleNamespace(OpsiAshBeacon_OneHitMode=True,
                                   OpsiAshBeacon_RequestAssist=False,
                                   OpsiAshBeacon_DossierAutoAttackMode=False),
            appear=Mock(side_effect=lambda button, **kwargs: button == 'beacon'),
            _ask_for_help=Mock(return_value=True),
            _dossier_auto_attack=Mock(return_value=True))

    def run_pre_attack(self):
        return self.scope['_pre_attack'](self.instance)

    def test_one_hit_does_not_override_assist_opt_out(self):
        self.assertTrue(self.run_pre_attack())
        self.instance._ask_for_help.assert_not_called()

    def test_normal_mode_respects_assist_opt_out(self):
        self.instance.config.OpsiAshBeacon_OneHitMode = False
        self.assertTrue(self.run_pre_attack())
        self.instance._ask_for_help.assert_not_called()

    def test_explicit_assist_enabled_in_both_modes(self):
        for one_hit in (False, True):
            with self.subTest(one_hit=one_hit):
                self.instance.config.OpsiAshBeacon_OneHitMode = one_hit
                self.instance.config.OpsiAshBeacon_RequestAssist = True
                self.instance._ask_for_help.reset_mock()
                self.assertTrue(self.run_pre_attack())
                self.instance._ask_for_help.assert_called_once_with()

    def test_finished_during_assist_returns_false(self):
        self.instance.config.OpsiAshBeacon_RequestAssist = True
        self.instance._ask_for_help.return_value = False
        self.assertFalse(self.run_pre_attack())

    def test_dossier_auto_attack_does_not_request_assist(self):
        self.instance.appear.side_effect = lambda button, **kwargs: button in ('dossier', 'auto')
        self.instance.config.OpsiAshBeacon_DossierAutoAttackMode = True
        self.assertTrue(self.run_pre_attack())
        self.instance._dossier_auto_attack.assert_called_once_with()
        self.instance._ask_for_help.assert_not_called()

    def test_unknown_page_does_not_request_assist(self):
        self.instance.appear.side_effect = None
        self.instance.appear.return_value = False
        self.assertFalse(self.run_pre_attack())
        self.instance._ask_for_help.assert_not_called()


if __name__ == '__main__':
    unittest.main()
