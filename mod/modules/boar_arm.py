is_preset = False
hide = True
ignore_transforms = True
system = ['scapula', 'humerus', 'radius', 'metacarpal', 'palm', 'sesamoid', 'phalanges']
system_pos = {'scapula': [6.582827748017153, 89.04037971492482, 40.22617299052012], 'humerus': [14.349449794036516, 61.40564330827516, 51.39592681974741], 'radius': [12.555323625680884, 45.11609502953871, 44.13620525472674], 'metacarpal': [10.218400465660622, 24.873030042016875, 45.0579962241527], 'palm': [10.21840046566058, 12.906793035789413, 45.62585168582525], 'sesamoid': [10.218400465660615, 3.529935803724058, 48.7873968600811], 'phalanges': [10.218400465660611, 0.117914515704995, 55.40698109877959]}
system_rot = {'scapula': [-22.74699138409364, -21.261859048698096, -74.3022136668225], 'humerus': [0.24665805110441472, 23.892799605070998, -96.28520761883259], 'radius': [0.1896847959130179, -2.590049198444642, -96.58525427755106], 'metacarpal': [-0.11551839910725473, -2.716921888146137, -90.00000000000023], 'palm': [-0.11551839910734447, -18.632289795002922, -89.99999999999979], 'sesamoid': [-0.11551839910712532, -62.731454880945016, -90.00000000000009], 'phalanges': [-1.8065550590712775e-12, -90.401333908138, -89.99999999999817]}
ik_joints = {
    "start_joint": "humerus",
    "end_joint": "palm",
    "pv_joint": "radius",
    "world_orientation": True,
    "ik_type": "quadruped",
    "hock": "metacarpal",
    "offset_ctrl": True
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
