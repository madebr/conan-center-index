import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class GitConan(ConanFile):
    name = "git"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency."
    license = "GPL-2.0"
    homepage = "https://git-scm.com/"
    topics = ("conan", "git", "scm", "collaboration")
    settings = "os_build", "arch_build", "compiler"
    exports_sources = "patches/**"

    generators = "pkg_config"

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

    def requirements(self):
        self.requires("openssl/1.1.1d", private=True)
        self.requires("pcre2/10.33", private=True)
        self.requires("libcurl/7.68.0", private=True)
        self.requires("expat/2.2.9", private=True)
        self.requires("zlib/1.2.11")

    # def build_requirements(self):
    #     if self.settings.compiler != "Visual Studio":
    #         if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
    #                 tools.os_info.detect_windows_subsystem() != "msys2":
    #             self.build_requires("msys2/20190524")

    # def config_options(self):
    #     if self.settings.compiler == "Visual Studio":
    #         raise ConanInvalidConfiguration("Builds with Visual Studio aren't currently supported, "
    #                                         "use MinGW instead to build for Windows")

    # def configure(self):
    #     if self.settings.os_build != "Windows":
    #         raise ConanInvalidConfiguration("Only Windows supported")
    #     if self.settings.arch_build not in ("x86", "x86_64"):
    #         raise ConanInvalidConfiguration("Unsupported architecture")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("git-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--with-openssl",
            "--with-libpcre2",
            "--with-curl",
            "--with-expat",
            "--without-tcltk",  # tk is not available (yet)
        ]
        self._autotools.link_flags.extend(self._autotools.vars_dict["LIBS"])
        print("link_flags", self._autotools.link_flags)
        self._autotools.configure(args=conf_args)
        return self._autotools

    def _patch_sources(self):
        for patch_data in self.conan_data["patches"][self.version]:
            tools.patch(**patch_data)

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        binext = ".exe" if self.settings.os_build == "Windows" else ""

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        git_bin = os.path.join(bindir, "git{}".format(binext))
        self.output.info("Setting GIT env var: {}".format(git_bin))
        self.env_info.GIT.append(git_bin)
