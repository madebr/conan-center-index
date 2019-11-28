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
    }
    default_options = {
        "shared": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "nss-{}".format(self.version)
        os.rename(os.path.join(extracted_dir, "nss"), self._source_subfolder)
        os.rmdir(extracted_dir)

    def build_requirements(self):
        # self.build_requires("gyp_installer/20190821@bincrafters/stable")
        if tools.os_info.is_windows:
            self.build_requires("make/4.2.1")

    def requirements(self):
        self.requires("nspr/4.23")
        self.requires("sqlite3/3.30.1")

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
        gyp_args = [
            "gyp",
            "-f", "ninja",
            "--depth", self._source_subfolder,  #".",
            "--generator-output", self.build_folder,
            "-Dpython={}".format("python2"),  # FIXME: gyp does not support python3!! sys.executable),
            "-Dstatic_libs={}".format(1 if self.options.shared else 0),
            "-Dstandalone_static_library={}".format(0 if self.options.shared else 1),
            "-Dtarget_arch={}".format(self._nss_arch(self.settings.arch)),
            "-Dnspr_lib_dir={}".format(self.deps_cpp_info["nspr"].libdirs[0]),
            "-Dnspr_include_dir={}".format(self.deps_cpp_info["nspr"].includedirs[0]),
            "-Dnss_dist_obj_dir={}".format(os.path.join(self.package_folder, "lib", "fff")),
            # "-Dhost_arch={}".format(self._nss_arch(tools.detected_architecture())),
            "-Ddisable_tests=1",
            "-Dnss_dist_dir={}".format(self.package_folder),
            "-Denable_sslkeylogfile={}".format(0),
            os.path.join(self.source_folder, self._source_subfolder, "nss.gyp"),
        ]
        self.run(" ".join('"{}"'.format(a) for a in gyp_args))

    def builda(self):
        self._configure_gyp()
        autotools = AutoToolsBuildEnvironment(self)
        with tools.environment_append(autotools.vars):
            with tools.chdir(os.path.join(self._source_subfolder, "out", "Release")):
                self.run("ninja")

    def build2(self):
        args = [
            os.path.join(self._source_subfolder, "build.sh"),
            "-j", tools.cpu_count(),
            "-t", self._nss_arch(self.settings.arch),
            "--disable-tests",
            "--system-nspr",  # -nspr={}:{}".format(self.deps_cpp_info["nspr"].include_paths[-1], self.deps_cpp_info["nspr"].lib_paths[-1]),
            "--system-sqlite",
            "-Dstatic_libs={}".format(1 if self.options.shared else 0),
            "-Ddisable_werror=1",
            "-Dsign_libs=0",
            "-Dlibrary={}".format("shared_library" if self.options.shared else "static_library")
        ]
        if self.settings.build_type != "Debug":
            args.append("--opt")
        if not self.options.shared:
            args.append("--static")
        if self.settings.compiler == "gcc":
            args.append("--gcc")
        elif self.settings.compiler == "clang":
            args.append("--clang")
        elif self.settings.compiler == "Visual Studio":
            args.append("--msvc")
        else:
            raise ConanInvalidConfiguration("Unsupported compiler")
        autotools = AutoToolsBuildEnvironment(self)

        with tools.environment_append(autotools.vars):
            self.run(" ".join('"{}"'.format(a) for a in args))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        build_environment = {
            "OS_TARGET": self._nss_os(self.settings.os),
            "FREEBL_LOWHASH": "1",
            "NSS_FORCE_FIPS": "1",
            "BUILD_OPT": "1" if self.settings.build_type != "Debug" else "0",
            "PKG_CONFIG_ALLOW_SYSTEM_LIBS": "1",
            "PKG_CONFIG_ALLOW_SYSTEM_CFLAGS": "1",
            "NSS_DISABLE_GTESTS": "1",
            # "NSS_ALLOW_SSLKEYLOGFILE": "1",
            "NSS_ENABLE_WERROR": "0",
            # "POLICY_FILE": "nss.config",
            "NSS_USE_SYSTEM_SQLITE": "1",
            "SQLITE_INCLUDE_DIR": self.deps_cpp_info["sqlite3"].include_paths[-1],
            "SQLITE_LIB_NAME": self.deps_cpp_info["sqlite3"].libs[0],
            "SQLITE_LIB_DIR": self.deps_cpp_info["sqlite3"].lib_paths[0],
            "NSPR_INCLUDE_DIR": self.deps_cpp_info["nspr"].include_paths[-1],
            "NSPR_LIB_DIR": self.deps_cpp_info["nspr"].lib_paths[0],
        }
        if self.settings.compiler == "Visual Studio":
            if "MT" in str(self.settings.compiler.runtime):
                build_environment["USE_STATIC_RTL"] = "1"
            if "d" in str(self.settings.compiler.runtime):
                build_environment["USE_DEBUG_RTL"] = "1"
        if str(self.settings.arch) in ("x86_64", "armv8", "mips64"):
            build_environment["USE_64"] = "1"
        if self.settings.os == "Android":
            build_environment["OS_TARGET_RELEASE"] = os.environ["ANDROID_PLATFORM"]
        with tools.environment_append(build_environment):
            for dir in (os.path.join(self._source_subfolder, "coreconf"),
                        os.path.join(self._source_subfolder, "lib", "dbm"),
                        os.path.join(self._source_subfolder)):
                with tools.chdir(dir):
                    autotools.make(args=["-j1"])

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

        shutil.copytree(src=os.path.join(self._source_subfolder, "dist", "Release" if self.settings.build_type != "Debug" else "Debug"),
                        dst=self.package_folder)

        # if self.options.shared:
        # self._configure_gyp()
        # self.run("ninja install")
        # tools.rmdir(os.path.join(self.package_folder, "lib"))
        # try:
        #     os.remove(os.path.join(self.package_folder, "nlohmann_json.natvis"))
        # except FileNotFoundError:
        #     pass

    def package_info(self):
        self.cpp_info.libs = ["ssl3", "smime3", "nss3"]
