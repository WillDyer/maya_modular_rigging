is_preset = False
hide = True
ignore_transforms = True
system = ["scapula","humerus","radius","metacarpal","palm","sesamoid","phalanges"]
system_pos = {'scapula': [6.582827748017153, 89.04037971492482, 40.22617299052012], 'humerus': [14.349449794036513, 61.40564330827515, 51.39592681974741], 'radius': [12.555323625680884, 45.1160950295387, 44.13620525472673], 'metacarpal': [10.218400465660622, 24.873030042016858, 45.057996224152696], 'palm': [10.21840046566058, 12.906793035789404, 45.62585168582525], 'sesamoid': [10.218400465660613, 3.529935803724049, 48.78739686008111], 'phalanges': [10.218400465660606, 0.11791451570499545, 55.40698109877959]}
system_rot = {'scapula': [0.0, -47.76110741692336, -90.00000000000004], 'humerus': [1.725378073728148e-15, 22.824421308770432, -90.00000000000003], 'radius': [0.0, -15.684413402240303, -90.00000000000003], 'metacarpal': [0.0, -15.684413402240303, -90.00000000000004], 'palm': [-1.769312332852551e-15, -25.99778747071054, -90.00000000000004], 'sesamoid': [-4.579998741307465e-13, -90.40133390813867, -90.0], 'phalanges': [180.0, 0.4013339081381424, 90.00000000000036]}
ik_joints = {
    "start_joint": "humerus",
    "end_joint": "palm",
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
    "ik_palm": "cube"
}
