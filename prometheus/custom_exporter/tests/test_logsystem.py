import logging
import unittest
from logsystem import get_logger


class TestGetLogger(unittest.TestCase):
    def test_get_logger(self):
        """Test the logger system
        """
        logger_name = "test_logger"
        log = get_logger(logger_name)
        self.assertEqual(log.name, logger_name)
        self.assertEqual(log.level, logging.DEBUG)
        self.assertFalse(log.propagate)
        self.assertTrue(len(log.handlers) > 0)


if __name__ == '__main__':
    unittest.main()
