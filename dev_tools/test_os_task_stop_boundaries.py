"""Device-free checks before live KR coordinate/stronghold verification.

These exercise production control flow; they do not validate map recognition.
"""
import ast
from contextlib import nullcontext
from pathlib import Path
import unittest
from unittest.mock import Mock


class TaskStopped(Exception):
    pass


class ActionPointLimit(Exception):
    pass


def method(relative_path, class_name, name, **symbols):
    path = Path(__file__).resolve().parents[1] / relative_path
    tree = ast.parse(path.read_text(encoding='utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == class_name)
    tree.body = [next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                      and node.name == name)]
    scope = dict(logger=Mock(), get_os_reset_remain=lambda: 10,
                 RequestHumanTakeover=TaskStopped, ActionPointLimit=ActionPointLimit)
    scope.update(symbols)
    exec(compile(tree, str(path), 'exec'), scope)
    return scope[name]


class OsTaskStopBoundariesTest(unittest.TestCase):
    def setUp(self):
        self.ui = Mock()
        self.ui.config.task_stop.side_effect = TaskStopped
        self.ui.config.temporary.side_effect = lambda **kwargs: nullcontext()
        self.ui.config.OpsiObscure_ForceRun = False

    def test_missing_obscure_coordinate_stops_before_map_actions(self):
        self.ui.storage_get_next_item.return_value = False
        clear = method('module/os/tasks/obscure.py', 'OpsiObscure', 'clear_obscure')
        with self.assertRaises(TaskStopped):
            clear(self.ui)
        self.ui.config.task_delay.assert_called_once_with(server_update=True)
        self.ui.zone_init.assert_not_called()
        self.ui.run_auto_search.assert_not_called()

    def test_missing_abyssal_coordinate_stops_before_combat(self):
        self.ui.storage_get_next_item.return_value = False
        delay = method('module/os/tasks/abyssal.py', 'OpsiAbyssal', 'delay_abyssal')
        self.ui.delay_abyssal.side_effect = lambda **kwargs: delay(self.ui, **kwargs)
        clear = method('module/os/tasks/abyssal.py', 'OpsiAbyssal', 'clear_abyssal')
        with self.assertRaises(TaskStopped):
            clear(self.ui)
        self.ui.run_abyssal.assert_not_called()
        self.ui.zone_init.assert_not_called()

    def test_failed_abyssal_combat_does_not_continue_as_success(self):
        self.ui.storage_get_next_item.return_value = True
        self.ui.run_abyssal.return_value = False
        clear = method('module/os/tasks/abyssal.py', 'OpsiAbyssal', 'clear_abyssal')
        with self.assertRaises(TaskStopped):
            clear(self.ui)
        self.ui.fleet_repair.assert_not_called()
        self.ui.delay_abyssal.assert_not_called()

    def test_missing_stronghold_stops_before_entering_any_zone(self):
        self.ui.find_siren_stronghold.return_value = None
        clear = method('module/os/tasks/stronghold.py', 'OpsiStronghold', 'clear_stronghold')
        with self.assertRaises(TaskStopped):
            clear(self.ui)
        self.ui.globe_enter.assert_not_called()
        self.ui.run_stronghold.assert_not_called()

    def test_obscure_without_force_run_returns_after_one_coordinate(self):
        run = method('module/os/tasks/obscure.py', 'OpsiObscure', 'os_obscure')
        run(self.ui)
        self.ui.clear_obscure.assert_called_once_with()

    def test_failed_stronghold_stops_before_repair_and_retry(self):
        self.ui.run_stronghold.return_value = False
        clear = method('module/os/tasks/stronghold.py', 'OpsiStronghold', 'clear_stronghold')
        self.ui.clear_stronghold.side_effect = lambda: clear(self.ui)
        # Bound the old outer loop so the regression cannot hang.
        self.ui.config.check_task_switch.side_effect = AssertionError('Failed battle returned to retry loop')
        run = method('module/os/tasks/stronghold.py', 'OpsiStronghold', 'os_stronghold')
        with self.assertRaises(TaskStopped):
            run(self.ui)
        self.ui.run_stronghold.assert_called_once_with()
        self.ui.fleet_repair.assert_not_called()
        self.ui.handle_fleet_resolve.assert_not_called()
        self.ui.config.check_task_switch.assert_not_called()

    def test_successful_stronghold_keeps_repair_path(self):
        self.ui.run_stronghold.return_value = True
        clear = method('module/os/tasks/stronghold.py', 'OpsiStronghold', 'clear_stronghold')
        clear(self.ui)
        self.ui.fleet_repair.assert_called_once_with(revert=False)
        self.ui.handle_fleet_resolve.assert_called_once_with(revert=False)

    def test_repeating_tasks_honor_scheduler_stop_between_zones(self):
        for name, cls in (('abyssal', 'OpsiAbyssal'), ('stronghold', 'OpsiStronghold')):
            with self.subTest(task=name):
                ui = Mock()
                ui.config.check_task_switch.side_effect = TaskStopped
                run = method('module/os/tasks/' + name + '.py', cls, 'os_' + name)
                with self.assertRaises(TaskStopped):
                    run(ui)
                getattr(ui, 'clear_' + name).assert_called_once_with()

    def test_ap_shortage_is_delayed_without_retrying_campaign(self):
        for name in ('explore', 'shop', 'voucher', 'daily', 'obscure', 'month_boss',
                     'abyssal', 'archive', 'stronghold'):
            for stage in ('initialization', 'task'):
                with self.subTest(task=name, stage=stage):
                    ui = Mock()
                    ui.config.SERVER = 'kr'
                    if stage == 'initialization':
                        ui.load_campaign.side_effect = ActionPointLimit
                    else:
                        campaign_method = 'clear_month_boss' if name == 'month_boss' else 'os_' + name
                        getattr(ui.load_campaign.return_value, campaign_method).side_effect = ActionPointLimit
                    run = method('module/campaign/os_run.py', 'OSCampaignRun', 'opsi_' + name)
                    run(ui)
                    ui.load_campaign.assert_called_once_with()
                    ui.config.opsi_task_delay.assert_called_once_with(ap_limit=True)


if __name__ == '__main__':
    unittest.main()
