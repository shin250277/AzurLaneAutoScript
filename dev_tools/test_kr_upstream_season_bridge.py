"""Offline proof that upstream namespaces use the KR release and deadline."""
from datetime import datetime
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from module.island import utils


class KoreanSeasonBridge(unittest.TestCase):
    def test_generated_setting_and_deadline_agree(self):
        args = json.loads(Path('module/config/argument/args.json').read_text(encoding='utf-8'))
        options = args['IslandGeneral']['IslandGeneral']['Season']['option_kr']
        self.assertEqual(options, ['season_20261105_cn'])
        with patch.object(utils.server, 'server', 'kr'):
            season = utils.get_season_data(options[0])
            self.assertEqual(set(season['activity']), {990027, 990028, 990029, 990030})
            self.assertEqual(utils.get_season_remaining_days(season, datetime(2027, 2, 16, 12)), 1)
            self.assertEqual(utils.get_season_remaining_days(season, datetime(2027, 2, 17, 12)), 0)
