cmake_minimum_required(VERSION 2.8.12)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

add_custom_command(OUTPUT "${PROJECT_BINARY_DIR}/BlinkyTop.sim.cpp"
    COMMAND "${CMAKE_COMMAND}" -E copy "${PROJECT_SOURCE_DIR}/proc.ys" "${PROJECT_SOURCE_DIR}/blinky.v" "${PROJECT_BINARY_DIR}"
    COMMAND yosys "${PROJECT_BINARY_DIR}/proc.ys"
    DEPENDS "${PROJECT_SOURCE_DIR}/proc.ys" "${PROJECT_SOURCE_DIR}/blinky.v"
)

#add_executable(${PROJECT_NAME}_cxxrtl test_package_cxxrtl.cpp "${PROJECT_BINARY_DIR}/BlinkyTop.sim.cpp")
add_executable(${PROJECT_NAME}_cxxrtl "${PROJECT_BINARY_DIR}/BlinkyTop.sim.cpp")
target_link_libraries(${PROJECT_NAME}_cxxrtl ${CONAN_LIBS})
target_include_directories(${PROJECT_NAME}_cxxrtl PRIVATE "${PROJECT_BINARY_DIR}")
