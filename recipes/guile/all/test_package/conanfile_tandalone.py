from conans import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    def test(self):
        guile_path = os.path.realpath(tools.which("guile"))
        assert guile_path.startswith(self.deps_cpp_info["guile"].rootpath)
        input = os.path.join(os.path.dirname(os.path.realpath(__file__)), "input.ss")
        if not tools.cross_building(self.settings):
            output = StringIO()
            with tools.environment_append({"GUILE_AUTO_COMPILE": "0"}):
                self.run("{} -s {}".format(guile_path, input), output = output)
            text = output.getvalue()
            print(text)
            assert "hello conan world" in text
            assert "1337" in text
