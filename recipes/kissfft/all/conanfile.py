from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os


class KissfftConan(ConanFile):
    name = "kissfft"
    description = "a Fast Fourier Transform (FFT) library that tries to Keep it Simple, Stupid"
    topics = "UNKNOWN TOPICS"
    license = "https://github.com/mborgerding/kissfft"
    homepage = "https://github.com/mborgerding/kissfft"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    # def requirements(self):
    #     pass

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _run_makefile(self, target=None):
            if self.settings.compiler != "Visual Studio":
                autotools = AutoToolsBuildEnvironment(self)
                autotools.libs = []
                with tools.environment_append(autotools.vars):
                    self.run("make -f 'Makefile' {}".format(target), run_environment=True)

    def build(self):
        self._run_makefile()

    def package(self):
        self._run_makefile("install")

    def package_info(self):
        self.cpp_info.libs = ["kissfft"]