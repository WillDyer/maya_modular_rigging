is_preset = False
hide = True
ignore_transforms = True
system = ["scapula","humerus","radius","metacarpal","wrist","sesamoid","phalanges"]
system_pos = {'scapula': [6.582827748017154, 89.04037971492482, 40.22617299052012], 'humerus': [14.349449794036515, 61.40564330827516, 51.3959268197474], 'radius': [12.555323625680874, 45.116095029538705, 44.136205254726725], 'metacarpal': [10.21840046566061, 24.873030042016868, 45.05799622415269], 'wrist': [10.218400465660565, 12.906793035789416, 45.62585168582524], 'sesamoid': [10.218400465660595, 3.5299358037240616, 48.787396860081095], 'phalanges': [10.218400465660585, 1.096311801579561, 51.47397416717617]}
system_rot = {'scapula': [0.0, -47.76110741692336, -90.00000000000004], 'humerus': [0.0, 22.824421308770418, -90.00000000000006], 'radius': [0.0, -15.684413402240311, -90.00000000000003], 'metacarpal': [0.0, -15.68441340224031, -90.00000000000004], 'wrist': [0.0, -25.99778747071054, -90.00000000000004], 'sesamoid': [-4.579998741307465e-13, -90.40133390813867, -90.0], 'phalanges': [180.0, 0.40133390813830433, 90.00000000000036]}
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
    "end": "metacarpal"
}
default_ctrl_shape = {
    "ik_wrist": "cube"
}
