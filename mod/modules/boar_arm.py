is_preset = False
hide = True
ignore_transforms = True
system = ['scapula', 'humerus', 'radius', 'metacarpal', 'palm', 'sesamoid', 'phalanges']
system_pos = {'scapula': [6.582827748017133, 89.03941996033022, 40.22549223998315], 'humerus': [14.34945122530466, 61.405929201019305, 51.398287793968215], 'radius': [12.560282582311736, 45.067564745985734, 44.24440966762264], 'metacarpal': [10.21799984778755, 24.820481573287353, 45.057996249108], 'palm': [10.219332611861743, 12.854338464431896, 45.62782537848872], 'sesamoid': [10.21800041198725, 6.110667527536862e-13, 48.76147460937644], 'phalanges': [10.218000411987234, 1.4799960884784076e-12, 56.69719696045066]}
system_rot = {'scapula': [-22.748823513076733, -21.26793403334725, -74.30154918965499], 'humerus': [0.24942428639408393, 23.513790930258704, -96.24897214903197], 'radius': [0.1836510329855398, -2.2858442368291523, -96.59892569522631], 'metacarpal': [-0.11559105666999708, -2.7263720831278944, -89.99361851554619], 'palm': [90.02507134440926, -13.700417656062644, -90.0059380286441], 'sesamoid': [3.2721293048797717e-14, -89.99999999999375, 0.0], 'phalanges': [0.0, 0.0, 0.0]}
ik_joints = {
    "start_joint": "humerus",
    "end_joint": "palm",
    "pv_joint": "radius",
    "world_orientation": True,
    "ball_joint": "sesamoid",
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
