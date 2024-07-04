system = ["spine_1","spine_2","spine_3","spine_4","kneck_1"]
system_pos = {"spine_1": [0,150,0],"spine_2": [0, 165, 3.771372431203975],"spine_3": [0, 185, 6.626589870023061],"spine_4": [0, 204, 5.4509520093959845],"kneck_1": [0.0, 231.0, 0.0150903206755304]}
system_rot = {"spine_1": [13.832579598094327, 0, 0],"spine_2":[8.04621385323777, 0, 0],"spine_3":[-3.330793760291316, 0, 0],"spine_4":[-11.225661138926666, 0, 0],"kneck_1":[0,0,0]}
ik_joints = {
    "start_joint": "spine_1",
    "end_joint": "spine_4",
    "pv_joint": None,
    "world_orientation": True
}
side = "None"
space_swapping = []
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]