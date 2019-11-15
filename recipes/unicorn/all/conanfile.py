from conans import ConanFile, CMake, tools
import os


class UnicornConan(ConanFile):
    name = "unicorn"
    license = "GPL-2.0-or-later"
    homepage = "http://www.unicorn-engine.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "unicorn", "emulator", "cpu")
    description = "Unicorn is a lightweight multi-platform, multi-architecture CPU emulator framework."
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt",
    generators  = "cmake",

    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows" or self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "unicorn-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        pass

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["UNICORN_STATIC_MSVCRT"] = "MT" in str(self.settings.compiler.runtime)

        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING.LGPL2", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING_GLIB", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.name = "JsonCpp"
        self.cpp_info.libs = tools.collect_libs(self)
