import pytest
import maya.cmds as cmds
from importlib import reload

import mod
reload(mod)

import maya.standalone
maya.standalone.initialize(name="python")

def test_idk():
    cmds.file(new=True, force=True)


def pytest_sessionfinish(session, exitstatus):
    maya.standalone.uninitialize()
