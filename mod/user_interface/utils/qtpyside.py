import sys
import importlib


def get_version():
    pyside_versions = ["PySide6", "PySide2"]

    for version in pyside_versions:
        # print("Trying pyside version:", version)
        try:
            sys.modules["PySide"] = importlib.import_module(version)
            sys.modules["PySide.QtCore"] = importlib.import_module(f"{version}.QtCore")
            sys.modules["PySide.QtWidgets"] = importlib.import_module(f"{version}.QtWidgets")
            sys.modules["PySide.QtGui"] = importlib.import_module(f"{version}.QtGui")
            shiboken = importlib.import_module(f"shiboken{version[-1]}")
            wrapInstance = shiboken.wrapInstance

            # print("Successful import of", version)
            break
        except ModuleNotFoundError:
            continue
    else:
        raise ModuleNotFoundError("No PySide module found.")
    
    return (sys.modules["PySide"], wrapInstance)
