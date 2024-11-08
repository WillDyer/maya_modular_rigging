is_preset = False
hide = True
ignore_transforms = True
system = ["fema","tibia","metatarsus","ankle","ball","toe"]
system_pos = {'fema': [12.779369612604684, 68.10601030584479, -47.19791441367375], 'tibia': [12.779369612604691, 50.49183420667646, -32.32010618381751], 'metatarsus': [11.496816788285205, 24.536049116517347, -53.54217964345622], 'ankle': [11.496816788285217, 6.825697839004423, -48.45612034024922], 'ball': [11.496816788285212, 3.5914158623963823, -40.35042168107209], 'toe': [11.496816788285209, 1.6114235180605088, -34.91910180911039]}
system_rot = {'fema': [0.0, -16.072746263879942, -89.99999999999999], 'tibia': [0.0, 38.93429139885964, -89.99999999999999], 'metatarsus': [8.14366796558228e-16, -12.475395472092554, -90.0], 'ankle': [0.0, -22.543337389891626, -90.0], 'ball': [-3.81666561775622e-13, -90.4617527861189, -90.0], 'toe': [179.99999999999963, -89.53824721388109, 90.00000000000158]}
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
    "end": "ankle"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}
