import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException


class QemuConan(ConanFile):
    name = "qemu"
    description = "QEMU is a generic and open source machine emulator and virtualizer"
    topics = ("conan", "qemu", "emulator", "virtualizer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qemu.org/"
    license = ("GPL-2.0", "BSD", "MIT", "CC-BY")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bzip2": [True, False],
        "with_lzo": [True, False],
        "with_lzfse": [True, False],
        "with_snappy": [True, False],
        "with_curl": [True, False],
        "with_curses": [True, False],
        "with_smartcard": [True, False],
        "with_usb": [True, False],
        "with_bluez": [True, False],
        "with_ssh": [True, False],
        "with_iconv": [True, False],
        "with_braille": [True, False],
        "with_libxml2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bzip2": True,
        "with_lzo": True,
        "with_lzfse": True,
        "with_snappy": True,
        "with_curl": True,
        "with_curses": True,
        "with_smartcard": True,
        "with_usb": True,
        "with_bluez": True,
        "with_ssh": True,
        "with_iconv": True,
        "with_braille": True,
        "with_libxml2": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if not tools.is_apple_os(self.settings.os):
            del self.options.with_lzfse

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("msys2/20161025")

    def requirements(self):
        import sys
        if sys.version_info < (3,):
            raise ConanException("This recipe requires Python >= 3.0")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzo:
            self.requires("lzo/2.10")
        # if self.options.with_lzfse:
        #     self.requires("lzfse/x.x.x")
        if self.options.with_snappy:
            self.requires("snappy/1.1.7")
        if self.options.with_curl:
            self.requires("libcurl/7.66.")
        if self.options.with_curses:
            raise ConanException("curses is not in the conan-center-index (yet)")
            self.requires("curses/x.x.x")
        if self.options.with_smartcard:
            self.requires("libcacard/x.x.x")
        if self.options.with_usb:
            self.requires("libusb/x.x.x")
        if self.options.with_bluez:
            self.requires("bluez/x.x.x")
        if self.options.with_ssh:
            self.requires("libssh2/1.9.0")
        if self.options.with_iconv:
            self.requires("iconv/x.x.x")
        if self.options.with_braille:
            self.requires("brlapi/x.x.x")
        if self.options.with_libxml2:
            self.requires("libxml2/2.9.9")

    @staticmethod
    def _enable_disable(name, b):
        return "--{}-{}".format("--enable-" if b else "--disable-", name)

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            self._enable_disable("bzip2", self.options.with_bzip2),
            self._enable_disable("lzo", self.options.with_lzo),
            self._enable_disable("curl", self.options.with_curl),
            self._enable_disable("curses", self.options.with_curses),
            self._enable_disable("smartcard", self.options.with_smartcard),
            self._enable_disable("libusb", self.options.with_usb),
            self._enable_disable("bluez", self.options.with_bluez),
            self._enable_disable("libssh", self.options.with_ssh),
            self._enable_disable("iconv", self.options.with_iconv),
            self._enable_disable("libxml2", self.options.with_libxml2),
        ]
        if tools.is_apple_os(self.settings.os):
            conf_args.append(self._enable_disable("lzfse", self.options.with_lzfse))

        autotools.configure(args=conf_args)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        # tools.rmdir(os.path.join(self.package_folder, "cmake"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.sort(reverse=True)

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]
        self.cpp_info.name = "Protobuf"
