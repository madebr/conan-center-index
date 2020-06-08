import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class MediainfoConan(ConanFile):
    name = "mediainfo"
    license = ("BSD-2-Clause", "Apache-2.0", "GLPL-2.1+", "GPL-2.0-or-later", "MPL-2.0")
    homepage = "https://mediaarea.net/en/MediaInfo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MediaInfo is a convenient unified display of the most relevant technical and tag data for video and audio files"
    topics = ("conan", "mediainfo", "cli", "gui", "video", "audio", "metadata", "tag")
    settings = "os",  "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def requirements(self):
        self.requires("libmediainfo/{}".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("MediaInfo", self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder, "Project", "GNU", "CLI"))
        return self._autotools

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "Project", "GNU", "CLI", "autogen.sh"),
                              "glibtoolize", "libtoolize")
        with tools.chdir(os.path.join(self._source_subfolder, "Project", "GNU", "CLI")):
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
        with tools.chdir(os.path.join(self._source_subfolder, "Source")):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("License.html", src=self._source_subfolder, dst="licenses")
        with tools.chdir(os.path.join(self._source_subfolder, "Source")):
            autotools = self._configure_autotools()
            autotools.install()

    def package_id(self):
        del self.settings.build_type
        del self.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
