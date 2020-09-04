from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class E2fsProgsConan(ConanFile):
    name = "e2fsprogs"
    description = "GNU Libidn is a fully documented implementation of the Stringprep, Punycode and IDNA 2003 specifications."
    homepage = "https://www.gnu.org/software/libidn/"
    topics = ("conan", "libidn", "encode", "decode", "internationalized", "domain", "name")
    license = "NOTICE"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("e2fsprogs is not supported on Windows")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("e2fsprogs-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        pass

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share").replace("\\", "/")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-elf-shlibs={}".format(yes_no(self.options.shared and self.settings.os != "FreeBSD")),
            "--enable-bsd-shlibs={}".format(yes_no(self.options.shared and self.settings.os == "FreeBSD")),
            "--disable-nls",
            "--disable-rpath",
            "--datarootdir={}".format(self._datarootdir),
            "--with-systemd-unit-dir={}".format(os.path.join(self.package_folder, "etc", "systemd").replace("\\", "/")),
            "--with-crond-dir={}".format(os.path.join(self.package_folder, "etc", "cron.d").replace("\\", "/")),
            "--with-udev-rules-dir={}".format(os.path.join(self.package_folder, "etc", "udev", "rules.d").replace("\\", "/")),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("NOTICE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        if self.options.shared:
            for fn in glob.glob(os.path.join(self.package_folder, "lib", "*.a")):
                os.unlink(fn)

        tools.rmdir(os.path.join(self.package_folder, "lib", "e2fsprogs"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self._datarootdir, "info"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.components["com_err"].libs = ["com_err"]
        self.cpp_info.components["com_err"].names["pkg_config"] = "com_err"
        if self.settings.os == "Linux":
            self.cpp_info.components["com_err"].system_libs = ["pthread", "rt"]

        self.cpp_info.components["e2p"].libs = ["e2p"]
        self.cpp_info.components["e2p"].names["pkg_config"] = "e2p"

        self.cpp_info.components["ext2fs"].libs = ["ext2fs"]
        self.cpp_info.components["ext2fs"].names["pkg_config"] = "ext2fs"
        self.cpp_info.components["ext2fs"].requires = ["com_err"]

        self.cpp_info.components["ss"].libs = ["ss"]
        self.cpp_info.components["ss"].names["pkg_config"] = "ss"
        self.cpp_info.components["ss"].requires = ["com_err"]
        if self.settings.os == "Linux":
            self.cpp_info.components["ss"].system_libs = ["dl"]

        bin_path = os.path.join(self.package_folder, "bin").replace("\\", "/")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        datadir = self._datarootdir
        self.env_info.E2FSPROGS_CONAN_DATADIR = datadir
