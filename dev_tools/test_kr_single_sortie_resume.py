"""Interrupted single-sortie recovery must never retreat or enter a new map."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from dev_tools.test_os_task_stop_boundaries import method, TaskStopped


class End(Exception):
    pass


class SingleSortieResumeTest(TestCase):
    def runner(self, **overrides):
        values = dict(SERVER='kr', Campaign_Event='campaign_main', Campaign_Mode='normal',
                      Campaign_UseAutoSearch=True, Campaign_UseClearMode=True,
                      StopCondition_RunCount=1, Scheduler_Enable=True)
        values.update(overrides)
        return SimpleNamespace(config=SimpleNamespace(**values), run_limit=1, run_count=0,
                               campaign=Mock())

    def test_finish_only_existing_sortie(self):
        run = method('module/campaign/run.py', 'CampaignRun', '_resume_kr_single_sortie', CampaignEnd=End)
        obj = self.runner()
        obj.campaign.auto_search_execute_a_battle.side_effect = End
        self.assertTrue(run(obj))
        obj.campaign.withdraw.assert_not_called()
        obj.campaign.run.assert_not_called()
        self.assertEqual(obj.config.StopCondition_RunCount, 0)
        self.assertFalse(obj.config.Scheduler_Enable)

    def test_other_modes_unchanged(self):
        run = method('module/campaign/run.py', 'CampaignRun', '_resume_kr_single_sortie', CampaignEnd=End)
        for changes in [dict(SERVER='jp'), dict(StopCondition_RunCount=2),
                        dict(Campaign_UseAutoSearch=False), dict(Campaign_Mode='hard')]:
            obj = self.runner(**changes)
            self.assertFalse(run(obj))
            obj.campaign.auto_search_execute_a_battle.assert_not_called()

    def test_failure_does_not_debit_count_or_start_another_sortie(self):
        run = method('module/campaign/run.py', 'CampaignRun', '_resume_kr_single_sortie', CampaignEnd=End)
        obj = self.runner()
        with self.assertRaises(TaskStopped):
            run(obj)
        self.assertEqual(obj.config.StopCondition_RunCount, 1)
        obj.campaign.run.assert_not_called()
