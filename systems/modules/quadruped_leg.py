system = ["hip","knee","hock","ankle","ball","toe"]
system_pos = {"hip": [15.500776368501974, 143.01952676981773, 0.0], "knee": [15.50077636850199, 84.40395851432912, 16.88831424642954], "hock": [15.500776368502, 55.891282567247885, -6.1467039283778355], "ankle": [15.500776368502013, 13.500824325128413, 3.231937805584531], "ball": [15.500776368502013, 0.09308141163140426, 8.797491818220422], "toe": [15.500776368502011, 0.19625368437834745, 21.599164032189798]}
system_rot = {"hip": [0.0, -16.072746263879946, -89.99999999999999], "knee": [0.0, 38.93429139885964, -89.99999999999999], "hock": [1.628733593116456e-15, -12.475395472092545, -89.99999999999999],"ankle": [0.0, -22.543337389891605, -89.99999999999999], "ball": [0.0, -90.4617527861189, -90.00000000000081], "toe": [179.99999999999963, -89.5382472138811, 90.0]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle",
    "pv_joint": "knee",
    "world_orientation": True,
    "ik_type": "quadruped",
    "hock": "hock"
}
side = "_l"
space_swapping = ["hip","root","COG","Custom"]
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
    "start": "hip",
    "end": "ankle"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}