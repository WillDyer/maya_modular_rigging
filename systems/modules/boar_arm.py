is_preset = False
hide = True
ignore_transforms = True
system = ["scapula","humerus","radius","metacarpal","wrist","sesamoid","phalanges"]
system_pos = {'scapula': [6.582827748017155, 89.04037971492482, 40.22617299052012], 'humerus': [14.349449794036516, 61.40564330827517, 51.3959268197474], 'radius': [12.555323625680863, 45.116095029538705, 44.136205254726725], 'metacarpal': [10.218400465660595, 25.096701926518957, 46.24336736744995], 'wrist': [10.218400465660551, 12.972899494078398, 46.888065090518026], 'sesamoid': [10.218400465660578, 3.5960422620130466, 50.04961026477388], 'phalanges': [10.218400465660565, 1.234625803118139, 53.12827229512154]}
system_rot = {'scapula': [0.0, -47.76110741692336, -90.00000000000004], 'humerus': [-5.176134221184443e-15, 22.824421308770404, -90.00000000000006], 'radius': [1.6517808656594674e-15, -15.684413402240311, -90.00000000000003], 'metacarpal': [0.0, -15.684413402240315, -90.00000000000004], 'wrist': [0.0, -25.99778747071055, -90.00000000000004], 'sesamoid': [-4.579998741307465e-13, -90.40133390813867, -90.0], 'phalanges': [180.0, 0.40133390813866415, 90.00000000000036]}
ik_joints = {
    "start_joint": "humerus",
    "end_joint": "wrist",
    "pv_joint": "radius",
    "world_orientation": True,
    "ik_type": "quadruped",
    "hock": "metacarpal"
}
side = "L"
space_swapping = ["scapula","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = False
rev_locators = {  # items foot_ctrl, ankle, ball, toe must be the same
    "foot_ctrl": system[4],
    "ankle": system[4],
    "ball": system[5],
    "toe": system[6],
    "heel": "heel",
    "bank_in": "bank_in",
    "bank_out": "bank_out",
}
twist_joint = {
    "start": "humerus",
    "end": "wrist"
}
default_ctrl_shape = {
    "ik_wrist": "cube"
}
