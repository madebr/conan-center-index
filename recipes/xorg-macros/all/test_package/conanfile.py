from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "configure.ac", "Makefile.am",

    def build_requirements(self):
        self.build_requires("automake/1.16.2")
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)
        print(tools.get_env("AUTOMAKE_CONAN_INCLUDES"))
        self.run("{} --verbose".format(tools.get_env("ACLOCAL")), win_bash=tools.os_info.is_windows, run_environment=True)
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows, run_environment=True)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure()

    def test(self):
        pass
