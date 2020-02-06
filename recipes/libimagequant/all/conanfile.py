from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class Libimagequant(ConanFile):
    name = "libimagequant"
    license = ("GPL-v3-or-later", "BSD-2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pngquant.org/lib"
    description = "Small, portable C library for high-quality conversion of RGBA images to 8-bit indexed-color (palette) images."
    topics = ("conan", "png", "compressor", "lossy")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_sse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_sse": True,
    }

    generators = "cmake"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.enable_sse

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pngquant-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
            self.build_requires("automake/1.16.1")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, tools.os_info.is_windows)
        conf_args = [
            "--includedir={}".format(os.path.join(self.package_folder, "include")),
            "--libdir={}".format(os.path.join(self.package_folder, "lib")),
        ]
        if self.settings.arch in ("x86", "x86_64"):
            conf_args.append("--enable-sse" if self.options.enable_sse else "--disable-sse")
        self._autotools.configure(args=conf_args)
        return self._autotools

    @contextmanager
    def _build_context(self):
        with tools.chdir(os.path.join(self._source_subfolder, "lib")):
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    automake_bin = str(self.deps_cpp_info["automake"].rootpath)
                    automake_scriptdir = os.path.join(automake_bin, "bin", "share", "automake-1.16")
                    cc = tools.unix_path(os.path.join(automake_scriptdir, "compile"))
                    ar = tools.unix_path(os.path.join(automake_scriptdir, "ar-lib"))

                    with tools.environment_append({"CC": "sh {} cl -nologo".format(cc), "AR": "sh {} lib".format(ar), "LD": "link"}):
                        yield
            else:
                yield

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            tools.patch(patch_file="patches/0001-add-msvc-dll-support.patch", base_path=self._source_subfolder)

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            if self.settings.os == "Windows":
                target = "dll" if self.options.shared else "static"
            else:
                target = "shared" if self.options.shared else "static"
            autotools.make(target=target)

    def package(self):
        builddir = os.path.join(self._source_subfolder, "lib")

        self.copy("COPYRIGHT", src=builddir, dst="licenses")

        self.copy("libimagequant.h", src=builddir, dst="include")
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy("imagequant.dll", src=builddir, dst="bin")

                implib = "imagequant_dll.a"
                self.copy(implib, src=builddir, dst="lib")
                if self.settings.compiler == "Visual Studio":
                    newimplib = "imagequant_dll.lib"
                else:
                    newimplib = "libimagequant_dll.a"
                os.rename(os.path.join(self.package_folder, "lib", implib),
                          os.path.join(self.package_folder, "lib", newimplib))
            else:
                self.copy("libimagequant.a", src=builddir, dst="lib")
                if self.settings.compiler == "Visual Studio":
                    os.rename(os.path.join(self.package_folder, "lib", "libimagequant.a"),
                              os.path.join(self.package_folder, "lib", "imagequant.lib"))
        else:
            if self.options.shared:
                libext = "dylib" if self.settings.os == "Macos" else "so"
            else:
                libext = "a"
            self.copy("libimagequant.{}".format(libext), src=builddir, dst="lib")

    def package_info(self):
        if self.settings.os == "Windows" and self.options.shared:
            lib = "imagequant_dll"
        else:
            lib = "imagequant"

        self.cpp_info.libs = [lib]

        if self.settings.os != "Windows":
            self.cpp_info.system_libs = ["m"]
