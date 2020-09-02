from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class UclConan(ConanFile):
    name = "ucl"
    description = "UCL is a portable lossless data compression library written in ANSI C."
    homepage = "http://www.oberhumer.com/opensource/ucl/"
    topics = ("conan", "ucl", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GP"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC


    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        configure_args = [
            "--with-pic" if self.options.get_safe("fPIC") in (True, None, ) else "--without-pic",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
        ]
        self._autotools.flags.append("-std=c90")
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=configure_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libucl.la"))

    def package_info(self):
        self.cpp_info.libs = ["ucl"]
