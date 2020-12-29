from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import glob
import os


class GraphvizConan(ConanFile):
    name = "graphviz"
    description = "Graphviz is open source graph visualization software. Graph visualization is a way of representing structural information as diagrams of abstract graphs and networks."
    topics = ("conan", "graphviz")
    license = "UNKNOWN_LICENSES"
    homepage = "https://graphviz.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/**"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_ondemand_plugins": [True, False],
        "with_lua": [True, False],
        "with_python": [True, False],
        "with_tcl": [True, False],
        "with_pango": [True, False],
        "with_visio": [True, False],
        "with_expat": [True, False],
        "with_webp": [True, False],
        "with_fontconfig": [True, False],
        "with_freetype": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_ondemand_plugins": True,
        "with_lua": False,
        "with_python": False,
        "with_tcl": False,
        "with_pango": False,
        "with_visio": False,
        "with_expat": False,
        "with_webp": False,
        "with_fontconfig": False,
        "with_freetype": False,
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
        if not self.options.with_webp:
            # fontconfig and freetype are not used in some configurations.
            # FIXME: this list is not complete as not all dependencies are available!!
            # They are probably only required when rasterizing the outputs.
            del self.options.with_fontconfig
            del self.options.with_freetype
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.enable_ondemand_plugins:
            self.requires("libtool/2.4.6")
        if self.options.with_python:
            self.requires("cpython/3.9.0")
        if self.options.with_lua:
            self.requires("lua/5.4.1")
        if self.options.with_tcl:
            self.requires("tcl/8.6.10")
        if self.options.with_pango:
            # FIXME: missing pango recipe
            raise ConanInvalidConfiguration("pango is not (yet) available on CCI")
        if self.options.with_expat:
            self.requires("expat/2.2.9")
        if self.options.with_webp:
            self.requires("libwebp/1.1.0")
        if self.options.get_safe("with_freetype"):
            self.requires("freetype/2.10.4")
        if self.options.get_safe("with_fontconfig"):
            self.requires("fontconfig/2.13.91")

    @property
    def _with_swig(self):
        return any((self.options.with_lua, self.options.with_python, self.options.with_tcl))

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.3")
        if self._with_swig:
            self.build_requires("swig/4.0.1")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("graphviz-*")[0], self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {
            "PS2PDF": ":",
        }
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
        self._autotools.include_paths = []
        self._autotools.libs = []
        yes_no = lambda x: "yes" if x else "no"
        python_opts = {
            "2": False,
            "3": False,
        }
        if self.options.with_python:
            python_opts[str(tools.Version(self.deps_cpp_info["cpython"].version).major)] = True
        # Options
        conf_args = [
            "--with-expat={}".format(yes_no(self.options.with_expat)),
            "--with-freetype2={}".format(yes_no(self.options.get_safe("with_freetype"))),
            "--with-fontconfig={}".format(yes_no(self.options.get_safe("with_fontconfig"))),
        ]
        # Plugin libraries
        conf_args.extend([
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-devil={}".format(yes_no(False)),
            "--with-webp={}".format(yes_no(self.options.with_webp)),
            "--with-poppler={}".format(yes_no(False)),
            "--with-ghostscript={}".format(yes_no(False)),
            "--with-rsvg={}".format(yes_no(False)),
            "--with-visio={}".format(yes_no(self.options.with_visio)),
            "--with-pangocairo={}".format(yes_no(self.options.with_pango)),
            "--with-lasi={}".format(yes_no(False)),
            "--with-glitz={}".format(yes_no(False)),
            "--with-gdk={}".format(yes_no(False)),
            "--with-gdk-pixbuf={}".format(yes_no(False)),
            "--with-gtk={}".format(yes_no(False)),
            "--with-gtkgl={}".format(yes_no(False)),
            "--with-gtkglext={}".format(yes_no(False)),
            "--with-gts={}".format(yes_no(False)),
            "--with-ann={}".format(yes_no(False)),
            "--with-glade={}".format(yes_no(False)),
            "--with-ming={}".format(yes_no(False)),
            "--with-qt={}".format(yes_no(False)),
            "--with-quartz={}".format(yes_no(False)),
            "--with-libgd={}".format(yes_no(False)),
            "--with-glut={}".format(yes_no(False)),
            "--with-sfdp={}".format(yes_no(False)),
            "--with-smyrna={}".format(yes_no(False)),
            "--with-ortho={}".format(yes_no(False)),
            "--with-digcola={}".format(yes_no(False)),
            "--with-ipsepcola={}".format(yes_no(False)),
            "--with-x={}".format(yes_no(False)),
            "--with-zlibdir={}".format(self.deps_cpp_info["zlib"].lib_paths[0].replace("\\", "/")),
            "--with-zincludedir={}".format(self.deps_cpp_info["zlib"].include_paths[0].replace("\\", "/")),
            "--enable-ltdl={}".format(yes_no(self.options.enable_ondemand_plugins)),
        ])
        # Language extensions
        conf_args.extend([
            "--enable-swig={}".format(yes_no(self._with_swig)),
            "--enable-python2={}".format(yes_no(python_opts["2"])),
            "--enable-python3={}".format(yes_no(python_opts["3"])),
            "--enable-lua={}".format(yes_no(self.options.with_lua)),
            "--enable-tcl={}".format(yes_no(self.options.with_tcl)),
        ])

        if self.options.with_expat:
            conf_args.extend([
                "--with-expatincludedir={}".format(self.deps_cpp_info["expat"].include_paths[0].replace("\\", "/")),
                "--with-expatlibdir={}".format(self.deps_cpp_info["expat"].lib_paths[0].replace("\\", "/")),
            ])

        def gather_dep_cflags_ldflags(optname):
            cflags = ["-D{}".format(define) for define in self.deps_cpp_info[optname].defines] \
                + ["-I{}".format(include) for include in self.deps_cpp_info[optname].include_paths] \
                + [flag for flag in self.deps_cpp_info[optname].cflags] \

            ldflags = ["-L{}".format(libdir) for libdir in self.deps_cpp_info[optname].lib_paths] \
                + ["-l{}".format(lib) for lib in self.deps_cpp_info[optname].libs] \
                + ["-l{}".format(lib) for lib in self.deps_cpp_info[optname].system_libs]
            return " ".join(cflags), " ".join(ldflags)

        extra_env = {}

        if self.options.with_webp:
            extra_env["WEBP_CFLAGS"], extra_env["WEBP_LIBS"] = gather_dep_cflags_ldflags("libwebp")
        if self.options.get_safe("with_freetype"):
            extra_env["FREETYPE_CFLAGS"], extra_env["FREETYPE_LIBS"] = gather_dep_cflags_ldflags("freetype")
        if self.options.get_safe("with_fontconfig"):
            extra_env["FONTCONFIG_CFLAGS"], extra_env["FONTCONFIG_LIBS"] = gather_dep_cflags_ldflags("fontconfig")

        with tools.environment_append(extra_env):
            self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            with tools.environment_append({"AUTOMAKE_CONAN_INCLUDES": tools.get_env("AUTOMAKE_CONAN_INCLUDES", "").replace(";", ":")}):
                self.run("./autogen.sh NOCONFIG", win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _libs(self):
        return ["cdt", "cgraph", "gvc", "gvpr", "lab_gamut", "pathplan", "xdot"]

    @property
    def _plugins(self):
        plugins = []
        if self.options.with_pango:
            plugins.append("pango")
        if self.options.with_webp:
            plugins.append("webp")
        plugins.extend(["dot_layout", "neato_layout", "core"])
        return plugins

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        for lib in self._libs:
            os.unlink(os.path.join(self.package_folder, "lib", "lib{}.la".format(lib)))
            if self.settings.os == "Windows" and not self.options.shared:
                lib_header = os.path.join(self.package_folder, "include", "graphviz", "{}.h".format(lib))
                if not os.path.isfile(lib_header):
                    continue
                tools.replace_in_file(lib_header,
                                      "#ifdef _WIN32\n#   ifdef EXPORT_",
                                      "#if 0\n#   ifdef EXPORT_")
        for plugin in self._plugins:
            os.unlink(os.path.join(self.package_folder, "lib", "graphviz", "libgvplugin_{}.la".format(plugin)))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    @property
    def _dot(self):
        if self.options.shared:
            if self.options.enable_ondemand_plugins:
                return "dot"
            else:
                return "dot_builtins"
        else:
            return "dot_static"

    def package_info(self):
        for libname in self._libs:
            self.cpp_info.components[libname].libs = [libname]
            self.cpp_info.components[libname].names["pkg_config"] = "lib{}".format(libname)

        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["cdt"].system_libs = ["pthread"]

        self.cpp_info.components["cgraph"].requires = ["cdt"]

        self.cpp_info.components["gvc"].requires = ["xdot", "cgraph", "cdt", "pathplan", "zlib::zlib"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["gvc"].system_libs = ["m"]

        if self.options.enable_ondemand_plugins:
            self.cpp_info.components["cdt"].requires.append("libtool::libtool")

        if self.options.with_expat:
            self.cpp_info.components["cdt"].requires.append("expat::expat")

        self.cpp_info.components["gvpr"].requires = ["cdt", "cgraph"]

        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["gvpr"].system_libs = ["m"]

        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["pathplan"].system_libs = ["m"]

        plugin_name = lambda name: "plugin_{}".format(name)

        for plugin in self._plugins:
            self.cpp_info.components[plugin_name(plugin)].libs = ["gvplugin_{}".format(plugin)]
            self.cpp_info.components[plugin_name(plugin)].libdirs = [os.path.join("lib", "graphviz")]

        if self.options.with_webp:
            self.cpp_info.components[plugin_name("webp")].requires = ["libwebp::libwebp"]
            if self.options.with_fontconfig:
                self.cpp_info.components[plugin_name("webp")].requires.append("fontconfig::fontconfig")
            if self.options.with_freetype:
                self.cpp_info.components[plugin_name("webp")].requires.append("freetype::freetype")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        dot_bin = os.path.join(bin_path, self._dot)
        self.output.info("Setting DOT environment variable: {}".format(dot_bin))
        self.env_info.DOT = dot_bin
