cmake_minimum_required(VERSION 3.15...3.29)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR "In-source builds are not allowed.")
endif()

project(GLOW LANGUAGES Fortran)

enable_testing()

include(FetchContent)

option(CMAKE_TLS_VERIFY "Enable TLS certificate verification" ON)

file(GENERATE OUTPUT ".gitignore" CONTENT "*")

set(glow_url https://github.com/NCAR/GLOW/archive/refs/tags/v0.981.tar.gz)

set(FETCHCONTENT_QUIET OFF)
set(FETCHCONTENT_UPDATES_DISCONNECTED ON)

FetchContent_Declare(ncar_glow
URL ${glow_url}
)

if(NOT ncar_glow_POPULATED)
  FetchContent_Populate(ncar_glow)
endif()

if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU")
    add_compile_options(-std=legacy -ffree-line-length-none)
    # add_compile_options(-fallow-argument-mismatch)
endif()

set(s ${ncar_glow_SOURCE_DIR})

add_executable(glowbasic ${s}/cglow.f90 ${s}/glowbasic.f90 ${s}/glow.f90
${s}/bands.f90 ${s}/conduct.f90 ${s}/egrid.f90 ${s}/ephoto.f90 ${s}/etrans.f90
${s}/exsect.f ${s}/fieldm.f ${s}/gchem.f90 ${s}/geomag.f90 ${s}/maxt.f90
${s}/mzgrid.f90 ${s}/qback.f90 ${s}/rcolum.f90 ${s}/rout.f90 ${s}/snoem.f90
${s}/snoemint.f90 ${s}/solzen.f90 ${s}/ssflux.f90 ${s}/iri90.f ${s}/nrlmsise00.f
)

add_test(NAME glowbasic
COMMAND ${CMAKE_COMMAND}
  -Dexe:FILEPATH=$<TARGET_FILE:glowbasic>
  -Din:FILEPATH=${s}/in.basic.aur
  -P ${CMAKE_CURRENT_SOURCE_DIR}/test_glow.cmake
WORKING_DIRECTORY ${s}
)
set_property(TEST glowbasic PROPERTY TIMEOUT 5)
set_property(TEST glowbasic PROPERTY PASS_REGULAR_EXPRESSION "(Z.*Tn)")
