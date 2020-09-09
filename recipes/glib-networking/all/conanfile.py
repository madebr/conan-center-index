from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import glob
import itertools
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
        "with_openssl": [True, False],
        "with_gnutls": [True, False],
        "with_libproxy": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_openssl": True,
        "with_gnutls": False,  # FIXME: glib-networking has as default tls backend gnutls
        "with_libproxy": True,
    }
    generators = "pkg_config"
    exports_sources = "patches/**"

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
        if not any((self.options.with_gnutls, self.options.with_openssl)):
            raise ConanInvalidConfiguration("Need at least one tls backend")

    def build_requirements(self):
        self.build_requires("meson/0.55.0")
        self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        self.requires("glib/2.65.1")
        if self.options.with_libproxy:
            self.requires("libproxy/0.4.15")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1g")
        if self.options.with_gnutls:
            # FIXME: missing gnutls recipe
            raise ConanInvalidConfiguration("gnutls recipe is not (yet) available on cci")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glib-networking-{}".format(self.version), self._source_subfolder)

    @property
    def _gio_module_dir(self):
        return os.path.join("lib", "gio", "modules")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        enabled_disabled = lambda v: "enabled" if v else "disabled"

        self._meson = Meson(self)
        self._meson.options["static_modules"] = not self.options.shared
        self._meson.options["gio_module_dir"] = os.path.join(self.package_folder, self._gio_module_dir)
        self._meson.options["openssl"] = enabled_disabled(self.options.with_openssl)
        self._meson.options["gnutls"] = enabled_disabled(self.options.with_gnutls)
        self._meson.options["libproxy"] = enabled_disabled(self.options.with_libproxy)

        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self.settings.compiler == "Visual Studio" else tools.no_op():
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(VisualStudioBuildEnvironment(self).vars) if self.settings.compiler == "Visual Studio" else tools.no_op():
            meson = self._configure_meson()
            meson.install()

        if not self.options.shared:
            with tools.chdir(os.path.join(self.package_folder, self._gio_module_dir)):
                for file in itertools.chain(glob.glob("*.dll"), glob.glob("*.so"), glob.glob("*.dylib")):
                    os.unlink(file)

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "systemd"))
        # tools.rmdir(os.path.join(self.package_folder, self._gio_module_dir, "pkgconfig"))

    def package_info(self):
        if self.options.with_openssl:
            self.cpp_info.components["gioopenssl"].libs = ["gioopenssl"]
            self.cpp_info.components["gioopenssl"].libdirs = [self._gio_module_dir]
            if self.settings.os == "Windows":
                self.cpp_info.components["gioopenssl"].bindirs.append(self._gio_module_dir)
            self.cpp_info.components["gioopenssl"].requires = ["glib::gio", "openssl::openssl"]
            # self.cpp_info.components["gioopenssl"].names["pkg_config"] = "gioopenssl"

        if self.options.with_gnutls:
            self.cpp_info.components["giognutls"].libs = ["giognutls"]
            self.cpp_info.components["giognutls"].libdirs = [self._gio_module_dir]
            if self.settings.os == "Windows":
                self.cpp_info.components["giognutls"].bindirs.append(self._gio_module_dir)
            self.cpp_info.components["giognutls"].requires = ["glib::gio", "gnutls::gnutls"]
            # self.cpp_info.components["giognutls"].names["pkg_config"] = "giognutls"

        if self.options.with_libproxy:
            self.cpp_info.components["giolibproxy"].libs = ["giolibproxy"]
            self.cpp_info.components["giolibproxy"].libdirs = [self._gio_module_dir]
            if self.settings.os == "Windows":
                self.cpp_info.components["giolibproxy"].bindirs.append(self._gio_module_dir)
            self.cpp_info.components["giolibproxy"].requires = ["glib::gio", "libproxy::libproxy"]
            # self.cpp_info.components["giolibproxy"].names["pkg_config"] = "giolibproxy"

        gio_extra_modules = os.path.join(self.package_folder, self._gio_module_dir)
        self.output.info("Appending GIO_EXTRA_MODULES environment variable: {}".format(gio_extra_modules))
        self.env_info.GIO_EXTRA_MODULES.append(gio_extra_modules)

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
