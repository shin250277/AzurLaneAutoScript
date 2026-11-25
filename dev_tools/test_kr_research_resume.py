import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

from module.research.kr_resume import can_resume_zero_requirement


class ResearchResumeTest(unittest.TestCase):
    def run_recovery(self, confirmations):
        path = Path('module/research/research.py')
        tree = ast.parse(path.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RewardResearch')
        tree.body = [next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                          and n.name == 'research_resume_interrupted_requirement')]
        scope = dict(RESEARCH_STOP='stop', page_research='research', logger=Mock())
        exec(compile(tree, str(path), 'exec'), scope)
        handler = SimpleNamespace(config=Mock(SERVER='kr'), device=Mock(), appear=Mock(return_value=True),
                                  research_detail_quit=Mock(), storage_disassemble_equipment=Mock(),
                                  ui_ensure=Mock())
        handler.config.task_stop.side_effect = StopIteration
        with patch('module.base.utils.load_image', return_value=np.zeros((21, 53, 3))), \
                patch('module.research.project.OCR_RESEARCH_DETAIL_KR.ocr', return_value='E-315-MI'), \
                patch('module.research.kr_resume.can_resume_zero_requirement', side_effect=confirmations):
            try:
                scope['research_resume_interrupted_requirement'](handler)
            except StopIteration:
                pass
        return handler

    def test_unconfirmed_second_frame_does_not_consume(self):
        handler = self.run_recovery([True, False])
        handler.storage_disassemble_equipment.assert_not_called()
        handler.research_detail_quit.assert_not_called()

    def test_confirmed_zero_resumes_once_without_cancel_or_restart_purchase(self):
        handler = self.run_recovery([True, True])
        handler.storage_disassemble_equipment.assert_called_once_with(rarity=1, amount=15)
        handler.config.task_delay.assert_called_once_with(minute=0)
        handler.config.task_stop.assert_called_once()
        self.assertTrue(handler._kr_requirement_resume_attempted)

    def test_only_observed_project_and_unchanged_zero_progress(self):
        label = np.asarray(Image.open('assets/kr/research/REQUIREMENT_ZERO_15.png').convert('RGB'))
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[529:550, 1052:1105] = label
        self.assertTrue(can_resume_zero_requirement('E-315-MI', frame, label))
        self.assertFalse(can_resume_zero_requirement('E-031-MI', frame, label))
        self.assertFalse(can_resume_zero_requirement('', frame, label))
        self.assertFalse(can_resume_zero_requirement('E-315-MI', np.zeros_like(frame), label))
        # Any changed glyph must fail rather than interpreting it as zero.
        changed = frame.copy()
        changed[535, 1064] = 255 - changed[535, 1064]
        self.assertFalse(can_resume_zero_requirement('E-315-MI', changed, label))


if __name__ == '__main__':
    unittest.main()
