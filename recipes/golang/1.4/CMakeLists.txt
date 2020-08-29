cmake_minimum_required(VERSION 3.1)
project(compiler_detector LANGUAGES C CXX)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(WRITE detected_compiler.txt "${CMAKE_C_COMPILER}\n${CMAKE_CXX_COMPILER}\n")
