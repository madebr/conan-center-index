from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/fontconfig"
    description = "Fontconfig is a library for configuring and customizing font access"
    topics = ("conan", "fontconfig", "font", "discover", "find")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_xml": ["expat", "libxml2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xml": "expat",
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("gperf/3.1")

    def requirements(self):
        if self.options.with_xml == "expat":
            self.requires("expat/2.2.9")
        elif self.options.with_xml == "libxml2":
            self.requires("libxml2/2.9.9")
        self.requires("freetype/2.10.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("fontconfig-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--sysconfdir={}".format(os.path.join(self.package_folder, "lib", "etc")),
            "--datarootdir={}".format(os.path.join(self.package_folder, "lib", "share")),
            "--disable-docs",
        ]
        if self.options.with_xml == "libxml2":
            conf_args.append("--enable-libxml2")
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch_data in self.conan_data["patches"][self.version]:
            tools.patch(**patch_data)

    def build(self):
        tools.replace_in_file("freetype2.pc",
                              "\nVersion: ",
                              "\nVersion: {}\n#Version: ".format(self.deps_user_info["freetype"].LIBTOOL_VERSION))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        os.chmod(os.path.join(self.package_folder, "licenses", "COPYING"), 0o644)
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libfontconfig.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share", "gettext"))
        tools.rmdir(os.path.join(self.package_folder, "share", "locale"))
        tools.rmdir(os.path.join(self.package_folder, "var"))

    def package_info(self):
        self.cpp_info.includedirs = ["include", os.path.join("include", "fontconfig")]
        self.cpp_info.libs = ["fontconfig"]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        fontconfig_root = self.package_folder
        self.output.info("Settings FONTCONFIG_SYSROOT environment variable: {}".format(fontconfig_root))
        self.env_info.FONTCONFIG_SYSROOT = fontconfig_root
