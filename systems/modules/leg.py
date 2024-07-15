system = ["hip","knee","ankle","ball","toe"]
system_pos = {"hip": [15.500776368501974, 143.01952676981773, 0.0], "knee": [15.500776368501974, 84.81057291070695, 16.48333754759564], "ankle": [15.500776368501972, 13.105669686730423, 3.2508317569701433], "ball": [15.500776368501969, 0.12302890199678806, 12.928208777109283], "toe": [15.50077636850197, 0.016002224253117384, 30.113464926919853]}
system_rot = {"hip": [0.0, -15.810811440715579, -90.0], "knee": [0.0, 10.455796273742568, -90.0], "ankle": [0.0, -36.70117682564226, -90.0], "ball": [0.0, -89.64317682564224, -90.0], "toe": [0.0, -89.64317682564226, -90.0]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle",
    "pv_joint": "knee",
    "world_orientation": True
}
side = "_l"
space_swapping = ["hip","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = True
rev_locators = { # items foot_ctrl, ankle, ball, toe must be the same
    "foot_ctrl": system[2],
    "ankle": system[2],
    "ball": system[3],
    "toe": system[4],
    "heel": "heel",
    "bank_in": "bank_in",
    "bank_out": "bank_out",
}