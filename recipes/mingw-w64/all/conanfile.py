from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class MingwW64Conan(ConanFile):
    name = "mingw-w64"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/mingw-w64/"
    license = "Zlib"
    description = "The mingw-w64 project is a complete runtime environment for gcc to support binaries native to Windows 64-bit and 32-bit operating systems."
    topics = ("zip", "compression", "inflate")
    settings = "os", "arch", "compiler", "build_type", "os_target", "arch_target"
    # options = {"shared": [True, False], "fPIC": [True, False], "bzip2": [True, False], "tools": [True, False]}
    # default_options = {"shared": False, "fPIC": True, "bzip2": True, "tools": False}
    # exports_sources = ["CMakeLists.txt", "*.patch"]
    # generators = "cmake", "cmake_find_package"

    options = {
        "headers": [True, False],
        "crt": [True, False],
        "default_WIN32_WINNT": "ANY",
    }
    default_options = {
        "headers": True,
        "crt": True,
        "default_WIN32_WINNT": None,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("binutils/2.35")

    @property
    def _multilib(self):
        return self.options.multilib

    def config_options(self):
        if self.settings.os_target != "Windows":
            raise ConanInvalidConfiguration("This package can only be built for Windows")

    def configure(self):
        if not self.options.headers:
            del self.options.default_WIN32_NT
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    # def requirements(self):
    #     self.requires("zlib/1.2.11")
    #     if self.options.bzip2:
    #         self.requires("bzip2/1.0.8")

    @property
    def _default_WIN32_WINNT(self):
        if self.options.headers:
            opt_string = str(self.options.default_WIN32_WINNT)
            if opt_string == str(None):
                return None
            return opt_string
        else:
            return None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mingw-w64-v{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        yes_no = lambda v: "yes" if v else "no"
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)

        conf_args = [
            "--with-headers={}".format(yes_no(self.options.headers)),
            "--with-crt={}".format(yes_no(self.options.crt)),
        ]
        if self.options.headers:
            conf_args.extend([
                "--with-default-win32-winnt={}".format(self._default_WIN32_WINNT),
            ])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("DISCLAIMER", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
