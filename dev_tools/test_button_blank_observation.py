"""Deterministic regression for OpenCV's constant-template special case."""
import unittest
import numpy as np
from module.base.button import Button


class BlankObservationTest(unittest.TestCase):
    def make_button(self, animated=False):
        button = Button(area=(10, 10, 30, 30), color=(0, 0, 0),
                        button=(10, 10, 30, 30), file=None)
        texture = np.random.RandomState(42).randint(0, 255, (20, 20, 3)).astype(np.uint8)
        button.__dict__['is_gif'] = animated
        button.image = [texture] if animated else texture
        button._match_init = True
        return button, texture

    def test_blank_equal_size_observation_is_rejected_for_still_and_animation(self):
        for animated in (False, True):
            button, texture = self.make_button(animated)
            for fill in (0, 127, 255):
                frame = np.full((50, 50, 3), fill, dtype=np.uint8)
                self.assertFalse(button.match(frame, offset=(0, 0)))
            frame[10:30, 10:30] = texture
            self.assertTrue(button.match(frame, offset=(0, 0)))

    def test_nonzero_search_window_keeps_offset(self):
        button, texture = self.make_button()
        frame = np.zeros((50, 50, 3), dtype=np.uint8)
        frame[12:32, 13:33] = texture
        self.assertTrue(button.match(frame, offset=(5, 5)))
        self.assertEqual(tuple(button.button), (13, 12, 33, 32))

    def test_binary_and_luma_reject_blank_and_accept_texture(self):
        for animated in (False, True):
            for name in ('match_binary', 'match_luma'):
                button, texture = self.make_button(animated)
                frame = np.zeros((50, 50, 3), dtype=np.uint8)
                with self.subTest(animated=animated, method=name):
                    self.assertFalse(getattr(button, name)(frame, offset=(0, 0)))
                    frame[10:30, 10:30] = texture
                    self.assertTrue(getattr(button, name)(frame, offset=(0, 0)))
