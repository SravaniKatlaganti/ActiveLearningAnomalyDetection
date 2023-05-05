import os
from types import SimpleNamespace
from collections import defaultdict, OrderedDict
import copy


import pyworld.toolkit.tools.fileutils as fu
import pyworld.toolkit.tools.visutils.jupyter as J

from . import transform as T


VERBOSE = False

class DatasetException(Exception):
    pass

class MetaException(Exception):
    pass

def Loader(file):
    #print("LOADER:", file)
    return fu.load(file)

class MTransform(type):

    def __new__(cls, name, bases, dct):

        # I AM A WIZARD
        for c in T.transform.Transform.__subclasses__():
            def _property(_c=c):
                def t(self, *args, **kwargs):
                    trans = _c(*args, **kwargs)
                    self._transforms.append(trans)
                    return self
                t.__doc__ = _c.__init__.__doc__
                return t
            dct[c.__name__] = _property(_c=c)
        
        return super().__new__(cls, name, bases, dct)

class Transform(metaclass=MTransform):

    def __init__(self):
        self._transforms = []

    def transform(self, x):
        for t in self._transforms:
            x = t.transform(x)
        return x 

    def transform_meta(self, meta):
        for t in self._transforms:
            meta = t.transform_meta(meta)
        return meta

    def reset(self):
        self._transforms.clear()

class LoadIterator:

    def __init__(self, path, ext, loader=Loader, verbose=True, count=None, files=None, file_names=False):
        self.verbose = verbose
        if files is not None:
            self.files = [os.path.join(path, f) for f in files]
        else:
            self.files = sorted(fu.files_with_extention(path, ext, full=True))

        self.file_names = file_names #yield file names?
        self.loader = loader
        if count is not None:
            self.files = self.files[:count]
        self.i = 0

    def __len__(self):
        return len(self.files)

    def __iter__(self):
        if self.verbose:
            print("-- loading {0} files...".format(len(self.files)))
        return self

    def __next__(self):
        if self.i >= len(self.files):
            if self.verbose:
                print("-- done.")
            raise StopIteration()

        file = self.files[self.i]
        if self.verbose:
            print("---- {0}/{1} loading {2}".format(self.i, len(self.files), file))
        self.i += 1
        if self.file_names: 
            #print(file)
            return os.path.split(file)[1], self.loader(file)
        else:
            return self.loader(file)

class SingleDataset:

    def __init__(self, name, path):
        super(SingleDataset, self).__init__()
        self.parent = None
        self.path = path
        self.name = name
        self.__meta = None

    def load(self):
        return fu.load(self.path)

    @property
    def meta(self):
        raise NotImplementedError()

class Dataset:

    def __init__(self, name, path, ext, children=[], loader=Loader):
        super(Dataset, self).__init__()
        self.__path = path
        self.__name = name
        self.__parent = None
        self.children = children
        for child in children:
            child.__parent = self
        self.ext = ext
        self.loader = loader
        self.__meta = {}
        self.__transform = Transform()

    def files(self, full=False):
        return sorted(fu.files_with_extention(self.path, self.ext, full=False))

    def __post_init__(self, *args, **kwargs):
        try:
            self.__meta = fu.load(os.path.join(self.path, "meta.json"))
        except:
            self.__meta = {} #TODO raise an error?
        for child in self.children:
            child.__post_init__(*args, **kwargs)
            self.__meta[child.__name] = child.meta
        
    @property
    def transform(self):
        self.__transform.reset()
        return self.__transform #TODO child transform

    @property
    def parent(self):
        return self.__parent

    @property
    def path(self):
        if self.parent is not None:
            return os.path.join(self.parent.path, self.__path)
        return self.__path

    @property
    def name(self):
        if self.parent is not None:
            return "{0}.{1}".format(self.parent.name, self.__name)
        return self.__name

    def load(self, count=None, files=None):
        load_iter = LoadIterator(self.path, self.ext, count=count, loader=self.loader, verbose=VERBOSE, files=files)
        return J.progress((self.__transform.transform(x) for x in load_iter), length=len(load_iter), info="loading dataset {0}...".format(self.name))

    def load_file(self, file):
        return self.__transform.transform(fu.load(file))
    
    def load_files(self, *files):
        def gen(files):
            for file in files:
                yield self.load_file(file)
        return J.progress(gen(files), length=len(files), info="loading dataset {0}...".format(self.name))

    @property
    def meta(self):
        return Meta(**self._Dataset__transform.transform_meta(copy.deepcopy(self.__meta)))

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class RootDataset(Dataset):
    def __init__(self, *args, **kwargs):
        super(RootDataset, self).__init__(*args, **kwargs)
        self.__post_init__()
        
