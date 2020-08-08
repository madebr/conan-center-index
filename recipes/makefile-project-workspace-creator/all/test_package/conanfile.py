from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "test_package_c.c", "test_package_cpp.cpp", "test_package.mpc"

    def build_requirements(self):
        if not tools.cross_building(self.settings) and self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6@")

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), dst=os.path.join(self.build_folder, src))

        if not tools.cross_building(self.settings):
            t = "nmake" if self.settings.compiler == "Visual Studio" else "automake"
            self.run("perl {} -type {}".format(self.deps_user_info["makefile-project-workspace-creator"].MWC, t))

            if self.settings.compiler == "Visual Studio":
                self._build_msvc()
            else:
                self._build_autotools()

    def _build_autotools(self):
        if not os.path.isfile("configure.ac"):
            raise ConanException("conanfigure.ac not generated")

        self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        autotools.configure()
        autotools.make()

    def _build_msvc(self):
        with tools.vcvars(self.settings):
            self.run("nmake")

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("perl -S mpc.pl --version", run_environment=True)
        if not tools.cross_building(self.settings):
            self.run(os.path.join(".", "test_package_c"), run_environment=True)
            self.run(os.path.join(".", "test_package_cpp"), run_environment=True)
