from conans import ConanFile, Meson, tools
import os


class LibSoupConan(ConanFile):
    name = "libsoup"
    description = "libsoup is an HTTP client/server library for GNOME."
    homepage = "https://gitlab.gnome.org/GNOME/libsoup"
    topics = ("conan", "http", "client", "server", "gnome", "gobject", "glib")
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_brotli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_brotli": True,
    }
    exports_sources = "patches/**"
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

    def requirements(self):
        self.requires("glib/2.65.1")
        self.requires("glib-networking/2.65.1")
        self.requires("sqlite3/3.32.3")
        self.requires("libxml2/2.9.10")
        self.requires("libpsl/0.21.1")
        self.requires("zlib/1.2.11")
        if self.options.with_brotli:
            self.requires("brotli/1.0.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libsoup-{}".format(self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        enabled_disabled = lambda v: "enabled" if v else "disabled"
        self._meson = Meson(self)
        self._meson.options["brotli"] = enabled_disabled(self.options.with_brotli)
        self._meson.options["gnome"] = False
        self._meson.options["introspection"] = enabled_disabled(False)  # FIXME: missing gobject-introspection recipe
        self._meson.options["gssapi"] = enabled_disabled(False)
        self._meson.options["ntlm"] = enabled_disabled(False)  # FIXME: missing samba-winbind-client (linux only option)
        self._meson.options["vapi"] = enabled_disabled(False)
        self._meson.options["tests"] = False
        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    @property
    def _abi_version(self):
        return "2.4"

    def package_info(self):
        self.cpp_info.libs = ["soup-{}".format(self._abi_version)]
        self.cpp_info.names["pkg_config"] = "soup-{}".format(self._abi_version)
        self.cpp_info.includedirs.append(os.path.join("include", "libsoup-{}".format(self._abi_version)))
