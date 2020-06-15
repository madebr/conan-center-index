from conans import AutoToolsBuildEnvironment, ConanFile, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import glob
import os


class YosysConan(ConanFile):
    name = "yosys"
    description = "framework for RTL synthesis tools"
    topics = ["conan", "yosys", "rtl", "synthesis", "fpga", "verific", "verification", "simulation"]
    homepage = "http://www.clifford.at/yosys/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "ISC"
    options = {
        "enable_cover": [True, False],
        "enable_glob": [True, False],
        "enable_plugins": ["auto", True, False],  # FIXME: not supported on Windows due to dlfcn
        "with_line_history": ["auto", "readline", "editline", "False"],
        "with_python": [True, False],
        "with_tcl": [True, False],
        "with_zlib": [True, False],
    }
    settings = "os", "compiler", "build_type", "arch"
    default_options = {
        "enable_cover": True,
        "enable_glob": True,
        "enable_plugins": "auto",
        "with_line_history": "auto",
        "with_python": True,
        "with_tcl": True,
        "with_zlib": True,
    }
    generators = "pkg_config"
    exports_sources = "CMakeLists.txt", "patches/**"

    _autotools = None

    @property
    def _with_line_history(self):
        if self.options.with_line_history == "auto":
            if self.settings.compiler == "Visual Studio":
                return False
            return "readline"
        return self.options.with_line_history

    @property
    def _enable_plugins(self):
        if self.options.enable_plugins == "auto":
            if self.settings.os == "Windows":
                return False
            return True
        return self.options.enable_plugins

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.arch in ("asm.js", "wasm") and self._enable_plugins:
            raise ConanInvalidConfiguration("asm configuration do not support plugins")

    # FIXME: remove this once cxxrtl issue is gone
    _with_conan_dependencies = False #True

    def requirements(self):
        if self._with_conan_dependencies:
            self.requires("abc/cci.20200605")
            # self.requires("abc/cci.yosys.20200430")
            self.requires("libffi/3.3")
            if self._with_line_history == "editline":
                self.requires("editline/3.1")
            if self._with_line_history == "readline":
                self.requires("readline/8.0")
            if self.options.with_python:
                self.requires("boost/1.73.0")
                self.requires("cpython/3.8.3")
            if self.options.with_tcl:
                self.requires("tcl/8.6.10")
            if self.options.with_zlib:
                self.requires("zlib/1.2.11")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self._with_conan_dependencies:
            if tools.os_info.is_windows:
                self.build_requires("winflexbison/2.5.22")
            else:
                self.build_requires("bison/3.5.3")
                self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("yosys-*")[0], self._source_subfolder)

    @property
    def _make_config(self):
        if self.settings.compiler == "gcc":
            if self.settings.os == "Windows":
                return {
                    "x86": "msys2",
                    "x86-64": "msys2-64",
                }[str(self.settings.arch)]
            return "gcc"
        if "clang" in str(self.settings.compiler):
            return "clang"
        if self.settings.arch in ("asm.js", "wasm"):
            return "emcc"
        return "none"

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    @property
    def _make_args(self):
        zero_one = lambda o : "1" if o else "0"
        make_args = [
            "CONFIG={}".format(self._make_config),
            # "ENABLE_LIBYOSYS={}".format(zero_one(True)),
            # "ENABLE_COVER={}".format(zero_one(self.options.enable_cover)),
            # "ENABLE_EDITLINE={}".format(zero_one(self._with_line_history == "editline")),
            # "ENABLE_GLOB={}".format(zero_one(self.options.enable_cover)),
            # "ENABLE_READLINE={}".format(zero_one(self._with_line_history == "readline")),
            # "ENABLE_PYSOSYS={}".format(zero_one(self.options.with_python)),
            # "ENABLE_TCL={}".format(zero_one(self.options.with_tcl)),
            # "ENABLE_ZLIB={}".format(zero_one(self.options.with_zlib)),
            # "ENABLE_DEBUG={}".format(zero_one(self.settings.build_type == "Debug")),
            # "ENABLE_NDEBUG={}".format(zero_one(self.settings.build_type != "Debug")),
            # "ENABLE_PLUGINS={}".format(zero_one(self._enable_plugins)),
            "LDLIBS={}".format(" ".join("-l{}".format(lib) for lib in self._autotools.libs)),
            "PREFIX={}".format(self.package_folder.replace("\\", "/")),
            "LIBDIR={}".format(os.path.join(self.package_folder, "lib").replace("\\", "/")),
            "DATDIR={}".format(self._datarootdir.replace("\\", "/")),
        ]
        if self._with_conan_dependencies:
            # FIXME: merge with list above
            make_args.extend([
                "ABCEXTERNAL={}".format(os.path.join(self.deps_user_info["abc"].ABC.replace("\\", "/"))),
                "ENABLE_ABC={}".format(zero_one(True)),
            ])
        if self.settings.os == "Windows":
            make_args.append("EXE=.exe")
        if self.settings.arch in ("asm.js", "wasm"):
            make_args.extend([
                "DISABLE_SPAWN=1",
                "DISABLE_ABC_THREADS=1",
            ])
        return make_args

    @contextmanager
    def _build_context(self, autotools):
        env = {}
        if self._with_conan_dependencies:
            env["LDLIBS"] = autotools.vars["LIBS"]
        context = tools.no_op()
        if self.settings.compiler == "Visual Studio":
            context = tools.vcvars(self.settings)
            env.update({
                "CC": os.path.join(self.build_folder, self._source_subfolder, "msvc_compile.sh").replace("\\", "/"),
                "CXX": os.path.join(self.build_folder, self._source_subfolder, "msvc_compile.sh").replace("\\", "/"),
                "LD": os.path.join(self.build_folder, self._source_subfolder, "msvc_link.sh").replace("\\", "/"),
                "AR": os.path.join(self.build_folder, self._source_subfolder, "msvc_lib.sh").replace("\\", "/"),
                "STRIP": ":",
            })
        with tools.environment_append(env):
            with context:
                yield

    @property
    def _libcxx(self):
        return {
            "libstdc++": "stdc++",
            "libstdc++11": "stdc++",
            "libc++": "c++",
        }[str(self.settings.compiler.libcxx)]

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            self._autotools.link_flags.append("-subsystem:console")
            self._autotools.defines.extend(["UNICODE", "_UNICODE", "_CRT_SECURE_NO_WARNINGS", "WIN32", "_CONSOLE", "_LIB"])
        else:
            self._autotools.libs.append(self._libcxx)
        if self.settings.os == "Linux":
            self._autotools.libs.append("m")
        if self.settings.os == "Windows":
            self._autotools.libs.append("user32")
        if not self._with_conan_dependencies:
            if self._with_line_history == "readline":
                self._autotools.libs.extend(["history", "readline"])
            if self.options.with_zlib:
                self._autotools.libs.append("z")
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self._with_conan_dependencies:
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"),
                                  " -lz", "")
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"),
                                  "$(shell PKG_CONFIG_PATH=$(PKG_CONFIG_PATH) $(PKG_CONFIG) --silence-errors --libs tcl || echo -l$(TCL_VERSION))", "")
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"),
                                  "$(LD) -o libyosys.so",
                                  "$(AR) -o libyosys.so")
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                prefix = ""
                suffix = "lib"
            else:
                prefix = "lib"
                suffix = "a"
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile"),
                                  "libyosys.so", "{}yosys.{}".format(prefix, suffix))

    def build(self):
        self._patch_sources()
        # FIXME: how to check that build requirement cpython and (host) requirement are the same version?
        # if self.options.with_python:
        #     if self.options["boost"].without_python:
        #         raise ConanInvalidConfiguration("This package needs boost with python support")
        autotools = self._configure_autotools()
        with self._build_context(autotools):
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(RunEnvironment(self).vars):
                    autotools.make(args=self._make_args)
        # except:
        #     print("OOPS! AN ERROR OCCURRED!")
        # with self._build_context():
        #     with tools.chdir(self._source_subfolder):
        #         with tools.environment_append(RunEnvironment(self).vars):
        #             with tools.environment_append(autotools.vars):
        #                 os.system("bash")

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        with self._build_context(autotools):
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(RunEnvironment(self).vars):
                    autotools.install(args=self._make_args)
        os.rename(os.path.join(self._datarootdir, "include"), os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.options.with_line_history = self._with_line_history

    def package_info(self):
        self.cpp_info.libs = ["yosys"]
        self.cpp_info.defines.extend(["_YOSYS_", "YOSYS_ENABLE_ABC", "YOSYS_ENABLE_ZLIB"])
        if self.options.with_tcl:
            self.cpp_info.defines.append("YOSYS_ENALE_TCL")
        if self._enable_plugins:
            self.cpp_info.defines.append("YOSYS_ENABLE_PLUGINS")
        if self.options.with_python:
            self.cpp_info.defines.append("WITH_PYTHON")
        if self.options.enable_cover:
            self.cpp_info.defines.append("YOSYS_ENABLE_COVER")
        if self.options.enable_glob:
            self.cpp_info.defines.append("YOSYS_ENABLE_GLOB")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
