is_preset = False
hide = True
ignore_transforms = True
system = ["fema","tibia","metatarsus","ankle","ball","toe"]
system_pos = {'fema': [12.779369612604688, 68.10601030584479, -47.19791441367375], 'tibia': [12.779369612604699, 50.49183420667646, -32.32010618381751], 'metatarsus': [11.496816788285223, 24.53604911651739, -48.326048098336265], 'ankle': [11.49681678828523, 7.147566572324841, -43.373596504631934], 'ball': [11.496816788285216, 2.5574684161854524, -39.20468666956761], 'toe': [11.49681678828522, 0.07440080420957473, -32.87495124063747]}
system_rot = {'fema': [0.0, -16.072746263879942, -89.99999999999999], 'tibia': [0.0, 38.93429139885964, -89.99999999999999], 'metatarsus': [8.14366796558228e-16, -12.475395472092554, -90.0], 'ankle': [1.7218437410617418e-15, -22.543337389891658, -89.99999999999999], 'ball': [0.0, -90.4617527861189, -90.0], 'toe': [179.99999999999963, -89.53824721388109, 90.0]}
ik_joints = {
    "start_joint": "fema",
    "end_joint": "ankle",
    "pv_joint": "tibia",
    "world_orientation": True,
    "ik_type": "quadruped",
    "hock": "metatarsus"
}
side = "L"
space_swapping = ["fema","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = True
rev_locators = {  # items foot_ctrl, ankle, ball, toe must be the same
    "foot_ctrl": system[3],
    "ankle": system[3],
    "ball": system[4],
    "toe": system[5],
    "heel": "heel",
    "bank_in": "bank_in",
    "bank_out": "bank_out",
}
twist_joint = {
    "start": "fema",
    "end": "metatarsus"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}
