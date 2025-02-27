<h1 align="center">Modular-Auto-Rigging aka MOD</h1>
<p align="center">
    <img src="https://img.shields.io/badge/Maya-37A5CC?style=for-the-badge&logo=autodeskmaya&logoColor=white">
    <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
    <img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=Qt&logoColor=white">
</p>
<div align="center">
    <img src="screenshots/MOD.png" alt="Project Screenshot" width="700"/>
</div>

### Running The Tool

> [!WARNING]
> - This tool was developed alongside a university degree and will likely not be production ready.
> - Tool is designed to be ran through maya.

```python
from importlib import reload
import maya_modular_rigging
reload(maya_modular_rigging)

maya_modular_rigging.start_interface()

```
### New Module Setup & Parameters

> [!IMPORTANT]
> New modules must be placed within their own .py file within [~/mod/modules](https://github.com/WillDyer/maya_modular_rigging/tree/main/mod/modules)

| Parameter             | Required    | Type        | Default     | Description|
|-----------------------|-------------|-------------|-------------|------------|
| `is_preset`           | True        | boolean     | False       | Adds module to preset pool and hides it to the UI |
| `hide`                | True        | boolean     | False       | Hide a module to the UI |
| `ignore_transforms`   | True        | boolean     | True        | Ignores matching a new module to that of whats just been created |
| `system`              | True        | list        | none        | List of guide names, has to be in order |
| `system_pos`          | True        | dictionary  | none        | Dictionary that includes the name as the key and a value that is a list with the XYZ world space location |
| `system_pos`          | True        | dictionary  | none        | Dictionary that includes the name as the key and a value that is a list with the XYZ world space rotation |
| `ik_joints`           | False       | dictionary  | none        | Dictionary that includes `'start_joint', 'end_joint', 'pv_joint', 'hock', world_orientation'(bool), 'ik_type'` as keys  and the values include the name of the guide that describes each item |
| `side`                | True        | string      | 'L'         | Side of rig options are the following: `'L'`, `'R'`, `'C'`. Others can be tried but will return unexpected outcomes |
| `space_swapping`      | False       | list        | 'root', 'cog', 'Custom' | list of items that are available space swapping locations |
| `guide_scale`         | True        | float       | 1           | scale of the guide for display purposes |
| `available_rig_types` | True        | list        | 'FK'        | Systems that are available to create on the module |
| `reverse_foot`        | False       | boolean     | False       | Boolean option to create reverse foot system on a module |
| `rev_locators`        | False       | dictionary  | none        | Dictionary that includes `'foot_ctrl', 'ankle', 'ball', 'toe', 'heel', 'bank_in', 'bank_out'`, first 4 items must be guides from the system |
| `twist_joints`        | False       | dictionary  | none        | Dictionary that includes `'start'` & `'end'` which values are a string with the name of the guide |
| `default_ctrl_shape`  | False       | dictionary  | none        | includes the key as 'rigtype_guidename' example ik_ankle, available shapes are `'cube', 'circle', 'locator'` |
| `module_to_be_made`   | False       | dictionary  | none        | includes the key as the module name and value as guide to connect to. naming needs to be exact |
| `locked_guide_attr`   | False       | list        | none        | A list of attributes to lock on guide creation, typically used for central guides locking attrs to stop guides being off centre |

