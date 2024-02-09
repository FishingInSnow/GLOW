# GLOW
The GLobal airglOW Model

This directory contains:
   Fortran-90 source code files,
   Makefiles,
   Example input and output files,
   Example job script,
   Subdirectory data/ contains input data files,
   Subdirectory data/iri90 contains IRI input data files

## Quickstart

The GLOW source code is unmodified.
This means a lot of variables output in space-physics/NCAR-GLOW are not present here.

With Python:

```sh
python glow_basic.py -h
```

Shows you the input options to specify.
This approach is very similar to space-physics/NCAR-GLOW using stdin/stdout to pass data in text format and parse into xarray.Dataset.

### Fortran alone

If you don't wish to use Python, you can use the Fortran code directly.

```sh
cmake -B build
cmake --build build
```

```sh
build/glowbasic < in.basic.aur
```
