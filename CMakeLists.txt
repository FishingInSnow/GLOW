cmake_minimum_required(VERSION 3.19)

project(GLOW LANGUAGES Fortran)

add_compile_options(-std=legacy -ffree-line-length-none)

if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU" AND CMAKE_Fortran_COMPILER_VERSION VERSION_GREATER_EQUAL 10)
  add_compile_options(-fallow-argument-mismatch)
endif()

add_executable(glowbasic cglow.f90 glowbasic.f90 glow.f90 bands.f90 conduct.f90 egrid.f90 ephoto.f90 etrans.f90 exsect.f fieldm.f gchem.f90 geomag.f90 maxt.f90 mzgrid.f90 qback.f90 rcolum.f90 rout.f90 snoem.f90 snoemint.f90 solzen.f90 ssflux.f90 iri90.f nrlmsise00.f)
