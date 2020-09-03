cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

include(FindPkgConfig)
pkg_check_modules(ss REQUIRED IMPORTED_TARGET ss)

find_program(MK_CMDS mk_cmds)
if(NOT MK_CMDS)
    message(FATAL_ERROR "mk_cmds not found")
endif()

add_custom_command(OUTPUT cmds.c
    COMMAND "${MK_CMDS}" "${PROJECT_SOURCE_DIR}/cmds.ct"
    DEPENDS "${PROJECT_SOURCE_DIR}/cmds.ct"
)

add_executable(${PROJECT_NAME} test_package.c cmds.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::ss)
