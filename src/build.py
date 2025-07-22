"""
Creative Commons Attribution 4.0 International Public License.
See License.txt in the root directory.
"""
__author__ = "Rodrigo Parrilla Mesas"

import PyInstaller.__main__
from pathlib import Path
import shutil
import os

if __name__ == "__main__":
    # make all paths relative to the project path instead of the current working directory
    src_path = Path(__file__).resolve().parent
    root_path = src_path.parent
    output_path = root_path / "output"
    icon_path = root_path / "assets/icon.ico"
    logo_path = root_path / "assets/logo.png"
    documentation_path = root_path / "doc/Speckle_Pattern_Generator_Documentation.pdf"
    dist_path = root_path / "output/dist"
    work_path = root_path / "output/build"
    #relative to project file structure
    mySpeckle_Patterns_path = dist_path / "Speckle Pattern Generator/_internal/mySpeckle_Patterns"
    mySpeckle_Parameters_path = dist_path / "Speckle Pattern Generator/_internal/mySpeckle_Parameters"

    # clean the output directory before building
    if output_path.exists() and any(output_path.iterdir()):
        for item in output_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    PyInstaller.__main__.run([
        "main.py",
        "--onedir",
        "--windowed",
        "--clean",
        "--name=Speckle Pattern Generator",
        f"--icon={icon_path}",
        f"--distpath={dist_path}",
        f"--workpath={work_path}",
        f"--specpath={work_path}",
        f"--add-data={logo_path}:assets",
        f"--add-data={documentation_path}:doc"
    ])
