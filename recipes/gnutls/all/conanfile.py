from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import shutil


class GnuTLSConan(ConanFile):
    name = "gnutls"
    description = "GnuTLS is a secure communications library implementing the SSL, TLS and DTLS protocols and technologies around them."
    homepage = "https://www.gnutls.org"
    topics = ("conan", "libgnutls", "tls", "secure", "socket")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "with_cxx": [True, False],
        "with_p11_kit": ["auto", True, False],
        "hardware_acceleration": [True, False],
        "tls13_interoperability": [True, False],
        "packlock_acceleration": [True, False],
        "sha1_support": [True, False],
        "ssl2_client_hello": [True, False],
        "ssl3": [True, False],
        "dtls_srtp_support": [True, False],
        "alpn_support": [True, False],
        "heartbeat_support": [True, False],
        "srp_authentication": [True, False],
        "psk_authentication": [True, False],
        "anon_authentication": [True, False],
        "dhe_support": [True, False],
        "ecdhe_support": [True, False],
        "gost_support": [True, False],
        "cryptodev_support": [True, False],
        "ocsp_support": [True, False],
        "openssl_compatibility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
        "with_cxx": True,
        "with_p11_kit": True,
        "hardware_acceleration": True,
        "tls13_interoperability": True,
        "packlock_acceleration": True,
        "sha1_support": True,
        "ssl2_client_hello": True,
        "ssl3": False,
        "dtls_srtp_support": True,
        "alpn_support": True,
        "heartbeat_support": True,
        "srp_authentication": True,
        "psk_authentication": True,
        "anon_authentication": True,
        "dhe_support": True,
        "ecdhe_support": True,
        "gost_support": True,
        "cryptodev_support": False,
        "ocsp_support": True,
        "openssl_compatibility": False,
    }
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.p11_kit
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared GnuTLS on Windows")
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("GnuTLS cannot be built using Visual Studio")
        if not self.options.with_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def _with_p11_kit(self):
        if self.options.get_safe("with_p11_kit",  False) == "auto":
            return self.settings.os != "Windows"
        else:
            return self.options.get_safe("with_p11_kit", False)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("gnutls-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("nettle/3.6")
        self.requires("libtasn1/4.16.0")
        self.requires("libunistring/0.9.10")
        if self._with_p11_kit:
            self.requires("p11-kit/0.23.20")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")

    @contextmanager
    def _build_context(self):
        env = {}
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
        enable_disable = lambda option, name : "--{}-{}".format("enable" if option else "disable", name)
        conf_args = [
            enable_disable(self.options.tools, "tools"),
            enable_disable(self.options.hardware_acceleration, "hardware-acceleration"),
            enable_disable(self.options.tls13_interoperability, "tls13-interop"),
            enable_disable(self.options.packlock_acceleration, "padlock"),
            enable_disable(self.options.sha1_support, "sha1-support"),
            enable_disable(self.options.ssl3, "ssl3-support"),
            enable_disable(self.options.ssl2_client_hello, "ssl2-support"),
            enable_disable(self.options.dtls_srtp_support, "dtls-srtp-support"),
            enable_disable(self.options.alpn_support, "alpn-support"),
            enable_disable(self.options.heartbeat_support, "heartbeat-support"),
            enable_disable(self.options.srp_authentication, "srp-authentication"),
            enable_disable(self.options.psk_authentication, "psk-authentication"),
            enable_disable(self.options.anon_authentication, "anon-authentication"),
            enable_disable(self.options.dhe_support, "dhe"),
            enable_disable(self.options.ecdhe_support, "ecdhe"),
            enable_disable(self.options.gost_support, "gost"),
            enable_disable(self.options.cryptodev_support, "cryptodev"),
            enable_disable(self.options.ocsp_support, "ocsp"),
            enable_disable(self.options.openssl_compatibility, "openssl-compatibility"),
            enable_disable(self.options.with_cxx, "cxx"),
            "--with-p11-kit" if self._with_p11_kit else "--without-p11-kit",
            "--disable-doc",
            "--disable-tests",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])

        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        if self.settings.os == "Windows":
            if not self.options.shared:
                gnutls_h_in = os.path.join(self._source_subfolder, "lib", "includes", "gnutls", "gnutls.h.in")
                tools.replace_in_file(gnutls_h_in,
                                      "# define _SYM_EXPORT __declspec(dllimport)",
                                      "# define _SYM_EXPORT")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libgnutls.la"))
        if self.options.with_cxx:
            os.unlink(os.path.join(self.package_folder, "lib", "libgnutlsxx.la"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gnutls"]
        if self.options.with_cxx:
            self.cpp_info.libs.append("gnutlsxx")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["crypt32", "ws2_32"])
        self.cpp_info.includedirs.append(os.path.join("include", "gnutls"))
