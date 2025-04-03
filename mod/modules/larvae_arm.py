is_preset = False
hide = False
ignore_transforms = False
system = ["shoulder","elbow","wrist"]
system_pos = {"shoulder": [23.92248806756285, 206.90953576827695, 8.978246464134521],"elbow": [48.84015296973088, 182.47726987882783, 11.656745919151222],"wrist": [73.83312760286583, 159.98878425187124, 21.383987727271354]}
system_rot = {"shoulder": [-11.425952708067294, -4.389054564090439, -44.43646490372016],"elbow": [-11.865857864384843, -16.13617420369717, -41.980636410933435],"wrist": [-11.865857864384836, -16.13617420369717, -41.980636410933435]}
ik_joints = {
    "start_joint": "shoulder",
    "end_joint": "wrist",
    "pv_joint": "elbow",
    "world_orientation": False,
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

