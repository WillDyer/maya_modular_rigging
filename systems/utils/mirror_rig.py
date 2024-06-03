import maya.cmds as cmds
import importlib

def collect_mirror_data(systems_to_be_made):
    for key in systems_to_be_made.values():
        print(key)
        mirror_attribute = cmds.getAttr(f"{key['master_guide']}.{key['master_guide']}_mirror_jnts")
        print(f"Mirror: {mirror_attribute}")
        
        if mirror_attribute == 1: # YES
            cmds.select(key["joints"][0])
            cmds.mirrorJoint(mirrorYZ=True,mirrorBehavior=True,searchReplace=('_l_', '_r_'))
            
            print("TO BE MIRROED")
            print(systems_to_be_made)
