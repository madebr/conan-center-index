from conans import CMake, ConanFile, tools
import os


class NaiveTsearchConan(ConanFile):
    name = "naive-tsearch"
    description = "simple tsearch() implementation for platforms without one"
    topics = ("conan","tsearch", "tfind", "tdelete", "twalk")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kulp/naive-tsearch"
    license = "MIT"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.header_only:
            del self.options.shared
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        version = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]
        os.rename("naive-tsearch-{}".format(version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NAIVE_TSEARCH_INSTALL_HDRONLY"] = True
        self._cmake.definitions["NAIVE_TSEARCH_INSTALL_LIB"] = not self.options.header_only
        self._cmake.definitions["NAIVE_TSEARCH_INSTALL"] = True
        self._cmake.definitions["NAIVE_TSEARCH_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = ["header_only"]
        self.cpp_info.includedirs.append(os.path.join("include", "naive-tsearch"))
