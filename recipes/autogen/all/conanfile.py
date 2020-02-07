from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class AutoGenConan(ConanFile):
    name = "autogen"
    description = "AutoGen is a tool designed to simplify the creation and maintenance of programs that contain large amounts of repetitious text."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/autogen"
    topics = ("conan", "autogen", "text", "generator")
    settings = "os_build", "arch_build", "compiler"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ \
                and not tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("gmp/6.1.2")
        self.build_requires("mpfr/4.0.2")
        self.build_requires("zlib/1.2.11")
        self.build_requires("guile/2.2.6")
        # self.build_requirements("bison/???")
        # self.build_requirements("flex/???")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("autogen-{}".format(self.version), self._source_subfolder)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--disable-dependency-tracking",
            "--disable-shared", "--enable-static",
            "--datarootdir={}".format(self._datarootdir),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
