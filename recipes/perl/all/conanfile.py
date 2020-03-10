from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class PerlConan(ConanFile):
    name = "perl"
    description = "Perl is a highly capable, feature-rich programming language with over 30 years of development"
    homepage = "https://www.perl.org/"
    topics = ("conan", "perl", "scripting", "programming")
    license = "???"
    url = "https://github.com/conan-io/conan-center-index"
    exports = "patches/**"
    settings = "os_build", "arch_build", "compiler"  # FIXME!!!
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    # def build_requirements(self):
    #     self.build_requires("libtool/2.4.6")
    #     if not tools.which("help2man"):
    #         self.build_requires("help2man/1.47.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("perl-{}".format(self.version), self._source_subfolder)

    _cc = {
        "gcc": "gcc",
        "clang": "clang",
        "clang-mac": "clang",
    }

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        cc = self._cc.get(str(self.settings.compiler))
        conf_args = [
            "-Dcc={}".format(cc),
        ]
        self.run("{} {}".format(os.path.join(self._source_subfolder, "Configure"), " ".join(conf_args)))
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("Copying", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "bash-completion"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "doc"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

