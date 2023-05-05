import os
from pprint import pprint

from collections import defaultdict

import pyworld.toolkit.tools.fileutils as fu

class DatasetBuilderException(Exception):
    pass

VERBOSE = True

# ================== META BUILDERS ================ #

def hdf5_meta(files):
    assert len(files) > 0

    def validate(files):

        def traverse(data): #TODO only checks 1 level deep...
            #validates the hierarchy of hdf5 files
            keys = set(data[0].keys())
            for d in data[1:]:
                if keys != set(d.keys()):
                    raise DatasetBuilderException("HDF5 files have a different hierarchy, failed to build dataset.")
            return keys
        
        data = [fu.load(f) for f in files]
        keys = traverse(data)

        for k in keys:
            n = sum([d[k].shape[0] for d in data])
        




            #print(data.shape)

    validate(files)

        #fu.save(os.path.join(path, 'meta.json'), None, force=True, overwrite=True)

#write more builders!         

# ================================================== #



meta_builders = {'.hdf5':hdf5_meta}


def build(path, blacklist=[], whitelist=[]):
    def filter_files(path):
        return fu.filter(fu.files(path, full=True), blacklist=blacklist, whitelist=whitelist)

    def filter_dirs(path):
        return fu.filter(fu.dirs(path, full=True), blacklist=['*/.*'])

    def write_meta(path):
        files = filter_files(path)
        #pprint(files)

        if len(files) > 0: #process files and write meta.json
            sfiles = defaultdict(list)
            for f in files:
                ext = os.path.splitext(f)[1]
                sfiles[ext].append(f)
            #print(sfiles.keys())
            assert len(sfiles) == 1 #multiple files types not yet supported, for the moment it is best to whitelist the file type that should be used to build the dataset
                        
            if VERBOSE:
                print("---- FOUND: {0} files in directory {1}".format(len(next(iter(sfiles.values()))), path))

            for ext,fs in sfiles.items():
                meta_builders[ext](fs) #append to meta.json for each file type




        dirs = filter_dirs(path)
        #pprint(dirs)
        for p in dirs:
            write_meta(p)

    write_meta(path)


