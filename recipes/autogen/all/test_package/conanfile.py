from conans import CMake, ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        autogen_path = os.path.realpath(tools.which("autogen"))
        assert autogen_path.startswith(self.deps_cpp_info["autogen"].rootpath)
        output = StringIO()
        self.run("{} --version".format(autogen_path), run_environment=True, output=output)
        text = output.getvalue()
        print(text)
        assert str(self.requires["autogen"].ref.version) in text

        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
