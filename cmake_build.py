"""
A generic, clean way to build C/C++/Fortran code with CMake.
"""

import shutil
import subprocess
import os
from pathlib import Path


BINDIR = "build"


def cmake_build(src_dir: Path):
    """
    attempt to build using CMake
    """

    # CMake needs absolute paths
    src_dir = Path(src_dir).expanduser().resolve(strict=True)

    cmake_exe = shutil.which("cmake")
    if not cmake_exe:
        raise FileNotFoundError("CMake not available")

    wopts = []
    if os.name == "nt" and not os.environ.get("CMAKE_GENERATOR"):
        wopts = ["-G", "MinGW Makefiles"]

    bin_dir = src_dir / BINDIR

    subprocess.check_call([cmake_exe, f"-S{src_dir}", f"-B{bin_dir}"] + wopts)

    subprocess.check_call([cmake_exe, "--build", str(bin_dir), "--parallel"])
