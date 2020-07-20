from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class DoxygenCOnan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("conan", "doxygen", "installer", "devtool", "documentation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    options = {
        "doxysearch": [True, False],
        "english_only": [True, False],
        "with_sqlite3": [True, False],
        "with_libclang": [True, False],
    }
    default_options = {
        "doxysearch": True,
        "english_only": False,
        "with_sqlite3": False,
        "with_libclang": False,
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libiconv/1.16")
        if self.options.doxysearch:
            self.requires("xapian-core/1.4.16")
            self.requires("zlib/1.2.11")
        if self.options.with_sqlite3:
            self.requires("sqlite3/3.32.3")
        if self.options.with_libclang:
            # FIXME: missing libclang recipe
            raise ConanInvalidConfiguration("libclang is not available (yet) on CCI")

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.5.3")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["build_parse"] = True
        self._cmake.definitions["build_search"] = self.options.doxysearch
        self._cmake.definitions["use_sqlite3"] = self.options.with_sqlite3
        self._cmake.definitions["use_libclang"] = self.options.with_libclang
        self._cmake.definitions["english_only"] = self.options.english_only
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["win_static"] = "MT" in str(self.settings.compiler.runtime)
        self._cmake.definitions["build_wizard"] = False
        self._cmake.definitions["build_app"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        # doxygen provides a FindXapian.cmake file which is "wrong". Official xapian project provides Findxapian.cmake
        os.unlink(os.path.join(os.path.join(self._source_subfolder, "cmake", "FindXapian.cmake")))
        os.rename("Findxapian.cmake", "FindXapian.cmake")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses",)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(binpath))
        self.env_info.PATH.append(binpath)
