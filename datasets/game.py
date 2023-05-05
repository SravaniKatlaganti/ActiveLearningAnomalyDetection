import pyworld.toolkit.tools.visutils as vu
import pyworld.toolkit.tools.visutils.transform as T

__image_type = {'float':T.to_float, 'integer':T.to_integer}
__image_format = {'chw':T.CHW, 'hwc':T.HWC}

def transform(episode, image_type='float', image_format='chw', onehot=False):
    episode['state'] = __image_type[image_type](episode['state'])
    episode['state'] = __image_format[image_format](episode['state'])
    return episode


if __name__ == "__main__":
    import numpy as np
    import pyworld.toolkit.tools.fileutils as fu

    #In each game there are redundant actions - i.e. actions that have the same effects
    # Some of the actions in each game are redundant, we need to transform the actions to include only those that are distinct.
    action_transform = {"BeamRider":[],   
        "Breakout":[0,0,1,2],
        "Enduro":[],      
        "Pong":[0,0,1,2,1,2],      
        "Qbert":[],       
        "Seaquest":[],
        "SpaceInvaders":[]}

    atari_meta = {"BeamRider":dict(action_shape=(9,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "Breakout":dict(action_shape=(4,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "Enduro":dict(action_shape=(9,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "Pong":dict(action_shape=(6,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "Qbert":dict(action_shape=(6,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "Seaquest":dict(action_shape=(18,), state_shape=(210,160,3), image_format=("HWC", "RGB")), 
                 "SpaceInvaders":dict(action_shape=(6,), state_shape=(210,160,3), image_format=("HWC", "RGB"))}
    
    #fu.save("/home/ben/Documents/repos/datasets/atari/meta.json", atari_meta)

    def tweak(episode, env):
        episode = {k:v[...] for k,v in episode.items()}
        episode['action'][-1] = 0
        episode['action'] = episode['action'].astype(np.uint8)
  
        #episode['action'] = np.array(action_transform[env], dtype=np.uint8)[episode['action'].astype(np.int64)]

        #print(episode['action'].dtype, episode['state'].dtype)
        #print(episode['action'].shape, episode['state'].shape)
        #print(episode['action'][-1])
   
        return episode

    #transform actions to uint8
    for path in fu.dirs("/home/ben/Documents/repos/datasets/atari/raw", full=True):
        for file in fu.files_with_extention(path, '.hdf5', full=True):
            env = file.split("/")[-2].replace("NoFrameskip-v4","")
            episode = fu.load(file)
            episode = tweak(episode, env)
            fu.save(file, episode, force=True, overwrite=True)
        
    print("DONE")
    