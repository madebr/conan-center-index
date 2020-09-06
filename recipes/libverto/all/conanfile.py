from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class LibVertoConan(ConanFile):
    name = "libverto"
    description = "An async event loop abstraction library."
    homepage = "https://github.com/latchset/libverto"
    topics = ("conan", "libverto", "async", "eventloop")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "pthread": [True, False],
        "with_glib": ["auto", "builtin", True, False],
        "with_libev": ["auto", "builtin", True, False],
        "with_libevent": ["auto", "builtin", True, False],
        "with_tevent": ["auto", "builtin", True, False],
        "default": ["glib", "libev", "libevent", "tevent"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "pthread": True,
        "with_libev": "auto",
        "with_glib": "auto",
        "with_libevent": "auto",
        "with_tevent": "auto",
        "default": "libevent",
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    generators = "pkg_config"

    _autotools = None

    @property
    def _all_auto(self):
        return all(self.options.get_safe(opt) == "auto" for opt in ("with_glib", "with_libev", "with_libevent", "with_tevent"))

    @property
    def _with_glib(self):
        if self.options.with_glib == "auto":
            if self._all_auto:
                return "builtin" if self.options.default == "glib" else False
            else:
                return False
        else:
            return self.options.with_glib

    @property
    def _with_libev(self):
        if self.options.with_libev == "auto":
            if self._all_auto:
                return "builtin" if self.options.default == "libev" else False
            else:
                return False
        else:
            return self.options.with_libev

    @property
    def _with_libevent(self):
        if self.options.with_libevent == "auto":
            if self._all_auto:
                return "builtin" if self.options.default == "libevent" else False
            else:
                return False
        else:
            return self.options.with_libevent

    @property
    def _with_tevent(self):
        if self.options.with_tevent == "auto":
            if self._all_auto:
                return "builtin" if self.options.default == "tevent" else False
            else:
                return False
        else:
            return self.options.with_tevent

    @property
    def _backend_dict(self):
        return {
            "glib": self._with_glib,
            "libev": self._with_libev,
            "libevent": self._with_libevent,
            "tevent": self._with_tevent,
        }

    @property
    def _event_opts(self):
        return tuple(self._backend_dict.values())

    @property
    def _with_builtin(self):
        return any(opt == "builtin" for opt in self._event_opts)

    @property
    def _avaiable_backends(self):
        return tuple(backend for backend, opt in self._backend_dict.items() if opt != False)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.pthread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libverto does not support Visual Studio")

        count = lambda iterable: sum(1 if it else 0 for it in iterable)
        count_builtins = count(opt == "builtin" for opt in self._event_opts)
        count_externals = count(opt == True for opt in self._event_opts)
        if count_builtins > 1:
            raise ConanInvalidConfiguration("Cannot have more then one builtin backends")
        if not self.options.shared:
            if count_externals > 0:
                raise ConanInvalidConfiguration("Cannot have a non-builtin backend when building a static libverto")
        if count_builtins > 0 and count_externals > 0:
            raise ConanInvalidConfiguration("Cannot combine builtin and external backends")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libverto-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        if self._with_glib:
            self.requires("glib/2.65.1")
        if self._with_libevent:
            self.requires("libevent/2.1.12")
        if self._with_libev:
            self.requires("libev/4.33")
        if self._with_tevent:
            self.requires("tevent/0.10.2")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.link_flags.extend("-L{}".format(p.replace("\\", "/")) for p in self.deps_cpp_info.lib_paths)
        yes_no = lambda v: "yes" if v else "no"
        yes_no_builtin = lambda v: {"True": "yes", "False": "no", "builtin": "builtin"}[str(v)]
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pthread={}".format(yes_no(self.options.get_safe("pthread"))),
            "--with-glib={}".format(yes_no_builtin(self._with_glib)),
            "--with-libev={}".format(yes_no_builtin(self._with_libev)),
            "--with-libevent={}".format(yes_no_builtin(self._with_libevent)),
            "--with-tevent={}".format(yes_no_builtin(self._with_tevent)),
        ]
        with tools.environment_append({"PKG_CONFIG_PATH": self.install_folder.replace("\\", "/")}):
            self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": tools.get_env("AUTOMAKE_CONAN_INCLUDES").replace(";", ":")}):
                self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libverto.la"))

        # if self._with_glib:
        #     os.unlink(os.path.join(self.package_folder, "lib", "libverto-glib.la"))
        # if self._with_libev:
        #     os.unlink(os.path.join(self.package_folder, "lib", "libverto-libev.la"))
        # if self._with_libevent:
        #     os.unlink(os.path.join(self.package_folder, "lib", "libverto-libevent.la"))
        # if self._with_tevent:
        #     os.unlink(os.path.join(self.package_folder, "lib", "libverto-tevent.la"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        del self.info.options.default
        self.info.options.with_glib = self._with_glib
        self.info.options.with_libev = self._with_libev
        self.info.options.with_libevent = self._with_libevent
        self.info.options.with_tevent = self._with_tevent

    def package_info(self):
        self.cpp_info.components["verto"].libs = ["verto"]
        self.cpp_info.components["verto"].names["pkg_config"] = "libverto"
        if self.settings.os == "Linux":
            self.cpp_info.components["verto"].system_libs.append("dl")
            if self.options.pthread:
                self.cpp_info.components["verto"].system_libs.append("pthread")

        if self._with_builtin:
            if self._with_glib:
                self.cpp_info.components["verto"].requires = ["glib::glib"]

            if self._with_libev:
                self.cpp_info.components["verto"].requires = ["libev::libev"]

            if self._with_libevent:
                self.cpp_info.components["verto"].requires = ["libevent::libevent"]

            if self._with_tevent:
                self.cpp_info.components["verto"].requires = ["tevent::tevent"]
        else:
            if self._with_glib:
                self.cpp_info.components["verto-glib"].libs = ["verto-glib"]
                self.cpp_info.components["verto-glib"].names["pkg_config"] = "libverto-glib"
                self.cpp_info.components["verto-glib"].requires = ["verto", "glib::glib"]

            if self._with_libev:
                self.cpp_info.components["verto-libev"].libs = ["verto-libev"]
                self.cpp_info.components["verto-libev"].names["pkg_config"] = "libverto-libev"
                self.cpp_info.components["verto-libev"].requires = ["verto", "libev::libev"]

            if self._with_libevent:
                self.cpp_info.components["verto-libevent"].libs = ["verto-libevent"]
                self.cpp_info.components["verto-libevent"].names["pkg_config"] = "libverto-libevent"
                self.cpp_info.components["verto-libevent"].requires = ["verto", "libevent::libevent"]

            if self._with_tevent:
                self.cpp_info.components["verto-tevent"].libs = ["verto-tevent"]
                self.cpp_info.components["verto-tevent"].names["pkg_config"] = "libverto-tevent"
                self.cpp_info.components["verto-tevent"].requires = ["verto", "tevent::tevent"]

        self.user_info.backends = ",".join(self._avaiable_backends)
