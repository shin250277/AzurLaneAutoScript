"""Keep special daily indices consistent with normal and emergency menus."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class DailyMenuIndicesTest(unittest.TestCase):
    def setUp(self):
        path = Path('module/daily/daily.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Daily')
        cls.bases = []
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in (
            'get_daily_stage_and_fleet', 'supply_line_disruption_index', 'empty_index')]
        tree.body = [cls]
        scope = {'logger': Mock()}
        exec(compile(tree, str(path), 'exec'), scope)
        self.daily = scope['Daily']()
        names = ['EmergencyModuleDevelopment', 'EscortMission', 'AdvanceMission',
                 'FierceAssault', 'TacticalTraining', 'ModuleDevelopment']
        config = {'Daily_SupplyLineDisruption': 'second'}
        for index, name in enumerate(names, 1):
            config['Daily_' + name] = 'first'
            config['Daily_' + name + 'Fleet'] = index
        self.daily.config = SimpleNamespace(**config)

    def test_normal_supply_index_points_to_skip_only_task(self):
        self.daily.emergency_module_development = False
        self.daily.daily_current = self.daily.supply_line_disruption_index
        self.assertEqual(self.daily.get_daily_stage_and_fleet(), (2, 0))

    def test_emergency_supply_index_points_to_skip_only_task(self):
        self.daily.emergency_module_development = True
        self.daily.daily_current = self.daily.supply_line_disruption_index
        self.assertEqual(self.daily.get_daily_stage_and_fleet(), (2, 0))

    def test_normal_empty_slot_is_four(self):
        self.daily.emergency_module_development = False
        self.assertEqual(self.daily.empty_index, 4)

    def test_emergency_does_not_skip_any_of_seven_open_slots(self):
        self.daily.emergency_module_development = True
        self.assertNotIn(self.daily.empty_index, range(1, 8))

    def test_emergency_fierce_assault_keeps_its_fleet(self):
        self.daily.emergency_module_development = True
        self.daily.daily_current = 4
        self.assertEqual(self.daily.get_daily_stage_and_fleet(), (1, 4))


if __name__ == '__main__':
    unittest.main()
