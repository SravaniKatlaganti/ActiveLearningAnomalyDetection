import os

from . import data
from . import game
from . import builders

__all__ = ('dataset_type', 'game')

from .data import RootDataset, Dataset, HDF5Dataset, SingleDataset
#from .image import ImageDataset

from .builders import build

import pyworld.toolkit.tools.fileutils as __fu

__DATASETS = {}
__TOP_LEVEL_PATH = os.path.split(os.path.split(__file__)[0])[0]

def __register_dataset(dataset):
    print(dataset.name)
    if hasattr(dataset, 'children'):
        for child in dataset.children:
            __register_dataset(child)
    __DATASETS[dataset.name] = dataset

def __get_dataset(name):
    if name in __DATASETS:
        return __DATASETS[name]
    else:
        raise KeyError("Dataset {0} does not exist".format(name))

""" __register_dataset(RootDataset("mnist", __TOP_LEVEL_PATH + "/mnist/", None, children=[
    HDF5Dataset("test", "test"),
    HDF5Dataset("train", "train"),
])) """

#__register_dataset(RootDataset("avenue", __TOP_LEVEL_PATH + "/video/AvenueDataset/training_videos/", ".avi"))

__register_dataset(RootDataset("aad", __TOP_LEVEL_PATH + "/atari/", None, children=[
    Dataset("clean", "clean/", None, children = [
        HDF5Dataset("BeamRider",    "BeamRiderNoFrameskip-v4"), 
        HDF5Dataset("Breakout",     "BreakoutNoFrameskip-v4"),
        HDF5Dataset("Enduro",       "EnduroNoFrameskip-v4"),
        HDF5Dataset("Pong",         "PongNoFrameskip-v4"),
        HDF5Dataset("Qbert",        "QbertNoFrameskip-v4"),
        HDF5Dataset("Seaquest",     "SeaquestNoFrameskip-v4"),
        HDF5Dataset("SpaceInvaders","SpaceInvadersNoFrameskip-v4")
    ]),
    Dataset("raw", "raw/", None, children=[
        HDF5Dataset("BeamRider",    "BeamRiderNoFrameskip-v4"), 
        HDF5Dataset("Breakout",     "BreakoutNoFrameskip-v4"),
        HDF5Dataset("Enduro",       "EnduroNoFrameskip-v4"),
        HDF5Dataset("Pong",         "PongNoFrameskip-v4"),
        HDF5Dataset("Qbert",        "QbertNoFrameskip-v4"),
        HDF5Dataset("Seaquest",     "SeaquestNoFrameskip-v4"),
        HDF5Dataset("SpaceInvaders","SpaceInvadersNoFrameskip-v4")
    ]),
    Dataset("anomaly", "anomaly/", None, children=[
        HDF5Dataset("BeamRider",    "BeamRiderNoFrameskip-v4"), 
        HDF5Dataset("Breakout",     "BreakoutNoFrameskip-v4"),
        HDF5Dataset("Enduro",       "EnduroNoFrameskip-v4"),
        HDF5Dataset("Pong",         "PongNoFrameskip-v4"),
        HDF5Dataset("Qbert",        "QbertNoFrameskip-v4"),
        HDF5Dataset("Seaquest",     "SeaquestNoFrameskip-v4"),
        HDF5Dataset("SpaceInvaders","SpaceInvadersNoFrameskip-v4")
    ])
]))

def dataset(name):
    return __get_dataset(name)

def datasets():
    return list(__DATASETS.keys())


