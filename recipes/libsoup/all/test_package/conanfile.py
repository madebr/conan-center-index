import os
from conans import ConanFile, CMake, tools


class SolaceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.joiN("bin", "test_package")
            self.run(bin_path, run_environment=True)
