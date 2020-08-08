from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException
import glob
import os
import textwrap


class AceConan(ConanFile):
    name = "ace"
    description = "UNKNOWN_DESCRIPTION"
    topics = ("conan", "ACE")
    license = "UNKNOWN_LICENSES"
    homepage = "UNKNOWN_HOMEPAGE"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "unicode": [True, False],
        "ostream": [True, False],
        "multithreading": [True, False],
        "ssl": [False, "openssl"],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_lzo": [True, False],
        "with_boost": [True, False],
        "with_xerces": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "unicode": False,
        "ostream": False,
        "multithreading": True,
        "ssl": "openssl",
        "with_zlib": False,
        "with_bzip2": False,
        "with_lzo": False,
        "with_boost": False,
        "with_xerces": False,
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

    def requirements(self):
        if self.options.ssl == "openssl":
            self.requires("openssl/1.1.1g")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8@")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        if self.options.with_boost:
            self.requires("boost/1.73.0")
        if self.options.with_xerces:
            self.requires("boost/3.2.3")

    @property
    def _with_ssl(self):
        return str(self.options.ssl) != str(None)

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if tools.os_info.is_windows:
            self.build_requires("strawberryperl/xxx")
        # self.build_requires("makefile-project-workspace-creator/4.1.46")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("ACE*")[0], self._source_subfolder)

    def _write_mpc_feature_file(self):
        one_zero = lambda v: "1" if v else "0"
        contents = textwrap.dedent("""\
            ssl         = {ssl}
            openssl11   = {openssl11}
            zlib        = {zlib}
            bzip2       = {bzip2}
            lzo1        = {lzo1}
            lzo2        = {lzo2}
            boost       = {boost}
            uses_wcher  = {wchar}
            xerces      = {xerces}
            xerces2     = {xerces2}
            xerces3     = {xerces3}
            """).format(
            ssl=one_zero(self._with_ssl),
            openssl11=one_zero(self.options.ssl and self.deps_cpp_info["openssl"].version[:3] == "1.1"),
            zlib=one_zero(self.options.with_zlib),
            bzip2=one_zero(self.options.with_bzip2),
            lzo1=one_zero(self.options.with_lzo and self.deps_cpp_info["lzo"].version[:1] == "1"),
            lzo2=one_zero(self.options.with_lzo and self.deps_cpp_info["lzo"].version[:1] == "2"),
            boost=one_zero(self.options.with_boost),
            wchar=one_zero(self.options.unicode),
            xerces=one_zero(self.options.with_xerces and self.deps_cpp_info["xerces-c"].version[:1] == "1"),
            xerces2=one_zero(self.options.with_xerces and self.deps_cpp_info["xerces-c"].version[:1] == "2"),
            xerces3=one_zero(self.options.with_xerces and self.deps_cpp_info["xerces-c"].version[:1] == "3"),
        )
        tools.save(os.path.join(self._source_subfolder, "bin", "MakeProjectCreator", "config", "default.features"), contents)

    def _write_config_header(self):
        if self.settings.os == "Windows":
            suffix = "windows"
        elif tools.is_apple_os(self.settings.os):
            suffix = "macosx"
        elif self.settings.os == "Linux":
            suffix = "linux"
        elif self.settings.os == "Android":
            suffix = "android"
        else:
            get_cfg_name = lambda v: os.path.splitext(os.path.basename(v))[0].split("-", 1)[1]
            configs = [get_cfg_name(cfg) for cfg in glob.glob(os.path.join(self._source_subfolder, "ace", "config-*"))]
            raise ConanException("Don't know  what config header to use.\nConfig headers are available for: {}.".format(configs))
        tools.save(os.path.join(self._source_subfolder, "ace", "config.h"), textwrap.dedent("""\
            #pragma once
            #include "ace/config-{}.h"
            """).format(suffix))

    def _write_makeinclude(self):
        name = None
        if tools.is_apple_os(self.settings.os):
            name = "macos"
        elif self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                name = "win32_msvc"
            elif self.settins.compiler == "gcc":
                name = "mingw32"
        elif self.settings.os == "Linux":
            name = "linux"
        if name is None:
            get_cfg_name = lambda v: os.path.splitext(os.path.basename(v))[0].split("-", 1)[1]
            platforms = [get_cfg_name(cfg) for cfg in glob.glob(os.path.join(self._source_subfolder, "include", "makeinclude", "platform_*.GNU"))]
            raise ConanException("Don't know what makeinclude to use.\nIncludes available for: {}.".format(platforms))

        one_zero = lambda v: "1" if v else "0"
        autotools = AutoToolsBuildEnvironment(self)
        autotools_vars = autotools.vars
        tools.save(os.path.join(self._source_subfolder, "include", "makeinclude", "platform_macros.GNU"),
                                textwrap.dedent("""\
                                    buildbits           := {buildbits}
                                    ssl                 := {ssl}
                                    threads             := {threads}
                                    shared_libs_only    := {shared_only} 
                                    static_libs_only    := {static_only} 
                                    debug               := {debug}
                                    
                                    AR                  := {AR}
                                    CC                  := {CC}
                                    CXX                 := {CXX}
                                    RC                  := {RC}
                                    CPPFLAGS            := {CPPFLAGS}
                                    CFLAGS              := {CFLAGS}
                                    CCFLAGS             := {CXXFLAGS}
                                    DFLAGS              :=
                                    DCCFLAGS            :=
                                    DLD                 := {DLD}
                                    LD                  := {LD}
                                    LDFLAGS             := {LDFLAGS}
                                    IDL                 := {IDL}
                                    
                                    INSTALL_PREFIX      := {prefix}
                                    INSINC              := {incdir}
                                    INSLIB              := {libdir}
                                    INSBIN              := {bindir}
                                    INSMAN              := {mandir}
                                    
                                    include $(ACE_ROOT)/include/makeinclude/platform_{platformname}.GNU
                                    """).format(
                                    buildbits={"x86_64": 64, "x86": 32}.get(str(self.settings.arch), ""),
                                    ssl=one_zero(self._with_ssl),
                                    threads=one_zero(self.options.multithreading),
                                    shared_only="1" if self.options.shared else "",
                                    static_only="1" if not self.options.shared else "",
                                    debug=one_zero(self.settings.build_type in ("Debug", "RelWithDebInfo")),
                                    AR=tools.get_env("AR", "ar"),
                                    CC=tools.get_env("CC", "cc"),
                                    CXX=tools.get_env("CXX", "c++"),
                                    RC=tools.get_env("RC", ""),
                                    CPPFLAGS=autotools.vars["CPPFLAGS"],
                                    CFLAGS=autotools_vars["CFLAGS"],
                                    CXXFLAGS=autotools_vars["CXXFLAGS"],
                                    RCFLAGS=tools.get_env("RCFLAGS", ""),
                                    DLD=tools.get_env("LD", "ld"),
                                    LD=tools.get_env("LD", "ld"),
                                    LDFLAGS=autotools_vars["LDFLAGS"],
                                    IDL=tools.get_env("IDL", "idl"),
                                    INSBIN=tools.get_env("IDL", "idl"),
                                    prefix=self.package_folder.replace("\\", "/"),
                                    bindir=os.path.join(self.package_folder, "bin").replace("\\", "/"),
                                    libdir=os.path.join(self.package_folder, "lib").replace("\\", "/"),
                                    incdir=os.path.join(self.package_folder, "include").replace("\\", "/"),
                                    mandir=os.path.join(self.package_folder, "share", "man").replace("\\", "/"),
                                    platformname=name,
                                ))

    def build(self):
        self._write_mpc_feature_file()
        self._write_config_header()
        self._write_makeinclude()
        mwc_args = [
            "perl", os.path.join(self._source_subfolder, "bin", "mwc.pl"),
            "-type", "nmake" if self.settings.compiler == "Visual Studio" else "gnuace",
        ]
        if not self.options.shared:
            mwc_args.append("-static")

        mpc_env = {
            "ACE_ROOT": os.path.join(self.source_folder, self._source_subfolder).replace("\\", "/"),
        }
        if self.options.ssl == "openssl":
            mpc_env["OPENSSL_ROOT"] = self.deps_cpp_info["openssl"].rootpath.replace("\\", "/")
        with tools.environment_append(mpc_env):
            self.run(" ".join(mwc_args), run_environment=True)

        if self.settings.compiler == "Visual Studio":
            pass
        else:
            with tools.chdir(self._source_subfolder):
                with tools.environment_append(mpc_env):
                    autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                    autotools.make(target="ACE")

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        # os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libACE.la")))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["ACE"]
