"""KR requirement projects keep their identity while the timer counts down."""
import unittest
from unittest.mock import Mock, patch

from module.research import project as detection
from dev_tools.test_os_task_stop_boundaries import method


class KrResearchIdentityTest(unittest.TestCase):
    def test_uncertain_requirement_code_is_not_given_japanese_quota(self):
        with patch.object(detection, 'get_research_series_jp', return_value='S8'), \
                patch.object(detection.OCR_RESEARCH_DETAIL_KR, 'ocr', return_value='E-999-MI'), \
                patch.object(detection, 'get_research_duration_jp', return_value=7200), \
                patch.object(detection, 'get_research_cost_jp', return_value={}):
            project = detection.research_kr_detect(None)
        self.assertFalse(project.valid)

    def test_exact_requirement_code_preserves_duration_and_amount(self):
        for code, amount in [('E-031-MI', 8), ('E-315-MI', 15)]:
            with self.subTest(code=code), \
                    patch.object(detection, 'get_research_series_jp', return_value='S8'), \
                    patch.object(detection.OCR_RESEARCH_DETAIL_KR, 'ocr', return_value=code), \
                    patch.object(detection, 'get_research_duration_jp', return_value=7164), \
                    patch.object(detection, 'get_research_cost_jp', return_value={}):
                project = detection.research_kr_detect(None)
            self.assertTrue(project.valid)
            self.assertEqual(project.duration, '2')
            self.assertEqual(project.equipment_amount, amount)

    def test_unsuccessful_start_does_not_disassemble(self):
        run = method('module/research/research.py', 'RewardResearch',
                     'research_project_start_with_requirements', page_research='research')
        for result in [False, None]:
            ui = Mock()
            ui.research_project_start.return_value = result
            project = Mock(genre='E', equipment_amount=8)
            self.assertIs(run(ui, project), result)
            ui.storage_disassemble_equipment.assert_not_called()

    def test_existing_kr_project_does_not_repeat_requirement(self):
        run = method('module/research/research.py', 'RewardResearch',
                     'research_project_start_with_requirements', page_research='research')
        ui = Mock()
        ui.config.SERVER = 'kr'
        ui._kr_research_started_now = False
        ui.research_project_start.return_value = True
        self.assertTrue(run(ui, Mock(genre='E', equipment_amount=8)))
        ui.storage_disassemble_equipment.assert_not_called()
        self.assertEqual(ui.research_project_start.call_count, 2)


if __name__ == '__main__':
    unittest.main()
