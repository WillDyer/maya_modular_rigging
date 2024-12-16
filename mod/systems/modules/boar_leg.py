is_preset = False
hide = True
ignore_transforms = True
system = ["fema","tibia","metatarsus","ankle","ball","toe"]
system_pos = {'fema': [12.779369612604686, 68.10601030584479, -47.19791441367375], 'tibia': [12.779369612604695, 50.49183420667646, -32.32010618381751], 'metatarsus': [11.496816788285214, 24.536049116517376, -48.32604809833627], 'ankle': [11.496816788285221, 7.147566572324823, -43.37359650463195], 'ball': [11.496816788285205, 2.557468416185432, -39.20468666956762], 'toe': [11.496816788285203, 0.5620937269400428, -35.68201659440596]}
system_rot = {'fema': [0.0, -16.072746263879942, -89.99999999999999], 'tibia': [0.0, 38.93429139885964, -89.99999999999999], 'metatarsus': [1.628733593116456e-15, -12.475395472092545, -89.99999999999999], 'ankle': [-3.4436874821234824e-15, -22.54333738989163, -90.0], 'ball': [7.887775610029521e-13, -90.4617527861189, -90.0], 'toe': [179.9999999999992, -89.5382472138811, 90.00000000000158]}
ik_joints = {
    "start_joint": "fema",
    "end_joint": "ankle",
    "pv_joint": "tibia",
    "world_orientation": True,
    "ik_type": "quadruped",
    "hock": "metatarsus"
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
