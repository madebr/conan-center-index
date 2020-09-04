from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os


class LibVertoConan(ConanFile):
    name = "libverto"
    description = "An async event loop abstraction library."
    homepage = "https://github.com/latchset/libverto"
    topics = ("conan", "libverto", "async", "eventloop")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "pthread": [True, False],
        "with_glib": [True, False],
        "with_libev": [True, False],
        "with_libevent": [True, False],
        "with_tevent": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "pthread": True,
        "with_glib": True,
        "with_libev": True,
        "with_libevent": True,
        "with_tevent": True,
    }
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.pthread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libverto-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.65.1")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libev:
            self.requires("libev/4.33")
        if self.options.with_tevent:
            self.requires("tevent/0.10.2")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pthread={}".format(yes_no(self.options.get_safe("pthread"))),
            "--with-glib={}".format(yes_no(self.options.with_glib)),
            "--with-libev={}".format(yes_no(self.options.with_libev)),
            "--with-libevent={}".format(yes_no(self.options.with_libevent)),
            "--with-tevent={}".format(yes_no(self.options.with_tevent)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libverto.la"))
        if self.options.with_glib:
            os.unlink(os.path.join(self.package_folder, "lib", "libverto-glib.la"))
        if self.options.with_libev:
            os.unlink(os.path.join(self.package_folder, "lib", "libverto-libev.la"))
        if self.options.with_libevent:
            os.unlink(os.path.join(self.package_folder, "lib", "libverto-libevent.la"))
        if self.options.with_tevent:
            os.unlink(os.path.join(self.package_folder, "lib", "libverto-tevent.la"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["verto"].libs = ["verto"]
        self.cpp_info.components["verto"].names["pkg_config"] = "libverto"
        if self.settings.os == "Linux":
            self.cpp_info.components["verto"].system_libs.append("dl")
            if self.options.pthread:
                self.cpp_info.components["verto"].system_libs.append("pthread")

        if self.options.with_glib:
            self.cpp_info.components["verto-glib"].libs = ["verto-glib"]
            self.cpp_info.components["verto-glib"].names["pkg_config"] = "libverto-glib"
            self.cpp_info.components["verto-glib"].requires = ["verto", "glib::glib"]

        if self.options.with_libev:
            self.cpp_info.components["verto-libev"].libs = ["verto-libev"]
            self.cpp_info.components["verto-libev"].names["pkg_config"] = "libverto-libev"
            self.cpp_info.components["verto-libev"].requires = ["verto", "libev::libev"]

        if self.options.with_libevent:
            self.cpp_info.components["verto-libevent"].libs = ["verto-libevent"]
            self.cpp_info.components["verto-libevent"].names["pkg_config"] = "libverto-libevent"
            self.cpp_info.components["verto-libevent"].requires = ["verto", "libevent::libevent"]

        if self.options.with_tevent:
            self.cpp_info.components["verto-tevent"].libs = ["verto-tevent"]
            self.cpp_info.components["verto-tevent"].names["pkg_config"] = "libverto-tevent"
            self.cpp_info.components["verto-tevent"].requires = ["verto", "tevent::tevent"]
