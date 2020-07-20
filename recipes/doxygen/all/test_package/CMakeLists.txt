cmake_minimum_required(VERSION 3.3)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Doxygen REQUIRED)

doxygen_add_docs(html test_package.cpp ALL COMMENT "generating docs...")
