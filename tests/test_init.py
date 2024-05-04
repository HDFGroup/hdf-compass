import unittest

from hdf_compass.utils import __version__


class TestHDFCompass(unittest.TestCase):

    def test_version(self):
        self.assertEqual(len(__version__.split(".")), 3)
        self.assertGreaterEqual(int(__version__.split(".")[0]), 0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHDFCompass))
    return s
