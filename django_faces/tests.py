from unittest import TestCase

try:
    from PIL import Image
except ImportError:
    import Image


class CheckPIL(TestCase):
    def testCanImportPIL(self):
        self.assert_(__import__('PIL'))

    def testPILHasZipAndPngSupport(self):
        self.assertEqual(True, hasattr(Image.core, 'zip_encoder'))
        self.assertEqual(True, hasattr(Image.core, 'zip_decoder'))

    def testPILHasJpegSupport(self):
        self.assertEqual(True, hasattr(Image.core, 'jpeg_encoder'))
        self.assertEqual(True, hasattr(Image.core, 'jpeg_decoder'))

