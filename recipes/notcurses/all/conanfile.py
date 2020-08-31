from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class NotCursesConan(ConanFile):
    name = "notcurses"

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "pkg_config"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_multimedia": [False, "ffmpeg", "openimageio"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_multimedia": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("ncurses/6.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("notcurses-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libunistring/0.9.10")
        if self.options.with_multimedia == "ffmpeg":
            # FIXME: missing ffmpeg recipe
            raise ConanInvalidConfiguration("ffmpeg is not (yet) available on cci")
        elif self.options.with_multimedia == "openimageio":
            self.requires("openimageio/2.1.18.1")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        use_multimedia = {
            "False": "none",
            "openimageio": "oiio",
            "ffmpeg": "ffmpeg",
        }.get(str(self.options.with_multimedia), str(self.options.with_multimedia))
        self._cmake.definitions["DFSG_BUILD"] = True
        self._cmake.definitions["USE_MULTIMEDIA"] = use_multimedia
        self._cmake.definitions["USE_QRCODEGEN"] = False
        self._cmake.definitions["USE_DOCTEST"] = False
        self._cmake.definitions["USE_PANDOC"] = False
        self._cmake.definitions["USE_DOXYGEN"] = False
        self._cmake.definitions["USE_STATIC"] = not self.options.shared
        self._cmake.verbose=True
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "TINFONAME", "tinfo" + self.deps_user_info["ncurses"].lib_suffix)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "NCURSESNAME", "ncurses" + self.deps_user_info["ncurses"].lib_suffix)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Notcurses"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Notcurses"

        self.cpp_info.components["libnotcurses"].libs = ["notcurses"]
        self.cpp_info.components["libnotcurses++"].libs = ["notcurses++"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "rt"]
