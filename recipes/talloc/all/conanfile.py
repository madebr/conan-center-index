from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import shlex


class TallocConan(ConanFile):
    name = "talloc"
    description = "talloc is a hierarchical, reference counted memory pool system with destructors."
    homepage = "http://talloc.samba.org/"
    topics = ("conan", "talloc", "memory", "allocator", "reference", "count", "destructor")
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"

    _waf = None

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
        if not self.options.shared:
            raise ConanInvalidConfiguration("talloc does not support static libraries (due to its new waf build system)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("talloc-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LINK": "link -nologo",
                    "AR": "lib",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_waf(self):
        # talloc, as part of samba, uses a specialized waf client
        if self._waf:
            return self._waf
        waf_cmd = os.path.join(self.source_folder, self._source_subfolder, "buildtools", "bin", "waf").replace("\\", "/")
        self._waf = WafBuildHelper(self, configure_folder=self._source_subfolder, waf=waf_cmd)
        conf_args = [
            "--without-gettext",
            "--disable-python",
            "--disable-rpath",
            "--disable-rpath-install",
            "-C",
        ]
        if self.settings.build_type == "Debug":
            conf_args.append("--enable-debug")
        self._waf.configure(args=conf_args)
        return self._waf

    def build(self):
        with self._build_context():
            waf = self._configure_waf()
            waf.build()

    @property
    def _license_text(self):
        talloc_c = tools.load(os.path.join(self._source_subfolder, "talloc.c"))
        return talloc_c[talloc_c.find("/*")+2:talloc_c.find("*/")]

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        with self._build_context():
            waf = self._configure_waf()
            waf.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["talloc"]
        self.cpp_info.names["pkg_config"] = "talloc"
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("dl")


class WafBuildHelper(object):
    def __init__(self, conanfile, configure_folder=None, waf="waf"):
        self.conanfile = conanfile
        self.vars = AutoToolsBuildEnvironment(conanfile).vars
        if "pkg_config" in self.conanfile.generators:
            self.vars["PKG_CONFIG_PATH"] = [self.conanfile.install_folder]
        self.configure_folder = os.path.realpath(configure_folder) if configure_folder is not None else None
        self.waf = waf

    def run_waf(self, args):
        safe_args = " ".join(shlex.quote(a) for a in args)
        with tools.chdir(self.configure_folder) if self.configure_folder else tools.no_op():
            self.conanfile.run("{} {}".format(self.waf, safe_args))

    def configure(self, args=None):
        args = args if args is not None else []
        waf_args = ["configure"] + args
        if not self._is_flag_in_args("prefix", waf_args):
            waf_args.append("--prefix={}".format(self.conanfile.package_folder).replace("\\", "/"))

        with tools.environment_append(self.vars):
            self.run_waf(waf_args)

    def build(self, args=None):
        args = args if args is not None else []
        waf_args = ["build"] + args
        self.run_waf(waf_args)

    def install(self, args=None):
        args = args if args is not None else []
        waf_args = ["install"] + args
        self.run_waf(waf_args)

    @staticmethod
    def _is_flag_in_args(varname, args):
        flag = "--%s=" % varname
        return any([flag in arg for arg in args])