class HDF5Leaf(Dataset):

    def __init__(self, data, name, path):
        super(HDF5Leaf, self).__init__(name, path, '.hdf5')
        self.__data = data

    def files(self):
        return [f for f in self.__data]

    @property
    def meta(self):
        #print(self._Dataset__meta)
        return Meta(**self._Dataset__transform.transform_meta(copy.deepcopy(self._Dataset__meta)))

    def __post_init__(self, *args, **kwargs):
        raise NotImplementedError()

    def load_file(self, file):
        if isinstance(file, str):   
            return self._Dataset__transform.transform(self.__data[file][...])
        elif isinstance(file, int):
            return self._Dataset__transform.transform(list(self.__data.values())[file][...])
        else:
            raise TypeError("file {0} must be str or int".format(file))

    def load(self, count=None):
        if count is None:
            count = len(self.__data)
        def gen():
            for d in list(self.__data.values())[:count]:
                yield self._Dataset__transform.transform(d[...])
        return J.progress(gen(), length=count, info="loading dataset {0}...".format(self.name))

class HDF5Dataset(Dataset):

    def __init__(self, name, path):
        super(HDF5Dataset, self).__init__(name, path, '.hdf5', children=[])
        self.__data = None

        def _error_iter(*args, **kwargs):
             raise DatasetException("Load using children of a hdf5 dataset, parent loading may be added in the future. Available children: {0}".format(self.children))
        self.__load_iter = _error_iter
        self.__meta = None

    def load_file(self, file):
        return SimpleNamespace(**{child._Dataset__name:child.load_file(file) for child in self.children})
    
    def load_files(self, *files, close=False):
        def gen(files):
            for file in files:
                d = self.load_file(file)
                self.__data[file].close() #free memory...?
                yield d


        return J.progress(gen(files), length=len(files), info="loading dataset {0}...".format(self.name))

    def load(self, count=None):
        if count is None:
            count = len(self.__data)
        files = self.files()[:count]
        return self.load_files(*files)


    def __post_init_meta__(self):
        try:
            self.__meta = fu.load(os.path.join(self.path, "meta.json"))
        except Exception as e:
            print(e)
            self.__meta = {} #TODO raise an error?

    def __post_init__(self):
        load_iter = LoadIterator(self.path, self.ext, loader=fu.load, verbose=False, file_names=True)
        self.__data = OrderedDict([(n,d) for n,d in load_iter])
        self.__post_init_meta__()
        if len(self.__data) == 0:
            raise DatasetException("Found no data files for dataset: {0}".format(self.name))

        # get keys from a .hdf5 file (these become children of this Dataset)
        keys = next(iter(self.__data.values())).keys()
        for key in keys:
            self.__post_init_child__(key)

    def __post_init_child__(self, key):
        name = key
        #print(self.__data.items(), key)
        data = OrderedDict([(n,d[key]) for n,d in self.__data.items()])
        child = HDF5Leaf(data, name, self.path)
        child._Dataset__parent = self
        self.children.append(child)
        if key in self.__meta: #TODO otherwise? the child has no meta info...
            #print(key, self.__meta)
            child._Dataset__meta = self.__meta[key]
        self.__dict__[key] = child #add child as an attribute of this object

    @property
    def meta(self):
        meta = copy.deepcopy(self.__meta)
        for child in self.children: #update meta incase there have been any transformations on children
            meta[child._Dataset__name] = child.meta
        return Meta(**self._Dataset__transform.transform_meta(meta)) #perform any final transformations

def write_meta(dataset, meta, overwrite=False):
    path = os.path.join(dataset.path, 'meta.json')
    if not overwrite and os.path.exists(path):
        old_meta = fu.load(path)
        old_meta.update(meta)
        meta = old_meta
    fu.save(path, meta, force=True, overwrite=True)

from pprint import pformat

class Meta(SimpleNamespace):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def to_dict(self): 
        def _td(v):
            if isinstance(v, Meta):
                return v.to_dict()
            else:
                return v
        return {k:_td(v) for k,v in self.__dict__.items()}
