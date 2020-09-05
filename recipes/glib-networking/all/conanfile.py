from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
import os


class GLibNetworkingConan(ConanFile):
    name = "glib-networking"
    description = "GLib Networking contains Network related gio modules for GLib."
    topics = ("conan", "glib", "networking", "gio", "gmodule")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/glib-networking"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }
    generators = "pkg_config"

    _meson = None
    
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
        self.build_requires("meson/0.55.0")
        self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        self.requires("glib/2.65.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glib-networking-{}".format(self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        # self._meson.options

        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self.settings.compiler == "Visual Studio" else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self.settings.compiler == "Visual Studio" else tools.no_op():
            meson = self._configure_meson()
            meson.install()

    def package_info(self):
        pass
