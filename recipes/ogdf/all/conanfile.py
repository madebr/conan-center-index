from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import string


class OgdfConan(ConanFile):
    name = "ogdf"
    description = "the Open Graph Drawing Framework/Open Graph algorithms and Data structure Framework"
    topics = ("conan", "ogdf", "graph", "algorithm", "automatic", "drawing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.ogdf.net/"
    license = ("GPL-2.0-with-special-exceptions", "GPL-3.0-with-special-exceptions")
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "memory_manager": ["strings", "pool_ts", "pool_nts", "malloc_ts"],
        "coin_solver": ["clp", "cpx", "grb"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "memory_manager": "pool_ts",
        "coin_solver": "clp",
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

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

    def requirements(self):
        self.requires("coin-clp/1.17.6")
        self.requires("coin-osi/0.108.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("ogdf-*-{}".format("".join(c for c in self.version if c in string.digits)))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OGDF_MEMORY_MANAGER"] = str(self.options.memory_manager).upper()
        self._cmake.definitions["COIN_SOLVER"] = str(self.options.coin_solver).upper()
        self._cmake.definitions["OGDF_INSTALL_RUNTIME_DIR"] = "/".join((self.package_folder, "bin"))
        self._cmake.definitions["OGDF_INSTALL_LIBRARY_DIR"] = "/".join((self.package_folder, "lib"))
        self._cmake.definitions["OGDF_INSTALL_INCLUDE_DIR"] = "/".join((self.package_folder, "include"))
        self._cmake.definitions["OGDF_INSTALL_CMAKE_DIR"] = "/".join((self.package_folder, "lib", "cmake"))
        self._cmake.definitions["COIN_INSTALL_RUNTIME_DIR"] = "/".join((self.package_folder, "bin"))
        self._cmake.definitions["COIN_INSTALL_LIBRARY_DIR"] = "/".join((self.package_folder, "lib"))
        self._cmake.definitions["COIN_INSTALL_INCLUDE_DIR"] = "/".join((self.package_folder, "include"))
        self._cmake.definitions["COIN_INSTALL_CMAKE_DIR"] = "/".join((self.package_folder, "lib", "cmake"))
        self._cmake.definitions["COIN_SOLVER"] = str(self.options.coin_solver).upper()

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE_GPL_v2.txt", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("LICENSE_GPL_v3.txt", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["OGDF", "COIN"]
        self.cpp_info.filenames["cmake_find_package"] = "OGDF"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OGDF"
        self.cpp_info.names["cmake_find_package"] = "OGDF"  # FIXME: creates a `OGDF` target (no OGDF::OGDF)
        self.cpp_info.names["cmake_find_package_multi"] = "OGDF"  # FIXME: creates a `OGDF` target (no OGDF::OGDF)
