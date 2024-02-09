cmake_minimum_required(VERSION 3.19)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR "In-source builds are not allowed.")
endif()

project(GLOW LANGUAGES Fortran)

enable_testing()

file(GENERATE OUTPUT ".gitignore" CONTENT "*")

if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU")
    add_compile_options(-std=legacy -ffree-line-length-none)
    # add_compile_options(-fallow-argument-mismatch)
endif()

add_executable(glowbasic cglow.f90 glowbasic.f90 glow.f90 bands.f90 conduct.f90 egrid.f90 ephoto.f90 etrans.f90 exsect.f fieldm.f gchem.f90 geomag.f90 maxt.f90 mzgrid.f90 qback.f90 rcolum.f90 rout.f90 snoem.f90 snoemint.f90 solzen.f90 ssflux.f90 iri90.f nrlmsise00.f)

add_test(NAME glowbasic
COMMAND ${CMAKE_COMMAND}
  -Dexe:FILEPATH=$<TARGET_FILE:glowbasic>
  -Din:FILEPATH=${CMAKE_CURRENT_SOURCE_DIR}/in.basic.aur
  -P ${CMAKE_CURRENT_SOURCE_DIR}/test_glow.cmake
WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
set_property(TEST glowbasic PROPERTY TIMEOUT 5)
set_property(TEST glowbasic PROPERTY PASS_REGULAR_EXPRESSION "(Z.*Tn)")
