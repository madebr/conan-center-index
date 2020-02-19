from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class CrosstoolNGConan(ConanFile):
    name = "crosstool-ng"
    description = "Crosstool-NG is a versatile (cross) toolchain generator"
    homepage = "https://github.com/crosstool-ng/crosstool-ng/"
    topics = ("conan", "crosstool-ng", "toolchain", "gcc", "cross", "build", "crossbuilding")
    license = ("GPL-2.0-or-later", "LGPL-2.1-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    exports = "patches/**"
    settings = "os_build", "arch_build"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("ncurses/6.2")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if not tools.which("help2man"):
            self.build_requires("help2man/1.47.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{0}-{0}-{1}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self.run("./bootstrap", cwd=self._source_subfolder)
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "share"))),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        tools.save(os.path.join(self._source_subfolder, ".tarball-version"), "{}\n".format(self.version))
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "bash-completion"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "doc"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
