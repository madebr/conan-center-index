import os
from conans import ConanFile, CMake, tools


class OrToolsConan(ConanFile):
    name = "or-tools"
    description = "Google's software suite for combinatorial optimization"
    homepage = "https://developers.google.com/optimization/"
    license = "Apache-2.0"
    topics = ("conan", "or-tools", "combinatorial", "optimization")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_coinor": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_coinor": True,
    }
    exports_sources = "CMakeLists.txt"
    no_copy_source = True
    generators = "cmake", "pkg_config", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    # @property
    # def _build_subfolder(self):
    #     return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("abseil/20200225.2")
        self.requires("glog/0.4.0")
        self.requires("zlib/1.2.11")
        self.requires("protobuf/3.11.4")
        if self.options.with_coinor:
            self.requires("coin-utils/2.11.4")
            self.requires("coin-clp/1.17.6")
            self.requires("coin-cbc/2.10.5")
            self.requires("coin-osi/0.108.6")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("or-tools-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_CXX"] = True

        self._cmake.definitions["USE_SCIP"] = False  # FIXME: add scip recipe
        self._cmake.definitions["USE_COINOR"] = self.options.with_coinor
        self._cmake.definitions["USE_CPLEX"] = False # FIXME: add CPLEX solver
        self._cmake.definitions["USE_XPRESS"] = False # FIXME: add XPRESSsolver

        self._cmake.definitions["BUILD_SAMPLES"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOXYGEN"] = False

        self._cmake.definitions["BUILD_DEPS"] = False
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["BUILD_JAVA"] = False
        self._cmake.definitions["BUILD_DOTNET"] = False

        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE-2.0.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        pass
