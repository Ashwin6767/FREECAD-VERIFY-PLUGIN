# FreeCAD command for VerifyImagePlugin

try:
    import FreeCAD
    import FreeCADGui
except Exception:
    class _Dummy:
        def __getattr__(self, name):
            raise RuntimeError("FreeCAD API is only available inside FreeCAD GUI runtime.")
    FreeCAD = _Dummy()
    FreeCADGui = _Dummy()

class VerifyImageCommand:
    def GetResources(self):
        return {
            'MenuText': 'Verify with Image',
            'ToolTip': 'Compare CAD silhouette with a photo',
            'Pixmap': ''  # Provide an icon path here if available
        }

    def IsActive(self):
        try:
            return FreeCADGui.ActiveDocument is not None
        except Exception:
            return False

    def Activated(self):
        try:
            from .VerifyImageTaskPanel import VerifyImageTaskPanel
        except Exception:
            from VerifyImageTaskPanel import VerifyImageTaskPanel  # type: ignore

        panel = VerifyImageTaskPanel()
        FreeCADGui.Control.showDialog(panel)
