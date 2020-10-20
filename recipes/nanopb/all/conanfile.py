from conans import CMake, ConanFile, tools
import os


class NanopbConan(ConanFile):
    name = "nanopb"
    description = "Protocol Buffers with small code size"
    topics = "UNKNOWN TOPICS"
    license = "https://github.com/nanopb/nanopb"
    homepage = "https://github.com/nanopb/nanopb"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake_find_package", "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("protobuf/3.11.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["nanopb_BUILD_RUNTIME"] = True
        self._cmake.definitions["nanopb_BUILD_GENERATOR"] = True
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["nanopb_MSVC_STATIC_RUNTIME"] = "MT" in str(self.settings.compiler.runtime)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        # tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "nanopb"
        self.cpp_info.names["cmake_find_package_multi"] = "nanopb"

        self.cpp_info.components["_nanopb"].libs = ["protobuf-nanopb"]
        self.cpp_info.components["_nanopb"].names["cmake_find_package"] = "protobuf-nanopb" if self.options.shared else "protobuf-nanopb-static"
        self.cpp_info.components["_nanopb"].names["cmake_find_package_multi"] = "protobuf-nanopb" if self.options.shared else "protobuf-nanopb-static"
