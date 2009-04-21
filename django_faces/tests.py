from unittest import TestCase

class CheckPIL(TestCase):
    def testCanImportPIL(self):
        self.assert_(__import__('PIL'))

    def testPILHasZipAndPngSupport(self):
        from PIL import Image
        self.assertEqual(True, hasattr(Image.core, 'zip_encoder'))
        self.assertEqual(True, hasattr(Image.core, 'zip_decoder'))

    def testPILHasJpegSupport(self):
        from PIL import Image
        self.assertEqual(True, hasattr(Image.core, 'jpeg_encoder'))
        self.assertEqual(True, hasattr(Image.core, 'jpeg_decoder'))

