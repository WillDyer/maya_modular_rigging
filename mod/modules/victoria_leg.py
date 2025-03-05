is_preset = False
hide = False
ignore_transforms = False
system = ['hip', 'knee_1', 'knee_2', 'ankle', 'ball', 'toe']
system_pos = {'hip': [0.0, 15.300908262100057, 0.5127091543296566], 'knee_1': [1.7831006257476997e-15, 11.622802154791215, 5.387613593113872], 'knee_2': [1.1981881223452805e-15, 5.116554941243853, 6.583692753303456], 'ankle': [1.8194648835406626e-15, 2.2941462465963656, 6.356555546958471], 'ball': [1.7830213522372818e-15, 0.37495553569999474, 7.670601652921477], 'toe': [2.36279898315038e-15, 0.37981145032372804, 9.573186436661889]}
system_rot = {'hip': [90.0, -52.96551621141162, -90.0], 'knee_1': [90.0, -10.416691330672267, -90.0], 'knee_2': [89.99999999999999, 4.601040649595513, -89.99999999999999], 'ankle': [90.0, -34.39895935040449, -90.0], 'ball': [90.00000000000249, -90.14623411890568, -90.00000000000249], 'toe': [-90.0, -89.85376588109436, 90.0]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle",
    "pv_joint": "knee_1",
    "world_orientation": True,
    "ik_type": "biped",
    "offset_ctrl": True
}
side = "L"
space_swapping = ["hip","root","COG","Custom"]
guide_scale = 0.25
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
    "start": "hip",
    "end": "ankle"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}
