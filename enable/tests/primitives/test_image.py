
import unittest

import numpy as np
from numpy.testing import assert_array_equal

from kiva.image import GraphicsContext
from traits.api import TraitError
from traits.testing.unittest_tools import UnittestTools

from enable.primitives.image import Image


class ImageTest(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.data = np.empty(shape=(128, 256, 4), dtype='uint8')
        self.data[:, :, 0] = np.arange(256)
        self.data[:, :, 1] = np.arange(128)[:, np.newaxis]
        self.data[:, :, 2] = np.arange(256)[::-1]
        self.data[:, :, 3] = np.arange(128)[::-1, np.newaxis]

        self.image_24 = Image(self.data[..., :3])
        self.image_32 = Image(self.data)

    def test_init_bad_shape(self):
        data = np.zeros(shape=(256, 256), dtype='uint8')
        with self.assertRaises(TraitError):
            Image(data=data)

    def test_init_bad_dtype(self):
        data = np.array(['red']*65536).reshape(128, 128, 4)
        with self.assertRaises(TraitError):
            Image(data=data)

    def test_set_bad_shape(self):
        data = np.zeros(shape=(256, 256), dtype='uint8')
        with self.assertRaises(TraitError):
            self.image_32.data = data

    def test_set_bad_dtype(self):
        data = np.array(['red']*65536).reshape(128, 128, 4)
        with self.assertRaises(TraitError):
            self.image_32.data = data

    def test_format(self):
        self.assertEqual(self.image_24.format, 'rgb24')
        self.assertEqual(self.image_32.format, 'rgba32')

    def test_format_change(self):
        image = self.image_24
        with self.assertTraitChanges(image, 'format'):
            image.data = self.data

        self.assertEqual(self.image_24.format, 'rgba32')

    def test_bounds_default(self):
        self.assertEqual(self.image_24.bounds, [256, 128])
        self.assertEqual(self.image_32.bounds, [256, 128])

    def test_bounds_overrride(self):
        image = Image(self.data, bounds=[200, 100])
        self.assertEqual(image.bounds, [200, 100])

    def test_size_hint(self):
        self.assertEqual(self.image_24.layout_size_hint, (256, 128))
        self.assertEqual(self.image_32.layout_size_hint, (256, 128))

    def test_size_hint_change(self):
        data = np.zeros(shape=(256, 128, 3), dtype='uint8')
        image = self.image_24
        with self.assertTraitChanges(image, 'layout_size_hint'):
            image.data = data

        self.assertEqual(self.image_24.layout_size_hint, (128, 256))

    def test_image_gc_24(self):
        # this is non-contiguous, because data comes from slice
        image_gc = self.image_24._image
        assert_array_equal(image_gc.bmp_array, self.data[..., :3])

    def test_image_gc_32(self):
        # this is contiguous
        image_gc = self.image_32._image
        assert_array_equal(image_gc.bmp_array, self.data)

    def test_draw_24(self):
        gc = GraphicsContext((256, 128), pix_format='rgba32')
        self.image_24.draw(gc)
        # if test is failing, uncomment this line to see what is drawn
        #gc.save('test_image_draw_24.png')

        # smoke test: image isn't all white
        assert_array_equal(gc.bmp_array[..., :3], self.data[..., :3])

    def test_draw_32(self):
        gc = GraphicsContext((256, 128), pix_format='rgba32')
        self.image_32.draw(gc)
        # if test is failing, uncommetn this line to see what is drawn
        #gc.save('test_image_draw_32.png')

        # smoke test: image isn't all white
        # XXX actually compute what it should look like with alpha transfer
        white_image = np.ones(shape=(256, 128, 4), dtype='uint8')*255
        self.assertFalse(np.array_equal(white_image, gc.bmp_array))
