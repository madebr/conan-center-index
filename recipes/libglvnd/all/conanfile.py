import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibGLVndConan(ConanFile):
    name = "libglvnd"
    homepage = "https://github.com/zeromq/libzmq"
    description = "libglvnd is a vendor-neutral dispatch layer for arbitrating OpenGL API calls between multiple vendors"
    topics = ("conan", "libglvnd", "openGL", "vendor-neutral", "GLES", "EGL", "GLX")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "egl": [True, False],
        "x11": [True, False],
        "glx": [True, False],
        "gles": [True, False],
        "asm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "egl": True,
        "x11": True,
        "glx": True,
        "gles": True,
        "asm": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libglvnd cannot be used on Windows")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.glx and not self.options.x11:
            raise ConanInvalidConfiguration("Cannot build glx without x11")

    def requirements(self):
        if self.options.x11:
            self.requires("x11/??")
        if self.options.glx:
            self.requires("xext/??")
            self.requires("glproto/??")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libglvnd-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        en_dis = lambda name : "--{}-{}".format("enable" if self.options.get_safe(name) else "disable", name)
        conf_args = [
            en_dis("egl"),
            en_dis("x11"),
            en_dis("glx"),
            en_dis("gles"),
            "-enable-headers",
            en_dis("asm"),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    @property
    def _license_text(self):
        src = open(os.path.join(self._source_subfolder, "src", "GL", "libgl.c")).read()
        lines = src[src.find("/*")+2:src.find("*/")].split()
        return "\n".join([l.strip(" *") for l in lines])

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        pass
