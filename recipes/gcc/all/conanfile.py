from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class GccConan(ConanFile):
    name = "gcc"
    description = "The GNU Compiler Collection includes front ends for C, C++, Objective-C, Fortran, Ada, Go, and D, as well as libraries for these languages (libstdc++,...)"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://gcc.gnu.org"
    topics = ("conan", "gcc", "gnu", "compiler")
    settings = "os", "arch", "compiler", "build_type", "os_target", "arch_target"

    no_copy_source = True

    options = {
    }

    default_options = {
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _arch_target(self):
        return str(self.settings.arch_target)

    _triplet_arch_lut = {
        "x86": "i686",
        "x86_64": "x86_64",
    }

    @property
    def _triplet_arch_target(self):
        return self._triplet_arch_lut.get(self._arch_target, str(self._arch_target).lower())

    @property
    def _os_target(self):
        return str(self.settings.os_target)

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

    def config_options(self):
        if str(self.settings.arch_target) == str(None):
            self.settings.arch_target = self.settings.arch
        if str(self.settings.os_target) == str(None):
            self.settings.os_target = self.settings.os

    def requirements(self):
        # if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ \
        #         and not tools.os_info.detect_windows_subsystem() != "msys2":
        #     self.build_requires("msys2/20190524")
        self.requires("gmp/6.2.0")
        self.requires("mpfr/4.1.0")
        self.requires("zlib/1.2.11")
        self.requires("mpc/1.1.0")
        # if self.settings.os_target == "Windows":
        #     self.requires("mingw-w64/7.0.0")

    def build_requirements(self):
        self.build_requires("binutils/")
        # self.build_requires("bison/???")
        # self.build_requires("flex/???")
        pass

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
        self._autotools.include_paths = []
        self._autotools.libs = []
        yes_no = lambda tf : "yes" if tf else "no"
        conf_args = [
            "--target={}".format(tools.get_gnu_triplet(os_=str(self.settings.os_target), arch=str(self.settings.arch_target), compiler="gcc")),
            "--disable-nls",
            "--enable-languages=c,c++",  # all, default, ada, c, c++, d, fortran, go, jit, lto, objc, obj-c++
            # "--disable-boostrap",
            "--with-system-zlib",
            "--disable-win32-registry",
            "--with-mpc={}".format(self.deps_cpp_info["mpc"].rootpath),
            "--with-mpfr={}".format(self.deps_cpp_info["mpfr"].rootpath),
            "--with-gmp={}".format(self.deps_cpp_info["gmp"].rootpath),
            "--disable-nls",
            "exec_prefix={}".format(self._exec_prefix),
        ]
        self._autotools.configure(args=conf_args, configure_dir=os.path.join(self.source_folder, self._source_subfolder))
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        with tools.environment_append({"BOOT_CFLAGS": "-G"}):
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

        # Don't add sysroot/bin to PATH to avoid possible conflict between different binutils when cross building
        self.user_info.SYSROOT = os.path.join(self._exec_prefix, self._triplet_target)
