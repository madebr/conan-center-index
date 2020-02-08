from conans import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):

    def test(self):
        self.run("pkg-config --version", run_environment=True)
        test_dir = os.path.dirname(os.path.realpath(__file__))
        with tools.environment_append({"PKG_CONFIG_PATH": [test_dir]}):
            output = StringIO()
            self.run("pkg-config --modversion libastral", run_environment=True, output=output)
            text = output.getvalue()
            print(text)
            assert "6.6.6" in text
