import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image
from module.guild.logistics import GUILD_EXCHANGE_LIMIT


class GuildExchangeDigits(unittest.TestCase):
    def test_actual_counter_glyphs_and_blank(self):
        inputs = []
        for digit in ('0', '3'):
            path = Path(__file__).parent / 'fixtures' / 'kr_guild_limit' / (digit + '.png')
            with Image.open(str(path)) as im:
                inputs.append(np.array(im.convert('RGB')))
        inputs.append(np.zeros_like(inputs[0]))
        ocr = GUILD_EXCHANGE_LIMIT
        with patch('module.config.server.server', 'kr'):
            raw = ocr.cnocr.atomic_ocr_for_single_lines([ocr.pre_process(i) for i in inputs], ocr.alphabet)
        self.assertEqual([''.join(value) for value in raw[:2]], ['0', '3'])
        self.assertFalse(ocr.after_process(''.join(raw[2])))
