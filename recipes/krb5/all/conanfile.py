from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import glob
import os


class Krb5Conan(ConanFile):
    name = "krb5"
    description = "GNU Libidn is a fully documented implementation of the Stringprep, Punycode and IDNA 2003 specifications."
    homepage = "https://www.gnu.org/software/libidn/"
    topics = ("conan", "libidn", "encode", "decode", "internationalized", "domain", "name", "gssapi", "generic", "security", "service")
    license = "NOTICE"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread": [True, False],
        "use_dns_realms": [True, False],
        "leash": [True, False],
        "with_openssl": [True, False],
        "with_tcl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "thread": True,
        "use_dns_realms": False,
        "leash": False,
        "with_openssl": True,
        "with_tcl": False,
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            del self.options.thread
            del self.options.with_openssl
            del self.options.with_tcl
            # Visual Studio only builds shared libraries
            del self.options.shared
        else:
            del self.options.leash

    def configure(self):
        if self.options.get_safe("shared"):
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("krb5-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("pkgconf/1.7.3")
            self.build_requires("automake/1.16.2")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("e2fsprogs/1.45.6")
        if self.settings.compiler != "Visual Studio":
            self.requires("libverto/0.3.1")
        if self.options.get_safe("with_openssl"):
            self.requires("openssl/1.1.1g")
        if self.options.get_safe("with_tcl"):
            self.requires("tcl/8.6.10")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-thread-support={}".format(yes_no(self.options.thread)),
            "--enable-dns-for-realm={}".format(yes_no(self.options.use_dns_realms)),
            "--enable-pkinit={}".format(yes_no(self.options.with_openssl)),
            "--with-crypto-impl={}".format("openssl" if self.options.with_openssl else "builtin"),
            "--with-tls-impl={}".format("openssl" if self.options.with_openssl else "no"),
            "--with-spake-openssl={}".format(yes_no(self.options.with_openssl)),
            "--disable-nls",
            "--disable-rpath",
            "--without-libedit",
            "--without-readline",
            "--with-system-et",
            "--with-system-ss",
            "--with-system-libverto",
            "--with-tcl={}".format(self.deps_cpp_info["tcl"].rootpath if self.options.with_tcl else "no"),
        ]
        env = {
            "DB_LIB": "-ldb -pthread -ldl",             # FIXME: get info from deps_cpp_info somehow, including components
            "SS_LIB": "-lss -lcom_err -pthread -lrt",   # FIXME: get info from deps_cpp_info somehow, including components
            "CRYPTO_LIBS": "-lcrypto -pthread -ldl",    # FIXME: get info from deps_cpp_info somehow, including components
            "TLS_LIBS": "-lssl -lcrypto -pthread -ldl", # FIXME: get info from deps_cpp_info somehow, including components
        }
        with tools.environment_append(env):
            self._autotools.configure(args=conf_args, configure_dir=os.path.join(self._source_subfolder, "src"))
        return self._autotools

    def _build_autotools(self):
        with tools.chdir(os.path.join(self._source_subfolder, "src")):
            self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    @contextmanager
    def _msvc_context(self):
        env = {
            "KRB_INSTALL_DIR": self.package_folder,
        }
        with tools.environment_append(env):
            with tools.vcvars(self.settings):
                yield

    @property
    def _nmake_args(self):
        nmake_args = []
        if self.settings.build_type != "Debug":
            nmake_args.append("NODEBUG=1")
        if not self.options.leash:
            nmake_args.append("NO_LEASH=1")
        if self.options.use_dns_realms:
            nmake_args.append("KRB5_USE_DNS_REALMS=1")
        return nmake_args

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder, "src")):
            with self._msvc_context():
                self.run("nmake -f Makefile.in prep-windows", run_environment=True, win_bash=tools.os_info.is_windows)
                self.run("nmake {}".format(" ".join(self._nmake_args)), run_environment=True, win_bash=tools.os_info.is_windows)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("NOTICE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                with self._msvc_context():
                    self.run("nmake install {}".format(" ".join(self._nmake_args)), run_environment=True, win_bash=tools.os_info.is_windows)

            for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.unlink(pdb)
        else:
            autotools = self._configure_autotools()
            autotools.install()

            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "var"))

    def package_info(self):
        krb5_lib = "krb5"
        krb5support = "krb5support"
        crypto_libs = []
        gssapi_lib = "gssapi_krb5"
        if self.settings.compiler == "Visual Studio":
            suffix = {
                "x86_64": "64",
                "x86": "32",
            }[str(self.settings.arch)]

            krb5_lib += "_" + suffix
            krb5support = "k5sprt" + suffix
            gssapi_lib = "gssapi" + suffix
        else:
            crypto_libs.append("k5crypto")

        self.cpp_info.components["mit-krb5"].libs = [krb5_lib] + crypto_libs + [krb5support]
        if self.settings.compiler != "Visual Studio":
            self.cpp_info.components["mit-krb5"].requires = ["e2fsprogs::com_err"]
            if self.options.with_openssl:
                self.cpp_info.components["mit-krb5"].requires.append("openssl::ssl")
        self.cpp_info.components["mit-krb5"].names["pkg_config"] = "mit-krb5"
        if self.settings.os == "Linux":
            self.cpp_info.components["mit-krb5"].system_libs = ["resolv"]

        self.cpp_info.components["libkrb5"].libs = []
        self.cpp_info.components["libkrb5"].requires = ["mit-krb5"]
        self.cpp_info.components["libkrb5"].names["pkg_config"] = "krb5"

        self.cpp_info.components["mit-krb5-gssapi"].libs = [gssapi_lib]
        self.cpp_info.components["mit-krb5-gssapi"].requires = ["mit-krb5"]
        self.cpp_info.components["mit-krb5-gssapi"].names["pkg_config"] = "mit-krb5-gssapi"
        if self.settings.compiler != "Visual Studio" and self.settings.os == "Windows" and self.options.get_safe("shared"):
            self.cpp_info.components["mit-krb5-gssapi"].defines.append("GSS_DLL_FILE")

        self.cpp_info.components["krb5-gssapi"].libs = []
        self.cpp_info.components["krb5-gssapi"].requires = ["mit-krb5-gssapi"]
        self.cpp_info.components["krb5-gssapi"].names["pkg_config"] = "krb5-gssapi"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        if self.settings.compiler != "Visual Studio":
            self.cpp_info.components["gssrpc"].libs = ["gssrpc"]
            self.cpp_info.components["gssrpc"].requires = ["mit-krb5-gssapi"]
            self.cpp_info.components["gssrpc"].names["pkg_config"] = "gssrpc"

            self.cpp_info.components["kadm-client"].libs = ["kadm5clnt_mit"]
            self.cpp_info.components["kadm-client"].requires = ["mit-krb5-gssapi", "gssrpc"]
            self.cpp_info.components["kadm-client"].names["pkg_config"] = "kadm-client"

            self.cpp_info.components["kdb"].libs = ["kdb5"]
            self.cpp_info.components["kdb"].requires = ["mit-krb5-gssapi", "mit-krb5", "gssrpc"]
            self.cpp_info.components["kdb"].names["pkg_config"] = "kdb-client"

            self.cpp_info.components["kadm-server"].libs = ["kadm5srv_mit"]
            self.cpp_info.components["kadm-server"].requires = ["kdb", "mit-krb5-gssapi"]
            self.cpp_info.components["kadm-server"].names["pkg_config"] = "kadm-server"

            self.cpp_info.components["krad"].libs = ["krad"]
            self.cpp_info.components["krad"].requires = ["libkrb5", "libverto::libverto"]

            krb5_config = os.path.join(bin_path, "krb5-config").replace("\\", "/")
            self.output.info("Appending KRB5_CONFIG environment variable: {}".format(krb5_config))
            self.env_info.KRB5_CONFIG = krb5_config

