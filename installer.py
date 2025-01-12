from importlib import reload


def onMayaDroppedPythonFile(*args):
    import installer_tmp
    reload(installer_tmp)
    print("running installer tmp")
    installer_tmp.start_install_ui()



