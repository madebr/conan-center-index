from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class GuileConan(ConanFile):
    name = "guile"
    description = "Guile is a progamming language, designed to help programmers create flexible applications that can be extended by users or other programmers with plug-ins, modules, or scripts."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/guile"
    topics = ("conan", "guile", "language", "dialect", "scheme", "lisp")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "patches/**"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("bdwgc/8.0.4")
        self.requires("gmp/6.1.2")
        # self.requires("mpir/3.0.0")
        self.requires("libffi/3.3")
        self.requires("libtool/2.4.6")
        self.requires("libunistring/0.9.10")
        self.requires("readline/8.0")  # FIXME: only for binary

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("guile-{}".format(self.version), self._source_subfolder)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "lib", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--datarootdir={}".format(self._datarootdir),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        autotools = self._configure_autotools()
        autotools.make()

    @property
    def _bin_ext(self):
        return ".exe" if self.settings.os == "Windows" else ""

    @property
    def _major_minor_version(self):
        return ".".join(str(self.version).split(".", 2)[:2])

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libguile-{}.la".format(self._major_minor_version)))


        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self._datarootdir, "info"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "guile-{}".format(self._major_minor_version)
        self.cpp_info.includedirs = ["include", os.path.join("include", "guile", self._major_minor_version)]
        self.cpp_info.libs = ["guile-{}".format(self._major_minor_version)]

        self.cpp_info.names["pkg_config"] = "guile-{}".format(self._major_minor_version)

        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["crypt", "m", "pthread"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        guile_system_path = os.path.join(self._datarootdir, "guile", self._major_minor_version)
        self.output.info("Setting GUILE_SYSTEM_PATH env variable to {}".format(guile_system_path))
        self.env_info.GUILE_SYSTEM_PATH = guile_system_path

        guile_system_compiled_path = os.path.join(self.package_folder, "lib", "guile", self._major_minor_version, "ccache")
        self.output.info("Setting GUILE_SYSTEM_COMPILED_PATH env variable to {}".format(guile_system_compiled_path))
        self.env_info.GUILE_SYSTEM_COMPILED_PATH = guile_system_compiled_path

        guile = os.path.join(self.package_folder, "bin", "guile" + self._bin_ext)
        self.output.info("Setting GUILE env variable to {}".format(guile))
        self.env_info.GUILE = guile

        aclocal_path = os.path.join(self.package_folder, "lib", "share", "aclocal")
        self.output.info("Appending ACLOCAL_PATH environment variable: {}".format(aclocal_path))
        self.env_info.ACLOCAL_PATH.append(aclocal_path)
