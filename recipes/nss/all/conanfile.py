from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class NssConan(ConanFile):
    name = "nss"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    description = "Network Security Services (NSS) is a set of libraries designed to support cross-platform development of security-enabled server applications"
    topics = ("conan", "nss", "security")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "MPL-2.0"
    generators = "pkg_config"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "nss-{}".format(self.version)
        tools.rename(os.path.join(extracted_dir, "nss"), self._source_subfolder)
        tools.rmdir(extracted_dir)

    def build_requirements(self):
        # self.build_requires("gyp_installer/20190821@bincrafters/stable")
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("meson/0.56.0")
        # if tools.os_info.is_windows:
        #     self.build_requires("make/4.2.1")

    def requirements(self):
        self.requires("nspr/4.29")
        self.requires("sqlite3/3.34.0")

    def _nss_arch(self, arch):
        arch = str(arch)
        try:
            return {
                "x86": "ia32",
                "x86_64": "x64",
                "armv8": "aarch64",
                "sparcv9": "sparc64",
                "mips": "mips",
                "mips64": "mips64",
            }[arch]
        except KeyError:
            if arch.startswith("arm"):
                return "arm"
            raise ConanInvalidConfiguration("Unsupported architecture: {}".format(arch))

    def _nss_os(self, os):
        os = str(os)
        if os == "Windows":
           return {
                "win95": "WIN95",
                "winnt": "WINNT",
            }[self.options["nspr"].win32_target]
        else:
            try:
                {
                    "Linux": "Linux",
                    "Macos": "Darwin",
                    "Android": "Android",
                    "SunOS": "SunOS",
                    "FreeBSD": "FreeBSD",
                }[os]
            except KeyError:
                raise ConanInvalidConfiguration("Unsupported os")

    def _configure_gyp(self):
        with tools.environment_append({"PKG_CONFIG_PATH": self.install_folder}):
            sqlite_libs = tools.PkgConfig("sqlite3").libs

        gyp_args = [
            "gyp",
            "-f", "ninja",
            "--depth", self._source_subfolder,
            "--generator-output", self.build_folder,
            "-Duse_system_sqlite=1",
            "-Dsqlite_libs={}".format(" ".join(sqlite_libs)),
            "-Dpython={}".format("python2"),  # FIXME: gyp does not support python3!! sys.executable),
            "-Dstatic_libs={}".format(0 if self.options.shared else 1),
            "-Dstandalone_static_library={}".format(0 if self.options.shared else 1),
            "-Dtarget_arch={}".format(self._nss_arch(self.settings.arch)),
            "-Dnspr_lib_dir={}".format(self.deps_cpp_info["nspr"].libdirs[0]),
            "-Dnspr_include_dir={}".format(self.deps_cpp_info["nspr"].includedirs[0]),
            "-Dnss_dist_obj_dir={}".format(os.path.join(self.package_folder)),
            "-Dhost_arch={}".format(self._nss_arch(self.settings.arch)),
            "-Ddisable_tests=1",
            "-Dnss_dist_dir={}".format(self.package_folder),
            "-Denable_sslkeylogfile={}".format(0),
            "-Dnspr_include_dir={}".format(self.deps_cpp_info["nspr"].include_paths[1]),
            os.path.join(self.source_folder, self._source_subfolder, "nss.gyp"),
        ]
        self.run(" ".join('"{}"'.format(a) for a in gyp_args), run_environment=True)

    def build(self):
        self._configure_gyp()
        autotools = AutoToolsBuildEnvironment(self)
        with tools.environment_append(autotools.vars):
            with tools.chdir(os.path.join(self._source_subfolder, "out", "Release")):
                self.run("ninja", run_environment=True)

    def package(self):
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.TOC")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.chk")
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.mkdir(os.path.join(self.package_folder, "include"))
        shutil.move(os.path.join(self.package_folder, "private"),
                    os.path.join(self.package_folder, "include", "private"))
        shutil.move(os.path.join(self.package_folder, "public"),
                    os.path.join(self.package_folder, "include", "public"))

    def package_info(self):
        print(dir(self.cpp_info))
        self.cpp_info.includedirs = [os.path.join("include", "public"), os.path.join("include", "public", "nss")]
        self.cpp_info.names["pkg_config"] = "nss"
        self.cpp_info.libs = ["ssl3", "smime3", "nss3", "nssutil3"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
