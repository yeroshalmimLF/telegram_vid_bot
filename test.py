#!python3
import unittest

from utils import url_to_filename


class TestTelegramBot(unittest.TestCase):
    def test_url_to_filename(self):
        filename = url_to_filename("https://x.com/username/status/1234565262271123456")
        self.assertEqual(filename, "1234565262271123456.mp4")
        filename = url_to_filename("https://x.com/username/status/1234565262271123456?applebanana")
        self.assertEqual(filename, "1234565262271123456.mp4")
        filename = url_to_filename("fart.com")
        self.assertEqual(filename, "ERROR.mp4")



if __name__ == "__main__":
    unittest.main()
