from conans import CMake, ConanFile, tools
import os


class LibFtdi1(ConanFile):
    name = "libftdi1"
    description = "libFTDI - FTDI USB driver with bitbang mode"
    topics = ("conan", "libconfuse", "configuration", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.intra2net.com/en/developer/libftdi"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", )
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # "enable_cpp_wrapper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # "enable_cpp_wrapper": False,
    }
    generators = "cmake", "cmake_find_package"

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libftdi1-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libusb/1.0.23")
        self.requires("boost/1.73.0")
        self.requires("libconfuse/3.2.2")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["STATICLIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["DOCUMENTATION"] = False
        self._cmake.definitions["EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["PYTHON_BINDINGS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "\nset(CMAKE_MODULE_PATH ",
                              "\nlist(APPEND CMAKE_MODULE_PATH ")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}",
                              "${PROJECT_SOURCE_DIR}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdipp", "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}",
                              "${PROJECT_SOURCE_DIR}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdi_eeprom", "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}",
                              "${PROJECT_SOURCE_DIR}")
        tools.save_append(os.path.join(self._source_subfolder, "ftdi_eeprom", "CMakeLists.txt"),
                          "\ntarget_link_libraries(ftdi_eeprom CONAN_PKG::libusb CONAN_PKG::libconfuse)\n")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${LIB_SUFFIX}",
                              "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "${LIB_SUFFIX}",
                              "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdipp", "CMakeLists.txt"),
                              "${LIB_SUFFIX}",
                              "")
        tools.save(os.path.join(self._source_subfolder, "cmake", "FindUSB1.cmake"),
                   "set(LIBUSB_FOUND TRUE)\n"
                   "set(LIBUSB_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_LIBUSB})\n"
                   "set(LIBUSB_LIBRARIES CONAN_PKG::libusb)\n")
        os.unlink(os.path.join(self._source_subfolder, "cmake", "FindConfuse.cmake"))
        tools.save_append(os.path.join(self.install_folder, "Findlibconfuse.cmake"),
                          "\nset(CONFUSE_FOUND ON)\n")
        os.rename(os.path.join(self.install_folder, "Findlibconfuse.cmake"),
                  os.path.join(self.install_folder, "FindConfuse.cmake"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdi_eeprom", "CMakeLists.txt"),
                              "CONFUSE_INCLUDE_DIRS", "LIBCONFUSE_INCLUDE_DIRS")
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdi_eeprom", "CMakeLists.txt"),
                              "${CONFUSE_LIBRARIES}", "CONAN_PKG::libconfuse")
        if not self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "ftdi_eeprom", "CMakeLists.txt"),
                                  "target_link_libraries ( ftdi_eeprom ftdi1 ",
                                  "target_link_libraries ( ftdi_eeprom ftdi1-static ")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        os.unlink(os.path.join(self.package_folder, "bin", "libftdi1-config"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibFTDI1"
        self.cpp_info.names["cmake_find_package_multi"] = "LibFTDI1"
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "libftdi1"))
        self.cpp_info.libs = ["ftdipp1", "ftdi1"]
