cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_REQUIRED_INCLUDES ${CONAN_INCLUDE_DIRS})

add_subdirectory(source_subfolder)
