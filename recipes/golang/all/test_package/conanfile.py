from conans import CMake, ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type", "os_target", "arch_target"

    def build(self):
        if not tools.cross_building(self.settings):
            self.run("go build '{}'".format(os.path.join(self.source_folder, "test_package.go")))

    def test(self):
        if not tools.cross_building(self.settings) and (self.settings.os, self.settings.arch) == (self.settings.os_target, self.settings.arch_target):
            self.run("./test_package", run_environment=True)
