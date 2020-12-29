from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import contextlib
import os


conan_minimum_requires = ">=1.29.1"


class P11KitConan(ConanFile):
    name = "p11-kit"
    description = "Provides a way to load and enumerate PKCS#11 modules"
    homepage = "https://p11-glue.github.io/p11-glue/p11-kit.html"
    topics = ("conan", "p11-kit", "load", "enumerate", "install", "PKCS#11", "certificate")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # p11-kit is only available as a shared library
        "with_libffi": [True, False],
        "with_libtasn1": [True, False],
        "hash": ["internal", "freebl"],
        "with_systemd": [True, False],
        "trust_paths": "ANY",
    }
    default_options = {
        "with_libffi": True,
        "with_libtasn1": True,
        "hash": "internal",
        "with_systemd": False,
        "trust_paths": None,
    }
    exports_sources = "patches/*"
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
            # libtasn1 is unsupported on Windows
            self.options.with_libtasn1 = False
            self.options.with_systemd = False

    def configure(self):
        # FIXME: revisit Windows
        # if self.settings.os == "Windows":
        #     raise ConanInvalidConfiguration("p11-kit cannot be built for Windows")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _trust_paths(self):
        if self.options.trust_paths:
            return self.options.trust_paths.split(",")
        else:
            return None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("p11-kit-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        if self.options.with_libffi:
            self.requires("libffi/3.3")
        if self.options.with_libtasn1:
            self.requires("libtasn1/4.16.0")
        if self.options.get_safe("with_systemd"):
            self.requires("libsystemd/246.6")
        if self.options.hash == "freebl":
            raise ConanInvalidConfiguration("nss is not (yet) available on cci")
        if self.settings.compiler == "Visual Studio":
            self.requires("getopt-for-visual-studio/20200201")
            self.requires("dirent/1.23.2")

    def build_requirements(self):
        self.build_requires("meson/0.56.0")
        self.build_requires("pkgconf/1.7.3")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def _configure_meson(self):
        if self._meson:
            return self._meson
        feature_onoff = lambda v: "enabled" if v else "disabled"
        self._meson = Meson(self)
        self._meson.options["hash_impl"] = self.options.hash
        self._meson.options["libexecdir"] = "libexec"
        self._meson.options["trust_module"] = feature_onoff(self.options.with_libtasn1)
        self._meson.options["libffi"] = feature_onoff(self.options.with_libffi)
        self._meson.options["systemd"] = feature_onoff(self.options.get_safe("with_systemd"))
        if self._trust_paths:
            self._meson.options["trust_paths"] = ":".join(self._trust_paths)
        self._meson.options["bash_completion"] = feature_onoff(False)
        self._meson.options["gtk_doc"] = "false"
        self._meson.options["nls"] = "false"
        self._meson.options["test"] = "false"

        self._meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._meson

    @contextlib.contextmanager
    def _build_context(self):
        env = {}
        try:
            env.update({
                "MSYS_BIN": None,
                "MSYS_ROOT": None,
            })
        except KeyError:
            pass
        with tools.remove_from_path("bash") if tools.os_info.is_windows else tools.no_op():
            with tools.environment_append(env):
                yield

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            meson = self._configure_meson()
        meson.build() #args=["-j1", "-v"])

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        meson = self._configure_meson()
        meson.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "libexec"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["p11-kit"]
        self.cpp_info.includedirs.append(os.path.join("include", "p11-kit-1"))
        self.cpp_info.names["pkg_config"] = "p11-kit-1"

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
