from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "The GNU Binutils are a collection of binary tools."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/binutils"
    topics = ("conan", "binutils", "ld", "linker", "as", "assembler", "objcopy", "objdump")
    settings = "os", "arch", "compiler", "build_type", "os_target", "arch_target"

    options = {
        "bfd": [True, False],
        "gold": [True, False],
        "multilib": [True, False],
        "with_libquadmath": [True, False],
        # "arch_target": "ANY",
        # "os_target": "ANY",
    }

    default_options = {
        "bfd": True,
        "gold": True,
        "multilib": True,
        "with_libquadmath": True,
        # "arch_target": None,
        # "os_target": None,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _triplet_arch_lut = {
        "x86": "i686",
        "x86_64": "x86_64",
    }

    @property
    def _triplet_arch_target(self):
        return self._triplet_arch_lut.get(str(self.settings.arch_target), str(self.settings.arch_target).lower())

    _triplet_os_lut = {
        "MacOS": "darwin",
        "Windows": "mingw32",
    }

    @property
    def _triplet_os_target(self):
        return self._triplet_os_lut.get(str(self.settings.os_target), str(self.settings.os_target).lower())

    _vendor_default = {
        "Windows": "w64",
    }

    @property
    def _triplet_vendor_target(self):
        return self._vendor_default.get(str(self.settings.os_target), "conan")

    @property
    def _triplet_target(self):
        return "{}-{}-{}".format(self._triplet_arch_target, self._triplet_vendor_target, self._triplet_os_target)

    def config_options(self):
        if str(self.settings.arch_target) == str(None):
            self.settings.arch_target = self.settings.arch
        if str(self.settings.os_target) == str(None):
            self.settings.os_target = self.settings.os
        if self.settings.os_target != "Linux":
            del self.options.gold

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ \
                and not tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def requirements(self):
        self.requires("gmp/6.2.0")
        self.requires("mpfr/4.1.0")
        self.requires("zlib/1.2.11")
        # self.build_requirements("bison/???")
        # self.build_requirements("flex/???")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("binutils-{}".format(self.version), self._source_subfolder)

    @property
    def _exec_prefix(self):
        return os.path.join(self.package_folder, "bin", "exec_prefix")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda tf : "yes" if tf else "no"
        conf_args = [
            "--target={}".format(self._triplet_target),
            "--enable-gold={}".format(yes_no(self.options.get_safe("gold"))),
            "--enable-ld={}".format(yes_no(self.options.bfd)),
            "--enable-multilib={}".format(yes_no(self.options.multilib)),
            "--with-system-zlib",
            "--with-mpfr={}".format(tools.unix_path(self.deps_cpp_info["mpfr"].rootpath)),
            "--with-gmp={}".format(tools.unix_path(self.deps_cpp_info["gmp"].rootpath)),
            "--disable-nls",
            "exec_prefix={}".format(tools.unix_path(self._exec_prefix)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        # FIXME: should the vendor be included in the package_id?

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        target_bindir = os.path.join(self._exec_prefix, self._triplet_target, "bin")
        self.output.info("Appending PATH environment variable: {}".format(target_bindir))
        self.env_info.PATH.append(target_bindir)
