from conans import AutoToolsBuildEnvironment, ConanFile, tools
import glob
import os


class XorgMacrosConan(ConanFile):
    name = "xorg-macros"
    description = "GNU autoconf macros shared across X.Org projects"
    topics = ("conan", "autoconf", "macros", "build", "system", "m4")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/macros"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    exports_sources = "patches/**"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("automake/1.16.2")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("macros-*")[0], self._source_subfolder)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--datarootdir={}".format(tools.unix_path(self._datarootdir)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self._datarootdir, "pkgconfig"))
        tools.rmdir(os.path.join(self._datarootdir, "util-macros"))

    def package_info(self):
        aclocal = tools.unix_path(os.path.join(self._datarootdir, "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)
