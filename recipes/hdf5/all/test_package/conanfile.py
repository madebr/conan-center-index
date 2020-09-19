from conans import ConanFile, CMake, tools
import os.path


class Hdf5TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["HDF5_FIND_DEBUG"] = True
        cmake.definitions["HDF5_USE_STATIC_LIBRARIES"] = not self.options["hdf5"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
