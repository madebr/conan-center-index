from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("doxygen --version", run_environment=True)
