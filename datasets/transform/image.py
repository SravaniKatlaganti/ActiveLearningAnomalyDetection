import numpy as np
import re

import pyworld.toolkit.tools.visutils.transform as T
from .transform import Transform

def validate_format(format):
    re1 = r'[N]?[C]?HW'
    re2 = r'[N]?HW[C]?'
    #TODO

class crop(Transform):

    def __init__(self, xsize=None, ysize=None):
        """ Crop transformation for image data.

        Args:
            xsize ([tuple], optional): (x1,x2) coordinates to reduce the image width. Defaults to None.
            ysize ([tuple], optional): (y1,y2) coordinates to reduce the image height. Defaults to None.
        """
        super(crop, self).__init__()
        self.xsize = xsize
        self.ysize = ysize

    def transform(self, x):
        return T.crop_all(x, xsize=self.xsize, ysize=self.ysize)

    def transform_meta(self, meta):
        shape = list(meta['shape'])
        format = meta['format'][0] #e.g. (HWC, RBG)

        if self.xsize is not None:
            wi = format.index('W')
            shape[wi] = self.xsize[1] - self.xsize[0]

        if self.ysize is not None:     
            hi = format.index('H')
            shape[hi] = self.ysize[1] - self.ysize[0]

        meta['shape'] = tuple(shape)
        return meta

class to_float(Transform):

    def __init_(self):
        super(to_float, self).__init__()

    def transform(self, x):
        return T.to_float(x)

    def transform_meta(self, meta):
        meta['dtype'] = 'float32'
        return meta


class to_integer(Transform):

    def __init_(self):
        super(to_int, self).__init__()

    def transform(self, x):
        return T.to_integer(x)

    def transform_meta(self, meta):
        meta['dtype'] = 'uint8'
        return meta





class CHW(Transform):

    def __init_(self):
        super(CHW, self).__init__()

    def transform(self, x):
        return T.CHW(x)

    def transform_meta(self, meta):
        meta['format'][0] = meta['format'][0].replace('HWC', 'CHW')
        shape = meta['shape']
        shape.insert(-2, shape.pop(-1))
        meta['shape'] = shape

        return meta


class HWC(Transform):

    def __init_(self):
        super(HWC, self).__init__()

    def transform(self, x):
        return T.HWC(x)

    def transform_meta(self, meta):
        meta['format'][0] = meta['format'][0].replace('CHW', 'HWC')

        shape = list(meta['shape'])
        shape.append(shape.pop(-3))
        meta['shape'] = shape

        return meta


'''
    class ScaleTransform:

        def __init__(self, scale, interpolation=T.interpolation.area):
            self.scale = scale
            self.interpolation = interpolation


    def scale(self, meta, scale, interpolation=T.interpolation.area):
        self.add_transform(_t(T.scale_all, scale, interpolation=interpolation))
    
    def resize(self, meta, size, interpolation=T.interpolation.area):
        self.add_transform(_t(T.resize_all, size, interpolation=interpolation))

    def binarize(self, meta, threshold=0.5):
        self.add_transform(_t(T.binary_all, threshold=threshold))
    
    def gray(self, meta, weights=(0.299, 0.587, 0.114)):
        self.add_transform(_t(T.gray_all, components=weights))
    
    def CHW(self, meta):
        self.add_transform(_t(T.CHW))

    def HWC(self, meta):
        self.add_transform(_t(T.HWC))

    def to_float(self, meta):
        self.add_transform(_t(T.to_float))

    def to_int(self, meta):
        self.add_transform(_t(T.to_int))
'''



if __name__ == "__main__":
    print(Transform.__subclasses__())
