from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import glob
import os


class LibPciaccessConan(ConanFile):
    name = "libpciaccess"
    description = "Generic PCI access library"
    topics = ("conan", "libpciaccess", "pci", )
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libpciaccess"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    # def requirements(self):
    #     pass

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("libtool/2.4.6")
        self.build_requires("xorg-macros/1.19.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("libpciaccess-*")[0], self._source_subfolder)

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
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libpciaccess.la")))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["pciaccess"]
