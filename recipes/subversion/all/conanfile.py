from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import glob


class SubversionConan(ConanFile):
    name = "subversion"
    description = "Subversion is an open source version control system"
    license = "BSD-3-Clause"
    topics = ("conan", "subversion", "scm", "svn", "team", "apache")
    homepage = "https://subversion.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    # generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("apr/1.7.0")
        self.requires("apr-util/1.6.1")
        self.requires("lz4/1.9.2")
        self.requires("utf8proc/2.5.0")
        self.requires("sqlite3/3.32.2")
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            # self.build_requires("cpython/3.8.x")
            self.output.info("Assuming cpython is available")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--with-apr={}".format(tools.unix_path(self.deps_cpp_info["apr"].rootpath)),
            "--with-apr-util={}".format(tools.unix_path(self.deps_cpp_info["apr-util"].rootpath)),
            "--with-lz4={}".format(tools.unix_path(self.deps_cpp_info["lz4"].rootpath)),
            "--with-utf8proc={}".format(tools.unix_path(self.deps_cpp_info["utf8proc"].rootpath)),
            "--with-zlib={}".format(tools.unix_path(self.deps_cpp_info["zlib"].rootpath)),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        for la in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
            os.unlink(la)

    def package_info(self):
        # FIXME: subversion supplies a svn_XXX.pc for each library
        # self.cpp_info.names["pkg_config"] = "svc_client"
        self.cpp_info.includedirs.append(os.path.join("include", "subversion-1"))
        self.cpp_info.libs = tools.collect_libs(self)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        binext = ".exe" if self.settings.os == "Windows" else ""

        subversion = os.path.join(bindir, "subversion" + binext)
        self.output.info("Setting SUBVERSION environment variable: {}".format(subversion))
        self.env_info.SUBVERSION = subversion
