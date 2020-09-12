from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class PatchConan(ConanFile):
    name = "patch"
    description = "Patch takes a patch file containing a difference listing produced by the diff program and applies those differences to one or more original files, producing patched versions."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://savannah.gnu.org/projects/patch"
    license = "GPL-3-or-later"
    topics = ("conan", "patch", "diff", "apply")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("automake/1.16.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("patch-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            env = {
                "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                "LD": "{} link -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
            }
            with tools.environment_append(env):
                with tools.vcvars(self.settings):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = []
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            cmake = self._configure_autotools()
            cmake.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

        with self._build_context():
            cmake = self._configure_autotools()
            cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
