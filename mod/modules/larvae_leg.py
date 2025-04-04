is_preset = False
hide = False
ignore_transforms = False
system = ['hip', 'knee', 'ankle', 'toe']
system_pos = {'hip': [23.631793975830078, 32.57544708251953, 16.327001571655273], 'knee': [31.178215890338514, 19.77206654232421, 17.542463504720946], 'ankle': [32.88480141432433, 10.223110723801215, 17.15015938043977], 'toe': [34.99205997315062, 0.4757648915508259, 16.334425384639076]}
system_rot = {'hip': [3.988967130749292e-16, -4.675469148609374, -59.48453910196208], 'knee': [1.637995892130124, 2.315931138606995, -79.86710154104283], 'ankle': [1.7219375077004417, 4.676276371376927, -77.80107935372185], 'toe': [1.7219375077004404, 4.676276371376927, -77.80107935372183]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle",
    "pv_joint": "knee",
    "world_orientation": True,
    "ik_type": "biped",
    "offset_ctrl": True
}
side = "L"
space_swapping = ["hip","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = False
default_ctrl_shape = {
    "ik_ankle": "cube"
}

