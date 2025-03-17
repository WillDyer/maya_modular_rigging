is_preset = False
hide = False
ignore_transforms = False
system = ['hip', 'knee_1', 'knee_2', 'knee_3', 'ankle', 'ball', 'toe']
system_pos = {'hip': [0.9435646735872749, 15.619765596824175, 0.6180458353728713], 'knee_1': [2.892302407195335, 11.634599248013483, 4.78983984493618], 'knee_2': [3.3586923008120735, 5.1433240694305855, 5.788272076608935], 'knee_3': [3.268808739444083, 2.3255178447460674, 5.59585228793942], 'ankle': [3.289541636309848, 0.9752702824667099, 5.6402365955113565], 'ball': [3.641518325872149, 0.4199776753811745, 6.393736781656598], 'toe': [4.644841132792635, 0.4136931063793563, 8.541617434544374]}
system_rot = {'hip': [54.481069627027466, -43.24117529210966, -63.94146670312235], 'knee_1': [64.64813927291756, -8.722081281699829, -85.89043268313812], 'knee_2': [64.89939387980488, 3.9045176602008684, -91.82702523259356], 'knee_3': [64.94722300649973, -1.882483495088731, -89.12029899165779], 'ankle': [49.92884346169274, -48.89449135561878, -57.631104263985954], 'ball': [0.32515571674541194, -64.96124512409406, -0.3588820749383459], 'toe': [0.3251557167454157, -64.96124512409405, -0.3588820749383654]}
ik_joints = {
    "start_joint": "hip",
    "end_joint": "ankle",
    "pv_joint": "knee_1",
    "world_orientation": True,
    "ball_joint": "ball",
    "ik_type": "biped",
    "offset_ctrl": True
}
side = "L"
space_swapping = ["hip","root","COG","Custom"]
guide_scale = 0.25
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = True
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
    "start": "hip",
    "end": "ankle"
}
default_ctrl_shape = {
    "ik_ankle": "cube"
}
