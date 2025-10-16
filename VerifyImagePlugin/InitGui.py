# FreeCAD Workbench initialization for VerifyImagePlugin
# This file defines and registers the workbench and its toolbar/command.

try:
    import FreeCAD
    import FreeCADGui
except Exception:
    # Allow importing outside FreeCAD for linting/tests
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("FreeCAD API is only available inside FreeCAD GUI runtime.")
    FreeCAD = _Dummy()
    FreeCADGui = _Dummy()

class VerifyImageWorkbench:
    def __init__(self):
        self.__class__.MenuText = "Verify Image"
        self.__class__.ToolTip = "Tools for visual verification against photos"
        self.__class__.Icon = ""

    def Initialize(self):
        try:
            from .VerifyImageCommand import VerifyImageCommand
        except Exception:
            # Fallback absolute import when loaded as a macro without package context
            from VerifyImageCommand import VerifyImageCommand  # type: ignore

        # Register command with FreeCAD
        FreeCADGui.addCommand("VerifyImageCommand", VerifyImageCommand())

        # Create toolbar and add the command using Workbench helper
        self.appendToolbar("Verification Tools", ["VerifyImageCommand"])

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"

# Register the workbench
try:
    FreeCADGui.addWorkbench(VerifyImageWorkbench())
except Exception:
    # Ignore when not in FreeCAD GUI context
    pass
