from abc import ABC, abstractmethod

try:
    import torch as _torch
except:
    pass #torch transform wont work... oh well...

try:
    import numpy as np
except:
    pass #numpy transforms wont work... oh well


class Transform:

    def __init__(self, *args, **kwargs):
        super(Transform, self).__init__(*args, **kwargs)
    
    @abstractmethod
    def transform(self, x):
        pass
    
    @abstractmethod
    def transform_meta(self, meta):
        pass

class torch(Transform):

    def __init__(self, device='cpu'):
        super(torch, self).__init__()
        self.device = device

    def transform(self, x):
        return _torch.from_numpy(x).to(self.device)

    def transform_meta(self, meta):
        return meta

class onehot(Transform):
    
    def __init__(self, size):
        super(onehot, self).__init__()
        self.size = size

    def transform(self, x):
        print(x.shape, self.size)
        x = x.astype(np.int64)
        r = np.zeros((x.shape[0], self.size), dtype=np.float32)
        r[np.arange(x.shape[0]), x] = 1
        return r
    
    def transform_meta(self, meta):
        meta['shape'] = (self.size,)
        meta['dtype'] = np.float32
        return meta