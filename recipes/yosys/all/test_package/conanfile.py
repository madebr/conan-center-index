from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        with tools.environment_append(RunEnvironment(self).vars):
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run("{} {}".format(bin_path, os.path.join(self.source_folder, "demo.blif")), run_environment=True)
