is_preset = False
hide = True
ignore_transforms = True
system = ['fema', 'tibia', 'metatarsus', 'ankle', 'ball', 'toe']
system_pos = {'fema': [12.779369612604688, 68.10601030584479, -47.19791441367375], 'tibia': [12.779369612604704, 50.491834206676465, -32.320106183817515], 'metatarsus': [11.496816788285232, 24.536049116517404, -48.32604809833627], 'ankle': [11.49681678828524, 7.147566572324859, -43.373596504631905], 'ball': [11.496816788285232, 2.557468416185479, -39.204686669567586], 'toe': [11.49681678828523, 0.07440080420959916, -32.87495124063746]}
system_rot = {'fema': [0.0, -40.18609756884119, -90.0000000000001], 'tibia': [0.26060680715703727, 31.629346411784926, -92.82885465067827], 'metatarsus': [0.6836962758183982, -15.897598485457259, -90.0], 'ankle': [0.7629562325126982, -42.24697835168312, -90.00000000000013], 'ball': [0.8512864104999321, -68.58060999651676, -89.99999999999997], 'toe': [-33.97319789042459, -90.55632338553784, -55.2355559640229]}
ik_joints = {
    "start_joint": "fema",
    "end_joint": "ankle",
    "pv_joint": "tibia",
    "world_orientation": True,
    "ball_joint": "ball",
    "ik_type": "quadruped",
    "hock": "metatarsus",
    "offset_ctrl": True
}
side = "L"
space_swapping = ["fema","root","COG","Custom"]
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
    "start": "fema",
    "end": "metatarsus"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}
