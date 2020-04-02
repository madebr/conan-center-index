from conans import CMake, ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path1 = os.path.join("bin", "test_package")
            src_path = os.path.join(self.source_folder, "hello_world.c")
            self.run("{} {} {}".format(bin_path1, os.path.join(tools.get_env("TCCLIB_PATH"), "include"), src_path), run_environment=True)

            bin_path2 = os.path.join("bin", "hello_world{}".format(".exe" if self.settings.os == "Windows" else ""))
            self.run("tcc -c {}/hello_world.c -o hello_world.o".format(self.source_folder), run_environment=True)
            self.run("tcc hello_world.o -o {}".format(bin_path2), run_environment=True)
            if True:  # FIXME: use target arch of tcc
                self.run(bin_path2, run_environment=True)
                self.run("tcc -run {}".format(src_path))
