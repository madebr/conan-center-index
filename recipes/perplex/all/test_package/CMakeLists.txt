cmake_minimum_required(VERSION 2.8.12)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_custom_command(OUTPUT test_package.c
    COMMAND perplex -c -o basic_nr.re "${PROJECT_SOURCE_DIR}/basic_nr.l"
    COMMAND re2c -W basic_nr.re -o test_package.c
    BYPRODUCTS basic_nr.re
)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
