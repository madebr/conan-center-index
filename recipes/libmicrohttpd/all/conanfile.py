from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class LibmicrohttpdConan(ConanFile):
    name = "libmicrohttpd"
    description = "A small C library that is supposed to make it easy to run an HTTP server"
    homepage = "https://www.gnu.org/software/libmicrohttpd/"
    topics = ("conan", "libmicrohttpd", "httpd", "server")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_https": [True, False],
        "with_error_messages": [True, False],
        "with_postprocessor": [True, False],
        "with_digest_authentification": [True, False],
        "epoll": [True, False],
        "with_zlib": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_https": False,  # FIXME: should be True, but gnutls is not yet available in cci
        "with_error_messages": True,
        "with_postprocessor": True,
        "with_digest_authentification": True,
        "epoll": True,
        "with_zlib": True,
    }
    generators = "pkg_config"

    _autotools = False

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.epoll

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("This package cannot be built using Visual Studio")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_https:
            raise ConanInvalidConfiguration("gnutls is not (yet) available in cci")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libmicrohttpd-{}".format(self.version), self._source_subfolder)

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
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-https={}".format(yes_no(self.options.with_https)),
            "--enable-messages={}".format(yes_no(self.options.with_error_messages)),
            "--enable-postprocessor={}".format(yes_no(self.options.with_postprocessor)),
            "--enable-dauth={}".format(yes_no(self.options.with_digest_authentification)),
            "--enable-epoll={}".format(yes_no(self.options.get_safe("epoll"))),
            "--disable-doc",
            "--disable-examples",
            "--disable-curl",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        pass
        # original_def = "__attribute__((visibility(\\\"default\\\"))) __declspec(dllexport) extern"
        # extern_def = """$as_echo "#define _MHD_EXTERN {}" >>confdefs.h"""
        # configure = os.path.join(self._source_subfolder, "configure")
        # if self.options.shared:
        #     if self.settings.os == "Windows":
        #         new_def = "_declspec(dllexport)"
        #     else:
        #         new_def = "__declspec((visibility(\"default\")))"
        # else:
        #     new_def = "extern"
        # tools.replace_in_file(configure, extern_def.format(original_def), extern_def.format(new_def))

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libmicrohttpd"
        self.cpp_info.libs = ["microhttpd"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("MHD_W32DLL")
            self.cpp_info.system_libs = ["ws2_32"]
