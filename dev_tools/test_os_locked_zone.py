"""A positively locked mission is deferred without masking navigation bugs."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


class ExploreError(Exception):
    pass


class LockedError(ExploreError):
    pass


def method(path, name):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    tree.body = [next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == name)]
    scope = dict(logger=Mock(), Timer=Mock(), OSExploreError=ExploreError,
                 OSZoneLockedError=LockedError, ActionPointLimit=type('APLimit', (Exception,), {}),
                 ZONE_LOCKED='locked', ZONE_ENTRANCE='entry', AUTO_SEARCH_REWARD='reward')
    scope.update(MISSION_MONTHLY_BOSS='boss', MISSION_CHECKOUT='checkout')
    exec(compile(tree, path, 'exec'), scope)
    return scope[name]


class OsLockedZoneTest(unittest.TestCase):
    def test_explore_verified_lock_is_delayed_not_restarted(self):
        campaign = Mock()
        campaign.os_explore.side_effect = LockedError('zone 44 locked')
        ui = SimpleNamespace(config=Mock(), load_campaign=Mock(return_value=campaign))
        method('module/campaign/os_run.py', 'opsi_explore')(ui)
        ui.config.task_delay.assert_called_once_with(minute=30)
        ui.config.opsi_task_delay.assert_not_called()

    def test_explore_preserves_verified_lock_after_one_ny_retry(self):
        ui = SimpleNamespace(config=Mock(), _os_explore=Mock(side_effect=LockedError('locked')),
                             globe_goto=Mock())
        with self.assertRaises(LockedError):
            method('module/os/tasks/explore.py', 'os_explore')(ui)
        self.assertEqual(ui._os_explore.call_count, 2)
        ui.globe_goto.assert_called_once_with(0)

    def test_monthly_only_mission_exits_without_entering_boss(self):
        ui = SimpleNamespace(
            os_mission_enter=Mock(), appear=Mock(return_value=True),
            match_template_color=Mock(return_value=False), os_mission_quit=Mock(),
            globe_enter=Mock())
        run = method('module/os_handler/mission.py', 'os_get_next_mission')
        self.assertFalse(run(ui))
        ui.match_template_color.assert_called_once_with('checkout', offset=(-20, 100, 20, 150))
        ui.os_mission_quit.assert_called_once_with()
        ui.globe_enter.assert_not_called()

    def test_mission_keeps_cost_placeholder_but_labels_target_unknown(self):
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'), device=Mock(), os_mission_enter=Mock(),
            appear=Mock(return_value=False), match_template_color=Mock(return_value=True),
            is_in_opsi_explore=lambda: False, loop=lambda: iter([None]),
            is_zone_pinned=lambda: True, get_zone_pinned_name=lambda: 'DANGEROUS',
            name_to_zone=lambda value: value, globe_enter=Mock())
        run = method('module/os_handler/mission.py', 'os_get_next_mission')
        self.assertEqual(run(ui), 'pinned_at_mission_zone')
        ui.globe_enter.assert_called_once_with(zone=72, zone_label='mission target (unidentified)')
        ui.device.image_save.assert_called_once_with('./log/kr_os_mission_checkout.png')

    def test_verified_lock_has_specific_exception_and_retains_frame(self):
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'), device=Mock(), loop=lambda: iter([None]),
            get_zone_pinned_name=lambda: 'DANGEROUS', is_in_map=lambda: False,
            is_zone_pinned=lambda: True, appear=lambda *a, **kw: True)
        enter = method('module/os/globe_operation.py', 'globe_enter')
        with self.assertRaises(LockedError):
            enter(ui, 72)
        ui.device.click.assert_not_called()
        ui.device.image_save.assert_called_once_with('./log/kr_os_zone_locked.png')

    def test_mission_placeholder_is_not_reported_as_actual_zone(self):
        ui = SimpleNamespace(
            config=SimpleNamespace(SERVER='kr'), device=Mock(), loop=lambda: iter([None]),
            get_zone_pinned_name=lambda: 'DANGEROUS', is_in_map=lambda: False,
            is_zone_pinned=lambda: True, appear=lambda *a, **kw: True)
        enter = method('module/os/globe_operation.py', 'globe_enter')
        with self.assertRaisesRegex(LockedError, 'mission target') as caught:
            enter(ui, 72, zone_label='mission target')
        self.assertNotIn('72', str(caught.exception))

    def test_only_locked_missions_are_deferred_for_daily_and_archive(self):
        for name in ('opsi_daily', 'opsi_archive'):
            for error in (LockedError('locked'), ExploreError('navigation failed')):
                with self.subTest(task=name, error=type(error).__name__):
                    campaign = Mock()
                    getattr(campaign, 'os_' + name[5:]).side_effect = error
                    ui = SimpleNamespace(config=Mock(), load_campaign=Mock(return_value=campaign))
                    run = method('module/campaign/os_run.py', name)
                    if isinstance(error, LockedError):
                        run(ui)
                        ui.config.task_delay.assert_called_once_with(success=False)
                    else:
                        with self.assertRaises(ExploreError):
                            run(ui)
                        ui.config.task_delay.assert_not_called()
                    ui.config.opsi_task_delay.assert_not_called()


if __name__ == '__main__':
    unittest.main()
