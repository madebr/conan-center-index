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
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-tools={}".format(yes_no(self.options.tools)),
            "--enable-tools={}".format(yes_no(self.options.tools)),
            "--enable-hardware-acceleration={}".format(yes_no(self.options.hardware_acceleration)),
            "--enable-tls13-interop={}".format(yes_no(self.options.tls13_interoperability)),
            "--enable-padlock={}".format(yes_no(self.options.packlock_acceleration)),
            "--enable-sha1-support={}".format(yes_no(self.options.sha1_support)),
            "--enable-ssl3-support={}".format(yes_no(self.options.ssl3)),
            "--enable-ssl2-support={}".format(yes_no(self.options.ssl2_client_hello)),
            "--enable-dtls-srtp-support={}".format(yes_no(self.options.dtls_srtp_support)),
            "--enable-alpn-support={}".format(yes_no(self.options.alpn_support)),
            "--enable-heartbeat-support={}".format(yes_no(self.options.heartbeat_support)),
            "--enable-srp-authentication={}".format(yes_no(self.options.srp_authentication)),
            "--enable-psk-authentication={}".format(yes_no(self.options.psk_authentication)),
            "--enable-anon-authentication={}".format(yes_no(self.options.anon_authentication)),
            "--enable-dhe={}".format(yes_no(self.options.dhe_support)),
            "--enable-ecdhe={}".format(yes_no(self.options.ecdhe_support)),
            "--enable-gost={}".format(yes_no(self.options.gost_support)),
            "--enable-cryptodev={}".format(yes_no(self.options.cryptodev_support)),
            "--enable-ocsp={}".format(yes_no(self.options.ocsp_support)),
            "--enable-openssl-compatibility={}".format(yes_no(self.options.openssl_compatibility)),
            "--enable-cxx={}".format(yes_no(self.options.with_cxx)),
            "--with-p11-kit={}".format(yes_no(self._with_p11_kit)),
            "--disable-doc",
            "--disable-tests",
        ]

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
