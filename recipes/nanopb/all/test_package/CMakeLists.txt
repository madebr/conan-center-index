cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

#set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../extra)
#find_package(Nanopb REQUIRED)
#include_directories(${NANOPB_INCLUDE_DIRS})#

#nanopb_generate_cpp(PROTO_SRCS PROTO_HDRS simple.proto)
include_directories(${CMAKE_CURRENT_BINARY_DIR})
#add_custom_target(generate_proto_sources DEPENDS ${PROTO_SRCS} ${PROTO_HDRS})
set_source_files_properties(${PROTO_SRCS} ${PROTO_HDRS}
    PROPERTIES GENERATED TRUE)

add_executable(simple simple.c ${PROTO_SRCS} ${PROTO_HDRS})
target_include_directories(simple PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
