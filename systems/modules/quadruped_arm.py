is_preset = False
hide = False
ignore_transforms = False
system = ["scapula","humerus","radius","metacarpal","wrist","sesamoid","phalanges"]
system_pos = {'scapula': [-1.7763568394002505e-15, 150.0, 39.33961054684299], 'humerus': [-1.5372091120976232e-14, 129.41996990893247, 62.005283805350935], 'radius': [-2.557817642746297e-15, 91.17389060268104, 45.90892673013532], 'metacarpal': [2.6788303897714094e-14, 55.68284902100622, 55.87459167242473], 'wrist': [-5.151257196699762e-14, 21.428867135697253, 65.4928979039471], 'sesamoid': [-6.36014637313112e-14, 7.112755120640827, 72.4746479494226], 'phalanges': [-6.485679598815218e-14, 7.199759143858946, 84.89543199391119]}
system_rot = {'scapula': [0.0, -47.76110741692336, -90.00000000000004], 'humerus': [-5.176134221184443e-15, 22.824421308770404, -90.00000000000006], 'radius': [1.6517808656594674e-15, -15.684413402240327, -90.00000000000003], 'metacarpal': [1.6517808656594668e-15, -15.684413402240326, -90.00000000000003], 'wrist': [1.7693123328525505e-15, -25.997787470710556, -90.00000000000004], 'sesamoid': [4.579998741307465e-13, -90.40133390813867, -90.0], 'phalanges': [180.0, -89.59866609186132, 90.00000000000182]}
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
