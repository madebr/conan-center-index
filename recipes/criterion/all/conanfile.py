from conans import ConanFile, Meson, tools
import os
import glob


class CriterionConan(ConanFile):
    name = "criterion"
    description = "A cross-platform C and C++ unit testing framework for the 21st century"
    topics = "conan", "criterion", "unit", "testing", "framework"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Snaipe/Criterion"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
    }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.56.0")
        # self.build_requires("pkgconf/1.7.3")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-v{}".format(self.name, self.version), self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        self._meson.options["tests"] = "false"
        self._meson.options["sample"] = "false"
        self._meson.options["cxx-support"] = str(self.options.cxx).lower()
        self._meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        if self.settings.compiler == "Visual Studio":
            for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.unlink(pdb)
            if not self.options.shared:
                os.rename(os.path.join(self.package_folder, "lib", "libcriterion.a"),
                          os.path.join(self.package_folder, "lib", "criterion.lib"))

    def package_info(self):
        self.cpp_info.libs = ["criterion"]
        self.cpp_info.names["pkg_config"] = "criterion"
