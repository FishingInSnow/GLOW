#!/usr/bin/env python3

"""
Run glowbasic executable and collect output date into xarray.Dataset

Assumes you have first built glowbasic:

    cmake -B build

    cmake --build build

code based on https://github.com/space-physics/NCAR-GLOW
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import shutil
import argparse
import io
import sys
import functools
from dateutil import parser

import numpy as np
import xarray
import pandas
from matplotlib.pyplot import figure, show

import geomagindices as gi

import cmake_build

BINPATH = "build"

if sys.version_info < (3, 9):
    raise RuntimeError("Python >= 3.9 required")


@functools.cache
def get_exe(name: str = "glowbasic") -> Path:
    src_dir = Path(__file__).resolve().parent

    bin_dir = src_dir / BINPATH
    if not (exe := shutil.which(name, path=bin_dir)):
        cmake_build.cmake_build(src_dir)

    if not (exe := shutil.which(name, path=bin_dir)):
        raise RuntimeError("GLOW executable not available.")

    return Path(exe)


def maxwellian(
    time: datetime, glat: float, glon: float, Q: float, Echar: float
) -> xarray.Dataset:
    """
    Maxwellian energy distribution

    runs Glow executable and returns xarray.Dataset

    Note that Glow uses stdin and stdout for input and output, respectively.
    Glow will hang if you do not provide the correct input.
    """

    idate, utsec = glowdate(time)

    ip = gi.get_indices([time - timedelta(days=1), time], 81)

    # date, UT, lat, lon, F107a, F107, F107p, Ap, Ef, Ec
    # format data and pipe to stdin
    dat = subprocess.check_output(
        [str(get_exe())],
        timeout=5,
        input=f"{idate} {utsec} {glat} {glon} {ip['f107s'].iloc[1]} "
        f"{ip['f107'].iloc[1]} {ip['f107'].iloc[0]} {ip['Ap'].iloc[1]} "
        f"{Q} {Echar}",
        stderr=subprocess.DEVNULL,
        text=True,
    )

    return glowread(dat, time, ip, glat, glon)


def glowread(
    raw: str, time: datetime, ip: pandas.DataFrame, glat: float, glon: float
) -> xarray.Dataset:
    """
    set attributes and parse glow output

    based on https://github.com/space-physics/NCAR-GLOW
    """

    iono = glowparse(raw)
    iono.attrs["geomag_params"] = ip
    iono.attrs["time"] = time.isoformat()
    iono.attrs["glatlon"] = (glat, glon)

    return iono


def glowparse(raw: str) -> xarray.Dataset:
    """
    parse glow text output

    code based on https://github.com/space-physics/NCAR-GLOW
    """

    glow_var = [
        "Tn",
        "O",
        "N2",
        "NO",
        "NeIn",
        "NeOut",
        "ionrate",
        "O+",
        "O2+",
        "NO+",
        "N2D",
        "pedersen",
        "hall",
    ]

    table = io.StringIO(raw)

    header = np.genfromtxt(table, max_rows=1, skip_header=1)
    # idate,ut,glat,glong,f107a,f107,f107p,ap,ef,ec
    assert header.size == 10

    Nalt = 102

    dat = np.genfromtxt(table, skip_header=1, max_rows=Nalt)
    alt_km = dat[:, 0]

    if len(glow_var) != dat.shape[1] - 1:
        raise ValueError("did not read raw output from GLOW correctly")

    d: dict = {k: ("alt_km", v) for (k, v) in zip(glow_var, dat[:, 1:].T)}
    iono = xarray.Dataset(d, coords={"alt_km": alt_km})

    assert len(glow_var) == len(iono.data_vars)
    # %% VER
    dat = np.genfromtxt(table, skip_header=1, max_rows=Nalt)
    assert dat[0, 0] == alt_km[0]
    wavelen = [
        3371,
        4278,
        5200,
        5577,
        6300,
        7320,
        10400,
        3644,
        7774,
        8446,
        3726,
        "LBH",
        1356,
        1493,
        1304,
    ]

    ver = xarray.DataArray(
        dat[:, 1:],
        coords={"alt_km": alt_km, "wavelength": wavelen},
        dims=["alt_km", "wavelength"],
        name="ver",
    )

    # %% assemble output
    iono = xarray.merge((iono, ver))

    return iono


def glowdate(t: datetime) -> tuple[str, str]:
    """
    parse glow integer date in form yyddd
    code based on https://github.com/space-physics/NCAR-GLOW
    """
    idate = f'{t.year}{t.strftime("%j")}'
    utsec = str(t.hour * 3600 + t.minute * 60 + t.second)

    return idate, utsec


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run GLOW model and parse output")
    p.add_argument("time", help="time in ISO format")
    p.add_argument("glat", type=float, help="geographic latitude")
    p.add_argument("glon", type=float, help="geographic longitude")
    p.add_argument("Q", type=float, help="energy flux")
    p.add_argument("Echar", type=float, help="characteristic energy")
    P = p.parse_args()

    time = parser.parse(P.time)

    iono = maxwellian(time, P.glat, P.glon, P.Q, P.Echar)

    print(iono)

    fg = figure()
    ax = fg.gca()

    vars = {"NeOut", "NeIn"}

    for v in vars:
        iono[v].plot(ax=ax, y="alt_km", xscale="log", label=v)
        ax.set_ylabel("altitude (km)")
    ax.legend()

    fg = figure()
    ax = fg.gca()
    vars = {"O+", "N2"}

    for v in vars:
        iono[v].plot(ax=ax, y="alt_km", xscale="log", label=v)
        ax.set_ylabel("altitude (km)")
    ax.legend()

    fg2 = figure()
    ax2 = fg2.gca()
    iono["Tn"].plot(ax=ax2, y="alt_km", label="Tn")

    fg3 = figure()
    ax3 = fg3.gca()
    for v in iono["ver"].wavelength:
        iono["ver"].sel(wavelength=v).plot(
            ax=ax3, y="alt_km", xscale="log", label=v.item()
        )
    ax3.legend()
    ax3.set_title("Volume Emission Rate (VER)")

    show()
