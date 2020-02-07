from conans import ConanFile, CMake, tools
import os
from io import StringIO


class TclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        guile_path = self.deps_env_info["guile"].GUILE
        input = os.path.join(os.path.dirname(os.path.realpath(__file__)), "input.scm")
        if not tools.cross_building(self.settings):
            output = StringIO()
            with tools.environment_append({"GUILE_AUTO_COMPILE": "0"}):
                self.run("{} -s {}".format(guile_path, input), output=output, run_environment=True)
            text = output.getvalue()
            print(text)
            assert "hello conan world" in text
            assert "1337" in text

        if not tools.cross_building(self.settings):
            output = StringIO()
            bin_path = os.path.join("bin", "test_package")
            input = os.path.join(os.path.dirname(os.path.realpath(__file__)), "embedded_input.scm")
            with tools.environment_append({"GUILE_AUTO_COMPILE": "0"}):
                self.run("{} -s {}".format(bin_path, input), run_environment=True, output=output)
            text = output.getvalue()
            print(text)
            assert "SECRET VALUE DETECTED" in text
