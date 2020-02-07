from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class GccConan(ConanFile):
    name = "gcc"
    description = "The GNU Compiler Collection includes front ends for C, C++, Objective-C, Fortran, Ada, Go, and D, as well as libraries for these languages (libstdc++,...)"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://gcc.gnu.org"
    topics = ("conan", "gcc", "gnu", "compiler")
    settings = "os_build", "arch_build", "compiler"

    no_copy_source = True

    options = {
        "arch_target": "ANY",
        "os_target": "ANY",
    }

    default_options = {
        "arch_target": None,
        "os_target": None,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _arch_target(self):
        return str(self.options.arch_target or self.settings.arch_build)

    _triplet_arch_lut = {
        "x86": "i686",
        "x86_64": "x86_64",
    }

    @property
    def _triplet_arch_target(self):
        return self._triplet_arch_lut.get(self._arch_target, str(self._arch_target).lower())

    @property
    def _os_target(self):
        return str(self.options.os_target or self.settings.os_build)

    _triplet_os_lut = {
        "MacOS": "darwin",
        "Windows": "mingw32",
    }

    @property
    def _triplet_os_target(self):
        return self._triplet_os_lut.get(self._os_target, str(self._os_target).lower())

    _vendor_default = {
        "Windows": "w64",
    }

    @property
    def _triplet_vendor_target(self):
        return self._vendor_default.get(self._os_target, "conan")

    @property
    def _triplet_target(self):
        return "{}-{}-{}".format(self._triplet_arch_target, self._triplet_vendor_target, self._triplet_os_target)

    # def build_requirements(self):
    #     if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ \
    #             and not tools.os_info.detect_windows_subsystem() != "msys2":
    #         self.build_requires("msys2/20190524")
    #     self.build_requires("gmp/6.1.2")
    #     self.build_requires("mpfr/4.0.2")
    #     self.build_requires("zlib/1.2.11")
    #     # self.build_requirements("bison/???")
    #     # self.build_requirements("flex/???")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("gcc-{}".format(self.version), self._source_subfolder)

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
            "--enable-gold={}".format(yes_no(self.options.with_gold)),
            "--enable-ld={}".format(yes_no(self.options.with_ld)),
            "--disable-multilib",
            "--with-system-zlib",
            "--with-mpfr={}".format(self.deps_cpp_info["mpfr"].rootpath),
            "--with-gmp={}".format(self.deps_cpp_info["gmp"].rootpath),
            "--disable-nls",
            "exec_prefix={}".format(self._exec_prefix),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYTING*", src=self._source_subfolder, dst="licenses")
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
