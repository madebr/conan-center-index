from conans import ConanFile, CMake, tools
import glob
import os


class PerplexConan(ConanFile):
    name = "perplex"
    description = "Perplex is a simple tool to simplify the creation of scanners using re2c."
    topics = ("conan", "re2", "regex")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stepcode/baffledCitrus/tree/master/perplex"
    license = "BRL-CAD", "BSD-3-Clause"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("baffledCitrus-*")[0], self._source_subfolder)
        tools.rmdir(os.path.join(self._source_subfolder, "cmake"))
        tools.rmdir(os.path.join(self._source_subfolder, "lemon"))
        tools.rmdir(os.path.join(self._source_subfolder, "re2c"))

    def build_requirements(self):
        self.build_requires("lemon/3.32.3")
        self.build_requires("re2c/1.3")

    def requirements(self):
        self.requires("re2c/1.3")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DATA_DIR"] = "bin"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
