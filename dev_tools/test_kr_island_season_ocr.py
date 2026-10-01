"""Korean season names must not be guessed from unrelated OCR output."""
import subprocess
import sys
import unittest
import numpy as np
import ast
from pathlib import Path


class KoreanSeasonOcrTest(unittest.TestCase):
    def test_completed_task_marker_uses_korean_asset(self):
        tree = ast.parse(Path('module/island/assets.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and n.targets[0].id == 'TEMPLATE_ISLAND_SEASON_TASK_OBTAINED')
        values = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        self.assertEqual(values['file']['kr'],
                         './assets/kr/island/TEMPLATE_ISLAND_SEASON_TASK_OBTAINED.png')

    def test_season_fallback_has_ocr_margin(self):
        from module.island.korean_season_ocr import KoreanSeasonTaskOcr
        from unittest.mock import patch
        frame = np.full((30, 241, 3), 255, dtype=np.uint8)
        with patch('module.island_handler.korean_ocr.WindowsKoreanOcr') as backend:
            backend.return_value.atomic_ocr_for_single_lines.return_value = [[]]
            KoreanSeasonTaskOcr([]).ocr([frame], direct_ocr=True)
            passed = backend.return_value.atomic_ocr_for_single_lines.call_args[0][0][0]
            self.assertEqual(passed.shape, (54, 265, 3))

    def test_observed_titles_do_not_need_os_ocr(self):
        code = '''
from unittest.mock import patch
from module.config.server import set_server
set_server('kr')
from module.island.season_task import IslandSeasonTask
from module.base.utils import load_image
from module.island.data import DIC_ISLAND_TASK
ids = [80001401, 80001402, 80001405, 80001406, 80001407, 80001408, 80001409, 80001410, 80001412]
frames = [load_image('assets/kr/island_task_name/%s.png' % code) for code in ids]
ocr = IslandSeasonTask.task_name_ocr.fget(None)
with patch('module.ocr.windows_ocr.WindowsKoreanOcr.atomic_ocr_for_single_lines',
           side_effect=AssertionError('Observed exact names should not need fallback')):
    assert ocr.ocr(frames, direct_ocr=True) == [DIC_ISLAND_TASK[code]['name']['kr'] for code in ids]
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))

    def test_korean_names_are_exact_and_unknown_is_rejected(self):
        code = '''
from unittest.mock import Mock, patch
from module.config.server import set_server
set_server('kr')
from module.island.season_task import IslandSeasonTask
from module.island.data import DIC_ISLAND_SEASON
season = {1: {'start_time': {'kr': '2000-01-01 00:00:00'},
              'end_time': {'kr': '2100-01-01 00:00:00'},
              'task_list': [80001402, 80001406, 80001407]}}
ui = Mock()
with patch.dict(DIC_ISLAND_SEASON, season, clear=True):
    assert IslandSeasonTask.task_name_to_codename(ui, '애니멀 푸드') == 80001402
    assert IslandSeasonTask.task_name_to_codename(ui, ' 애니멀푸드 ') == 80001402
    assert IslandSeasonTask.task_name_to_codename(ui, '') is None
    assert IslandSeasonTask.task_name_to_codename(ui, '미확인 과제') is None
    assert IslandSeasonTask.task_name_to_codename(ui, '애니멀 푸트') is None
ocr = IslandSeasonTask.task_name_ocr.fget(ui)
assert ocr.lang == 'ko'
from module.island.korean_season_ocr import KoreanSeasonTaskOcr
assert isinstance(ocr, KoreanSeasonTaskOcr)
'''
        result = subprocess.run([sys.executable, '-B', '-c', code], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout.decode('utf-8', errors='replace'))
