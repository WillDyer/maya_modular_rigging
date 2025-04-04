is_preset = False
hide = False
ignore_transforms = False
system = ['shoulder', 'elbow', 'wrist', 'end']
system_pos = {'shoulder': [4.788953278278173, 56.616605064853154, 20.367719286554465], 'elbow': [4.788953278278158, 55.93719483355755, 37.04625055407362], 'wrist': [4.78895327827815, 55.29731997937774, 52.75424591702951], 'end': [4.7889532782781465, 47.84988858111693, 64.65170275705765]}
system_rot = {'shoulder': [90.00000000000063, -87.66731088509282, -90.00000000000063], 'elbow': [90.00000000000063, -87.66731088509282, -90.00000000000063], 'wrist': [90.00000000000006, -57.95473682211436, -90.00000000000006], 'end': [90.00000000000006, -57.95473682211435, -90.00000000000006]}
ik_joints = {
    "start_joint": "shoulder",
    "end_joint": "wrist",
    "pv_joint": "elbow",
    "world_orientation": True,
    "ik_type": "biped",
    "offset_ctrl": False
}
twist_joint = {
    "start": "shoulder",
    "end": "wrist"
}
side = "L"
space_swapping = ["shoulder","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
default_ctrl_shape = {
    "fk_wrist": "circle",
    "ik_wrist": "cube"
}

