import maya.cmds as cmds

def update_guide_position(guide_list=[], joint_list=[]):
    guide_list = [guide for guide in guide_list if "master" not in guide]
    guide_list.reverse()
    if len(joint_list) != len(guide_list):
        cmds.warning(f"update_guides.update_guide_position: error jointlist length is not equal to guide_list ignoring updating {guide_list}")
        return

    for joint, locator in zip(joint_list, guide_list):
        joint_world_matrix = cmds.xform(joint, query=True, matrix=True, worldSpace=True)
        locator_world_matrix = cmds.xform(locator, query=True, matrix=True, worldSpace=True)

        if not matrix_equal(joint_world_matrix, locator_world_matrix):
            cmds.xform(locator, matrix=joint_world_matrix, worldSpace=True)


def matrix_equal(matrix1, matrix2, tolerance=1e-6):
    return all(abs(a - b) <= tolerance for a, b in zip (matrix1, matrix2))

def loop_update_guide_position(systems_to_be_made={}):
    for key in systems_to_be_made.values():
        update_guide_position(guide_list=key['guide_list'], joint_list=key['joints'])


