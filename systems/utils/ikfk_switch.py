import maya.cmds as cmds

collected_ctrls = []
collected_joints = []

def collect_ctrls(imported_ctrls):
    for x in imported_ctrls:
        if x not in collected_ctrls: 
            collected_ctrls.append(x)
        else:
            pass

def collect_joints(imported_joints):
    for x in imported_joints:
        if x not in collected_joints: 
            collected_joints.append(x)
        else:
            pass

def create_ikfk():
    print("collected ctrls")
    print(collected_ctrls)
    print(collected_joints)
    for x in collected_ctrls:
        cmds.addAttr(x,ln=f"{x}_dvdr",nn="------------",at="enum",en="IKFK Switch",k=1) # dvdr
        cmds.setAttr(f"{x}.{x}_dvdr",l=True)
    
    attr_name = f"{collected_ctrls[-1][8:]}_switch"
    display_name = f"IKFK {collected_ctrls[-1][8:]}"
    proxy_attr = collected_ctrls[-1]
    cmds.addAttr(proxy_attr,ln=attr_name,nn=display_name,at="float",min=0,max=1,k=1) # eventually change name to a system name from ui

    collected_ctrls.remove(proxy_attr)
    cmds.addAttr(collected_ctrls,ln=attr_name,nn=display_name, proxy=f"{proxy_attr}.{attr_name}")
    
    # create one time nodes
    reverse_node = cmds.createNode('reverse', n=f"{proxy_attr}_IKFK_Reverse")
    cmds.connectAttr(f"{proxy_attr}.{attr_name}",f"{reverse_node}.inputX")

    collected_ctrls.append(proxy_attr) # adds proxy attr to the list again for connections
    
    # create ctrl crv connections
    for ctrl in collected_ctrls:
        if "ctrl_ik" in ctrl or "ctrl_pv" in ctrl:
            cmds.connectAttr(f"{reverse_node}.outputX",f"{ctrl}.visibility")
        elif "ctrl_fk" in ctrl:
            cmds.connectAttr(f"{proxy_attr}.{attr_name}",f"{ctrl}.visibility")
        else:
            cmds.warning(f"{ctrl} does not meet connection requirement therefore wont be connected to either {reverse_node} or visibility attr")

    # create rig joint connections
    for joint in collected_joints:
        rig_jnt_pconst = cmds.listRelatives(f"jnt_rig_{joint[7:]}",c=1,type="parentConstraint")
        if "jnt_ik" in joint:
            cmds.connectAttr(f"{reverse_node}.outputX",f"{rig_jnt_pconst[0]}.{joint}W0")
        elif "jnt_fk" in joint:
            cmds.connectAttr(f"{proxy_attr}.{attr_name}",f"{rig_jnt_pconst[0]}.{joint}W1")
        else:
            cmds.warning(f"{joint} does not meet connection requirement therefore wont be connected to either {reverse_node} or constraint weights")