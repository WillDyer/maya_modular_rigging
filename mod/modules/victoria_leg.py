is_preset = False
hide = False
ignore_transforms = False
system =  ['hip', 'knee_1', 'knee_2', 'ankle_1', 'ankle_2', 'ankle_3', 'ball', 'toe']
system_pos = {'hip': [0.0, 15.300908262100057, 0.5127091543296566], 'knee_1': [1.7831006257476993e-15, 11.622802154791211, 5.3876135931138736], 'knee_2': [1.435987377904067e-15, 5.116554941243854, 6.583692753303456], 'ankle_1': [1.7919367300163013e-15, 2.294146246596364, 6.356555546958469], 'ankle_2': [2.5484182616088586e-15, 1.710970194401583, 6.309623655218611], 'ankle_3': [2.4736334834054913e-15, 1.1617660384674613, 6.3041310081648225], 'ball': [3.5634839527148555e-15, 0.3843867112696093, 7.681010334195838], 'toe': [3.77104155012466e-15, 0.3892159988413349, 9.573162433692316]}
system_rot = {'hip': [89.99999999999999, -52.96551621141161, -89.99999999999999], 'knee_1': [90.0, -10.416691330672267, -90.0], 'knee_2': [90.0, 4.60104064959551, -90.0], 'ankle_1': [90.0, 4.601040649595505, -90.0], 'ankle_2': [90.0, 0.5730018596363975, -90.0], 'ankle_3': [90.0, -60.55113994253277, -90.0], 'ball': [90.00000000000499, -90.14623411890564, -90.00000000000499], 'toe': [-90.0, -89.85376588109436, 90.0]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle_1",
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
    "foot_ctrl": system[5],
    "ankle": system[5],
    "ball": system[6],
    "toe": system[7],
    "heel": "heel",
    "bank_in": "bank_in",
    "bank_out": "bank_out",
}
twist_joint = {
    "start": "hip",
    "end": "ankle"
}
default_ctrl_shape = {
    "ik_ankle_3": "cube"
}
