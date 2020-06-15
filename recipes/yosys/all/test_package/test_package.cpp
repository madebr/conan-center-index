#include "kernel/yosys.h"

#include <iostream>

int main(int argc, const char *argv[]) {
    Yosys::yosys_banner();
    Yosys::yosys_setup();
    std::cout << "yosys version string: " << Yosys::yosys_version_str << "\n";
    Yosys::yosys_shutdown();
    return 0;
}
