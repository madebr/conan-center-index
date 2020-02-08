import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class PkgConfigConan(ConanFile):
    name = "pkg-config"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The pkg-config program is used to retrieve information about installed libraries in the system"
    license = "GPL-2.0-or-later"
    homepage = "https://www.freedesktop.org/wiki/Software/pkg-config"
    topics = ("conan", "pkg-config", "package", "config")
    settings = "os_build", "arch_build", "compiler"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    # def build_requirements(self):
    #     if self.settings.compiler != "Visual Studio":
    #         if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
    #                 tools.os_info.detect_windows_subsystem() != "msys2":
    #             self.build_requires("msys2/20190524")

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Builds with Visual Studio aren't currently supported, "
                                            "use MinGW instead to build for Windows")

    # def configure(self):
    #     if self.settings.os_build != "Windows":
    #         raise ConanInvalidConfiguration("Only Windows supported")
    #     if self.settings.arch_build not in ("x86", "x86_64"):
    #         raise ConanInvalidConfiguration("Unsupported architecture")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pkg-config-{}".format(self.version), self._source_subfolder)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        # http://www.linuxfromscratch.org/lfs/view/systemd/chapter06/pkg-config.html
        conf_args = [
            "--with-internal-glib",
            "--disable-host-tool",
            "--datarootdir={}".format(self._datarootdir),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self._datarootdir, "doc"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))
        # FIXME: compile static library????
        # if self._is_mingw_windows:
        #     package_folder = tools.unix_path(os.path.join(self.package_folder, "bin"))
        #     tools.run_in_windows_bash(self, "cp $(which libwinpthread-1.dll) {}".format(package_folder))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        binext = ".exe" if self.settings.os_build == "Windows" else ""

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        pkg_config_bin = os.path.join(bindir, "pkg-config{}".format(binext))
        self.output.info("Setting PKG_CONFIG env var: {}".format(pkg_config_bin))
        self.env_info.PKG_CONFIG.append(pkg_config_bin)
