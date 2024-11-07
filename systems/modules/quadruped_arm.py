is_preset = False
system = ["scapula","humerus","radius","metacarpal","wrist","sesamoid","phalanges"]
system_pos = {"scapula": [15.500776368501974, 143.01952676981767, 2.0821671481145895e-15], "humerus": [15.500776368501963, 122.43949667875015, 22.665673258507947], "radius": [15.500776368501947, 84.1934173724987, 6.569316183292344],"metacarpal": [14.57334105143621, 48.71612091714072, 16.54076593974449], "wrist": [13.678232000396925, 14.47540506424123, 26.164655352563003], "sesamoid": [13.485869282167808, 0.15899920406086387, 33.14315209300567], "phalanges": [14.251775388457839, 0.22143834463552853, 45.54044757105048]}
system_rot = {"scapula": [0.0, -47.76110741692336, -90.00000000000004], "humerus": [-5.176134221184442e-15, 22.824421308770393, -90.00000000000006], "radius": [-3.65590755926804, -15.693752463833576, -91.49746556491168],"metacarpal": [-3.655907559268042, -15.693752463833539, -91.49746556491165], "wrist": [-3.9158196988253517, -25.98476785187488, -90.76980974072035], "sesamoid": [82.8653035146257, -93.54694392305827, -175.3393695929728], "phalanges": [-97.13469648537368, -86.45305607694172, 4.660630407027287]}
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
