import os
from conans import CMake, ConanFile, tools


class PackageP7Zip(ConanFile):
    name = "p7zip"
    version = "16.02"
    url = "https://github.com/conan-io/conan-center-index"
    description = "p7zip is a quick port of 7z.exe and 7za.exe (command line version of 7zip, see www.7-zip.org) for Unix"
    license = ("LGPL-2.1", "BSD-3-Clause", "Unrar")
    homepage = "https://www.7-zip.org"
    exports_sources = "CMakeLists.txt", "patches/**"
    topics = ("conan", "7zip", "zip", "compression", "decompression")
    settings = "os_build", "arch_build", "compiler"

    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("p7zip_{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*", src="bin", dst="bin")
        self.copy("License.txt", src=os.path.join(self._source_subfolder, "DOC"), dst="licenses")
        self.copy("unRarLicense.txt", src=os.path.join(self._source_subfolder, "DOC"), dst="licenses")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.path.append(bin_path)
