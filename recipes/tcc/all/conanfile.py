from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import glob
import os


class TccConan(ConanFile):
    name = "tcc"
    description = "Compile and execute C code everywhere, for example on rescue disks"
    topics = ("conan", "tcc", "compiler", "c", "tinycc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bellard.org/tcc/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_selinux": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_selinux": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.1")
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_selinux

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("tinycc-*")[0], self._source_subfolder)

    @property
    def _libtcc_path(self):
        return os.path.join(self.package_folder, "bin", "libtcc")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--disable-static" if self.options.shared else "--enable-static",
            "--cpu={}".format(self.settings.arch),
            "--bindir={}/bin".format(tools.unix_path(self.package_folder)),
            "--tccdir={}".format(tools.unix_path(self._libtcc_path)),
            "--libdir={}/lib".format(tools.unix_path(self.package_folder)),
            "--disable-rpath",
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        if self.options.get_safe("with_selinux"):
            conf_args.append("--with-selinux")
        if tools.get_env("CC"):
            conf_args.append("--cc={}".format(tools.unix_path(tools.get_env("CC"))))
        if tools.get_env("AR"):
            conf_args.append("--ar={}".format(tools.unix_path(tools.get_env("AR"))))
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, build=False, host=False)
        return self._autotools

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(self.deps_user_info["automake"].ar_lib),
                    "CC": "{} cl -nologo".format(self.deps_user_info["automake"].compile),
                    "CXX": "{} cl -nologo".format(self.deps_user_info["automake"].compile),
                    "LD": "link",
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

    @property
    def _tcc_targetos(self):
        if tools.is_apple_os(self.settings.os):
            return "Darwin"
        elif self.settings.os == "Windows":
            return "MINGW"
        elif "BSD" in str(self.settings.os):
            return str(self.settings.os)
        else:
            return str(self.settings.os)

    def _patch_sources(self):
        configure = os.path.join(self._source_subfolder, "configure")
        makefile = os.path.join(self._source_subfolder, "Makefile")
        os.chmod(configure, 0o755)
        tools.replace_in_file(configure, "targetos=`uname`", "targetos={}".format(self._tcc_targetos))
        if self.settings.compiler == "Visual Studio":
            shared_linker = "link -DLL -OUT:"
            implib_arg = "-IMPLIB:$@.lib"
        else:
            shared_linker = "$(CC) -shared -o "
            implib_arg = "-Wl,--out-implib,$@.a"
        tools.replace_in_file(makefile,
                              "$(CC) -shared -o $@ $^ $(LDFLAGS)",
                              "{}$@ $^ $(LDFLAGS) {}".format(shared_linker, implib_arg))
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(makefile,
                                  "tcc.dll : $(LIBTCC_OBJ)",
                                  "tcc.dll.lib : tcc.dll\n"
                                  "tcc.dll : $(LIBTCC_OBJ)")
            tools.replace_in_file(makefile,
                                  "tcc$(EXESUF): tcc.o $(LIBTCC)",
                                  "tcc$(EXESUF): tcc.o $(LIBTCC){}".format(".lib" if self.options.shared else ""))
            tools.replace_in_file(makefile,
                                  "libtcc$(DLLSUF)", "tcc$(DLLSUF)")
            tools.replace_in_file(makefile,
                                  "libtcc.def", "tcc.def")
            tools.replace_in_file(configure,
                                  "OPT1=", "OPT1="" #")
            tools.replace_in_file(configure,
                                  "OPT2=", "OPT2="" #")
            tools.replace_in_file(makefile,
                                  ".o", ".obj")
            tools.replace_in_file(makefile,
                                  "libtcc.a", "tcc.lib")
            tools.replace_in_file(makefile,
                                  "libtcc.dll", "tcc.dll")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        if self.settings.os == "Windows":
            tools.mkdir(os.path.join(self.package_folder, "include"))
            os.rename(os.path.join(self.package_folder, "lib", "libtcc.h"),
                      os.path.join(self.package_folder, "include", "libtcc.h"))
        if self.options.shared:
            if self.settings.compiler == "Visual Studio":
                self.copy("tcc.dll.lib", src=self.build_folder, dst="lib")
            else:
                self.copy("libtcc.dll.a", src=self.build_folder, dst="lib")
        tools.rmdir(os.path.join(self._libtcc_path, "doc"))
        tools.rmdir(os.path.join(self._libtcc_path, "examples"))
        tools.rmdir(os.path.join(self._libtcc_path, "share"))

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        libtcc = "tcc"
        if self.settings.os == "Windows" and self.options.shared:
            libtcc += ".dll"
            if self.settings.compiler == "Visual Studio":
                libtcc += ".lib"
            else:
                libtcc += ".a"
        self.cpp_info.libs = [libtcc]
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.extend(["dl", "pthread"])

        self.output.info("Settings TCCLIB_PATH environment variable: {}".format(self._libtcc_path))
        self.env_info.TCCLIB_PATH = self._libtcc_path
