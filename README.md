<h1 align="center">WD-Modular-Auto-Rigging</h1>
<p align="center"}>
  <img src="https://img.shields.io/badge/Maya-37A5CC?style=for-the-badge&logo=autodeskmaya&logoColor=white">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
  <img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=Qt&logoColor=white">
</p>

A assortment of tools I've integrated into a modular auto limb/rigging tool to speed up my workflow
> Many of the tools are made for my own hardware, in this repository I've tried my best to make the code work on any machine however there might be some cases where you might have to edit the code slightly.
> This tool is also still in WIP and in some instances won't work due to me changing things, if you have any questions if you do use it feel free to reach out to me.

### Running The Tool
- All tools are designed to be either run through the Maya script editor or a shelf tool and can be ran with a similar code to the below.
- See each individual sub-folder for the specific run code.
- NOTE: As I have switched to linux recently you might need to check the pathing if you are running a windows based machine.

```python
from maya_modular_rigging import main

main.run_ui()
```
### New Module Setup & Parameters

#### Example Usage:
```python
system = ["joint_1","joint_2","joint_3"]
system_pos = {"joint_1": [X, Y, Z],"joint_2": [X, Y, Z],"joint_3": [X, Y, Z]}
system_rot = {"joint_1": [X, Y, Z],"joint_2": [X, Y, Z],"joint_3": [X, Y, Z]}
ik_joints = {
    "start_joint": "joint_1",
    "end_joint": "joint_2",
    "pv_joint": "joint_3",
    "world_orientation": False
}
side = "_l"
space_swapping = ["joint_1","root","COG","Custom"]
guide_scale = 1
available_rig_types = ["FK","IK","FKIK"]
reverse_foot = True
rev_locators = {
    "foot_ctrl": system[2],
    "ankle": system[2],
    "ball": system[3],
    "toe": system[4],
    "heel": "heel",
    "bank_in": "bank_in",
    "bank_out": "bank_out",
}
```