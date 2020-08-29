from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class GolangConanfile(ConanFile):
    name = "golang"
    description = "Go is an open source programming language that makes it easy to build simple, reliable, and efficient software."
    homepage =  "https://golang.org/"
    license = "BSD-3-Clause"
    topics = ("conan", "golang", "language", "compiler")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "build_type", "arch_target", "os_target"

    options = {
        "lto": [True, False],
        "shared": [True, False],
        "race": [True, False],
        "enable_ss2": [True, False],
    }
    default_options = {
        "lto": False,
        "shared": False,
        "race": True,
        "enable_ss2": True,
    }
    exports_sources = "patches/**"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("go", self._source_subfolder)

    def config_options(self):
        if self.settings.arch != "x86":
            del self.options.enable_sse2

    def build_requirements(self):
        self.build_requires("golang/1.4.3")

    def configure(self):
        if not self.settings.arch_target:
            self.settings.arch_target = self.settings.arch
        if not self.settings.os_target:
            self.settings.os_target = self.settings.os
        if tools.detected_os() != self.settings.os:
            raise ConanInvalidConfiguration("Cross building not supported")
        if tools.detected_architecture() != self.settings.arch:
            raise ConanInvalidConfiguration("Cross building not supported")
        if not all((self._go_os(self.settings.os), self._go_arch(self.settings.arch))):
            raise ConanInvalidConfiguration("This recipe (or go) does not support the host os/arch")
        if not all((self._go_os(self.settings.os_target), self._go_arch(self.settings.arch_target))):
            raise ConanInvalidConfiguration("This recipe (or go) does not support the target os/arch")

    def _go_os(self, os_):
        ret = {
            "Macos": "darwin",
            "Windows": "windows",
            "Linux": "linux",
            "FreeBSD": "freebsd",
        }.get(str(os_))
        if ret is None:
            if "arm" in os_:
                ret = "arm"
        return ret

    def _go_arch(self, arch):
        ret = {
            "x86": "386",
            "x86_64": "amd64",
            "armv8": "arm",
            "armv7": "arm",
        }.get(str(arch))
        return ret

    def _build_enviroment_variables(self):
        cc, cxx = self._detect_compilers()
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.compiler in ("clang", "gcc", "apple-clang"):
            autotools.flags.append("-Wno-implicit-fallthrough")
        env = {
            "GOROOT_BOOTSTRAP": self.deps_user_info["golang"].goroot,
            "GOROOT_FINAL": str(self.package_folder),
            "GOHOSTARCH": self._go_arch(self.settings.arch),
            "GOHOSTOS": self._go_os(self.settings.os),
            "GOARCH": self._go_arch(self.settings.arch_target),
            "GOOS": self._go_os(self.settings.os_target),
            "GO_LDFLAGS": "-w" if self.settings.build_type in ("Debug", "RelWithDebInfo") else "",
            "GO_GCFLAGS": "-N -l" if self.settings.build_type == "Debug" else "",
            "CC": "{} {} {}".format(cc, autotools.vars["CPPFLAGS"], autotools.vars["CFLAGS"], "" if self.settings.os == "Windows" else "-fPIC"),
            "CC_FOR_TARGET": "{} {} {} {}".format(cc, autotools.vars["CPPFLAGS"], autotools.vars["CFLAGS"], "" if self.settings.os_target == "Windows" else "-fPIC"),  # FIXME: crossbuilding requires other compiler here
            "CXX_FOR_TARGET": "{} {} {} {}".format(cxx, autotools.vars["CPPFLAGS"], autotools.vars["CFLAGS"], "" if self.settings.os_target == "Windows" else "-fPIC"),  # FIXME: crossbuilding requires other compiler here
            "GO_DISTFLAGS": "-s" if not self.options.shared else "",
        }
        if self.options.get_safe("enable_sse2") is not None:
            env["GO386"] = "sse2" if self.options.enable_ss2 else "387"
        return env

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.mkdir(os.path.join(self.package_folder, "bin"))
        env = self._build_enviroment_variables()
        self.output.info("build environment variables: {}".format(env))
        with tools.environment_append(env):
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                script_name = "./{}.{}".format(
                    "race" if self.options.race else "make",
                    "bat" if tools.os_info.is_windows else "bash",
                )
                self.run(script_name, run_environment=True)

    @property
    def _goroot(self):
        return os.path.join(self.package_folder, "bin", "goroot")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder), dst=self._goroot)

    def package_info(self):
        self.output.info("Settings GOROOT environment variable: {}".format(self._goroot))
        self.env_info.GOROOT = self._goroot

        bin_path = os.path.join(self._goroot, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
