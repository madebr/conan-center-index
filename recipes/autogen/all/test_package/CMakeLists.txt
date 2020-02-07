cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_program(AUTOGEN_BIN autogen)

add_custom_command(OUTPUT list.c list.h
    COMMAND ${AUTOGEN_BIN} -L "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/list.def"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/list.def" "${CMAKE_CURRENT_SOURCE_DIR}/list.tpl"
)

add_executable(${PROJECT_NAME} list.c list.h test_package.c)
target_include_directories(${PROJECT_NAME}
    PUBLIC ${PROJECT_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
