from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.model.settings import SettingsItem
from contextlib import contextmanager
import os


class GLibCConan(ConanFile):
    name = "glibc"
    description = "The GNU C Library provides many of the low-level components used directly by programs written in the C or C++ languages."
    topics = ("conan", "glibc", "library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libc/"
    license = "MIT"
    exports_sources = "patches/**"

    settings = "os", "arch", "compiler"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glibc-{}".format(self.version), self._source_subfolder)
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build_requirements(self):
        self.build_requires("binutils/2.34")

    @contextmanager
    def _mock_settings(self):
        """
        glibc cannot be built in Debug mode.
        Adding `build_type` to self.settings is not a solution,
        because this disallows any debug builds of dependencies.
        """
        mock_settings = self.settings.copy()
        build_type = SettingsItem(["Release"], "build_type")
        build_type.value = "Release"
        mock_settings._data["build_type"] = build_type
        original_settings = self.settings
        self.settings = mock_settings
        yield
        self.settings = original_settings

    @property
    def _sbindir(self):
        return os.path.join(self.package_folder, "bin", "sbin")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share")),
            "--without-selinux",
            "--with-binutils={}".format(os.path.join(self.deps_cpp_info["binutils"].rootpath, "bin")),
        ]
        self._autotools.configure(args=conf_args, configure_dir=os.path.join(self.source_folder, self._source_subfolder))
        return self._autotools

    def build(self):
        os.mkdir(self._build_subfolder)
        with self._mock_settings():
            with tools.chdir(self._build_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSES", src=self._source_subfolder, dst="licenses")
        with self._mock_settings():
            with tools.chdir(self._build_subfolder):
                autotools = self._configure_autotools()
                autotools.install()

        os.rename(os.path.join(self.package_folder, "sbin"), self._sbindir)

        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "var"))

    def package_info(self):
        self.cpp_info.exelinkflags = ["-Wl,-z,nodefaultlib"]
        self.cpp_info.sharedlinkflags = ["-Wl,-z,nodefaultlib"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        sbindir = self._sbindir
        self.output.info("Appending PATH environment variable: {}".format(sbindir))
        self.env_info.PATH.append(sbindir)
