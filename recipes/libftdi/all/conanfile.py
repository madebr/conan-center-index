import os
from conans import ConanFile, CMake, tools


class LibFtdiConan(ConanFile):
    name = "libftdi1"
    description = "A library to talk to FTDI chips"
    license = ["MIT", "BSD-3-Clause"]
    topics = ("conan", "libftdi1")
    homepage = "http://developer.intra2net.com/git/?p=libftdi;a=summary"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"

    _cmake = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("libusb/1.0.23")
        self.requires("libconfuse/3.2.2")
        self.requires("boost/1.72.0")

    def _configure_cmake(self):
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        os.unlink(os.path.join(self.package_folder, "bin", "libftdi1-config"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibFTDI1"
        self.cpp_info.names["cmake_find_package_multi"] = "LibFTDI1"
        self.cpp_info.names["pkgconfig"] = "libftdi1"
        self.cpp_info.includedirs.append(
            os.path.join(self.package_folder, "include", "libftdi1")
        )
        self.cpp_info.libs = ["ftdipp1", "ftdi1"]