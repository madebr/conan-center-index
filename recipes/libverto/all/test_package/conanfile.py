from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.verbose=True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            impls = []
            if self.options["libverto"].with_glib:
                impls.append("glib")
            if self.options["libverto"].with_libev:
                impls.append("libev")
            if self.options["libverto"].with_libevent:
                impls.append("libevent")
            if self.options["libverto"].with_tevent:
                impls.append("tevent")

            for impl in impls:
                self.run("{} {}".format(bin_path, impl), run_environment=True)

