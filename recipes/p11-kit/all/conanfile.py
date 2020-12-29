from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


conan_minimum_requires = ">=1.29.1"


class P11KitTLS(ConanFile):
    name = "p11-kit"
    description = "Provides a way to load and enumerate PKCS#11 modules"
    homepage = "https://p11-glue.github.io/p11-glue/p11-kit.html"
    topics = ("conan", "p11-kit", "load", "enumerate", "install", "PKCS#11", "certificate")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_libffi": [True, False],
        "with_libtasn1": [True, False],
        "with_hash": ["internal", "freebl"],
        "with_systemd": [True, False],
        "trust_paths": "ANY",
    }
    default_options = {
        "with_libffi": True,
        "with_libtasn1": True,
        "with_hash": "internal",
        "with_systemd": False,
        "trust_paths": None,
    }
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("p11-kit cannot be built for Windows")
        # if not self.options.shared:
        #     raise ConanInvalidConfiguration("p11-kit cannot be used as a static library")
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
        if self.options.with_systemd:
            self.requires("libsystemd/246.6")
        if self.options.with_hash == "freebl":
            raise ConanInvalidConfiguration("nss is not (yet) available on cci")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--with-hash-impl={}".format(self.options.with_hash),
            "--with-libtasn1={}".format(yes_no(self.options.with_libtasn1)),
            "--with-libffi={}".format(yes_no(self.options.with_libffi)),
            "--with-systemd" if self.options.with_systemd else "--without-systemd",
            "--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share").replace("\\", "/")),
            "--with-trust-paths={}".format(":".join(self._trust_paths)) if self._trust_paths else "--without-trust-paths",
            "--disable-nls",
            "--disable-rpath",
            "--without-bash-completion",
            "--enable-shared",
            "--disable-static",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.libs = ["p11-kit"]
        self.cpp_info.includedirs.append(os.path.join("include", "p11-kit-1"))
        self.cpp_info.names["pkg_config"] = "p11-kit-1"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
