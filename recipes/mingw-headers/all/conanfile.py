import os
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class MingwHeaders(ConanFile):
    name = "mingw-headers"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/mingw-w64/"
    license = "Zlib"
    description = "The mingw-w64 project is a complete runtime environment for gcc to support binaries native to Windows 64-bit and 32-bit operating systems."
    topics = ("zip", "compression", "inflate")
    # settings = "os", "arch", "compiler", "build_type"
    # options = {"shared": [True, False], "fPIC": [True, False], "bzip2": [True, False], "tools": [True, False]}
    # default_options = {"shared": False, "fPIC": True, "bzip2": True, "tools": False}
    # exports_sources = ["CMakeLists.txt", "*.patch"]
    # generators = "cmake", "cmake_find_package"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    # def config_options(self):
    #     if self.settings.os == "Windows":
    #         del self.options.fPIC
    #
    # def configure(self):
    #     del self.settings.compiler.libcxx
    #     del self.settings.compiler.cppstd
    #
    # def requirements(self):
    #     self.requires("zlib/1.2.11")
    #     if self.options.bzip2:
    #         self.requires("bzip2/1.0.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mingw-w64-v{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("DISCLAIMER", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

    # def package_info(self):
    #     self.cpp_info.libs = ["minizip"]
    #     self.cpp_info.includedirs = ["include", os.path.join("include", "minizip")]
    #     if self.options.bzip2:
    #         self.cpp_info.defines.append('HAVE_BZIP2')
