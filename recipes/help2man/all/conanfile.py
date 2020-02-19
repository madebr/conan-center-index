from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException
import os


class Help2ManConan(ConanFile):
    name = "help2man"
    description = "help2man produces simple manual pages from the ‘--help’ and ‘--version’ output of other commands"
    homepage = "https://www.gnu.org/software/help2man"
    topics = ("conan", "help2man", "manual", "page")
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os_build"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        if not tools.which("perl"):
            if tools.os_info.is_windows:
                self.requires("strawberryperl/5.30.0.1")
            else:
                raise ConanException("perl not found")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(binpath))
        self.env_info.PATH.append(binpath)
