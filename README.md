# VerifyImagePlugin

FreeCAD plugin for visual verification using silhouette comparison between the current CAD view and a user-provided photo.

## Setup

1. Create and activate a Python 3.11 virtual environment (optional for development):

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
pip install -r requirements.txt
```

Note: Inside FreeCAD, PySide2 is provided by FreeCAD. You do not need to install PySide2 via pip for runtime inside FreeCAD. For local linting outside FreeCAD, you can skip UI usage.

## Installation (FreeCAD)

- Copy or symlink the `VerifyImagePlugin` folder into your FreeCAD `Mod` directory, e.g. on macOS:
  `~/Library/Preferences/FreeCAD/Mod/VerifyImagePlugin`
- Launch FreeCAD, switch to the "Verify Image" workbench. Use the toolbar button "Verify with Image".

## Usage

1. Align your 3D model view to match your photo perspective.
2. Click "Upload Photo…" and select your image.
3. Click "Run Verification" to compute shape similarity and view the overlay.

## Development

- Core logic is in `VerifyImagePlugin/ImageProcessor.py`.
- UI is in `VerifyImagePlugin/VerifyImageTaskPanel.py`.
- Workbench setup is in `VerifyImagePlugin/InitGui.py` and command in `VerifyImagePlugin/VerifyImageCommand.py`.

## Limitations

- CAD silhouette capture assumes a white background and uses the largest contour as the model outline.
- For complex scenes or non-white backgrounds, tweak thresholding in `ImageProcessor.generate_cad_silhouette`.
