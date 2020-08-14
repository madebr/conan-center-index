from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class HwlocTestConan(ConanFile):
    name = "hwloc"
    description = "UNKNOWN_DESCRIPTION"
    topics = ("conan", "hwloc-embedded-test")
    license = "UNKNOWN_LICENSES"
    homepage = "UNKNOWN_HOMEPAGE"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "embedded_mode": [True, False],
        "cpuid": [True, False],
        "io": [True, False],
        "opencl": [True, False],
        "cuda": [True, False],
        "pci": [True, False],
        "symbol_prefix": "ANY",
        "with_libxml2": [True, False],
        "with_udev": ["auto", True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "embedded_mode": False,
        "cpuid": True,
        "io": True,
        "opencl": False,  # FIXME: default should be True
        "cuda": False,  # FIXME: default should be True
        "pci": True,
        "symbol_prefix": "hwloc_",
        "with_libxml2": True,
        "with_udev": "auto",
    }
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_udev
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.cpuid

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.with_udev == False and self.settings.os == "Linux":
            raise ConanInvalidConfiguration("Linux requires udev")

    def requirements(self):
        if self.options.pci:
            self.requires("libpciaccess/0.15")
        if self.options.opencl:
            # FIXME: missing opencl cci recipe
            raise ConanInvalidConfiguration("cci has no opencl recipe (yet)")
        if self.options.cuda:
            # FIXME: missing cuda cci recipe
            raise ConanInvalidConfiguration("cci has no cuda recipe (yet)")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.10")
        # if self.options.with_udev:
        #     self.requires("udev/system")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("hwloc-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                    "HWLOC_MS_LIB": "lib",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        enable_disable = lambda name, v: "--enable-{}={}".format(name, "yes" if v else "no")
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = [
            enable_disable("embedded-mode", self.options.embedded_mode),
            enable_disable("libxml2", self.options.with_libxml2),
            enable_disable("udev", self.options.get_safe("with_udev", False)),
            enable_disable("io", self.options.io),
            enable_disable("opencl", self.options.opencl),
            enable_disable("cuda", self.options.cuda),
            enable_disable("pci", self.options.pci),
            enable_disable("cpuid", self.options.get_safe("cpuid", False)),
            "--with-hwloc-plugins-path=",
            enable_disable("shared", self.options.shared),
            enable_disable("static", not self.options.shared),
            enable_disable("debug", self.settings.build_type == "Debug"),
            "--with-hwloc-symbol-prefix={}".format(self.options.symbol_prefix),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libhwloc.la")))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["hwloc"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
                self.cpp_info.system_libs.append("udev")

        self.output.info("hwloc plugins can be added by adding its path to the HWLOC_PLUGINS_PATH environment variable")
