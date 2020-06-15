cmake_minimum_required(VERSION 3.3.0)
project(conan_abc)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_definitions(${CONAN_DEFINES})
include_directories(${CONAN_INCLUDE_DIRS})
link_libraries(${CONAN_LIBS})

if(ABC_WITH_READLINE)
    find_package(readline REQUIRED)
else()
    set(READLINE_FOUND FALSE)
endif()

add_subdirectory(source_subfolder)
