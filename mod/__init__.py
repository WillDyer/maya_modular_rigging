from importlib import reload


from mod import interface
reload(interface)

interface.main()
print("init ran")
