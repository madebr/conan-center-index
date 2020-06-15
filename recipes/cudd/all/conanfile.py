from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import shutil


class CuddConan(ConanFile):
    name = "cudd"
    homepage = "http://vlsi.colorado.edu/~fabio/CUDD/html/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The CUDD package is a package written in C for the manipulation of decision diagrams"
    topics = ("conan", "cudd", "decision", "diagram", "bdd", "add", "zdd")
    license = "BSD-3-Clause"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                not tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "ac_cv_prog_DOXYGEN=",
            "ac_cv_prog_PDFLATEX=",
            "ac_cv_prog_MAKEINDEX=",
            "--enable-dddmp",
            "--enable-obj",
            "--with-system-qsort",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        os.unlink(os.path.join(self.package_folder, "lib", "libcudd.la"))
        for fn in (
                "config.h",
                os.path.join(self._source_subfolder, "cudd", "cuddInt.h"),
                os.path.join(self._source_subfolder, "epd", "epd.h"),
                os.path.join(self._source_subfolder, "mtr", "mtr.h"),
                os.path.join(self._source_subfolder, "st", "st.h"),
                os.path.join(self._source_subfolder, "util", "util.h")):
            shutil.copy(src=fn, dst=os.path.join(self.package_folder, "include", os.path.basename(fn)))

    def package_info(self):
        self.cpp_info.libs = ["cudd"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "psapi"])
