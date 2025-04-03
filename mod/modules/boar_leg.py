is_preset = False
hide = True
ignore_transforms = True
system = ['fema', 'tibia', 'metatarsus', 'ankle', 'ball', 'toe']
system_pos = {'fema': [12.77936936732651, 68.10671135283118, -47.20026921219629], 'tibia': [12.781289741157357, 50.53389844657784, -32.27363535439399], 'metatarsus': [11.496816997684434, 24.6071634262695, -48.326047914149456], 'ankle': [11.49681678828541, 7.218673780129738, -43.37359650463187], 'ball': [11.496816788285232, -2.6645352591003757e-15, -41.5462897928388], 'toe': [11.496816788285233, -3.135722098253522e-28, -32.40136843565136]}
system_rot = {'fema': [-0.007142737268360664, -40.34508681328702, -89.99361548213429], 'tibia': [0.25729758897756644, 31.731875695951764, -92.83621755288623], 'metatarsus': [0.6836965449382056, -15.89758889219755, -90.00000092379727], 'ankle': [90.00000000000574, -14.20523223769559, -90.00000000000149], 'ball': [9.541664044718084e-15, -6.904984213457295e-12, -5.4355679506211505e-12], 'toe': [0.0, 0.0, 0.0]}
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
