from conans import ConanFile, tools
from io import StringIO


class TestPackageConan(ConanFile):

    def test(self):
        output = StringIO()
        if not tools.cross_building(self.settings):
            self.run("ct-ng help", run_environment=True, output=output)
            print(output.getvalue())
            assert self.requires["crosstool-ng"].ref.version in output.getvalue()
            self.run("ct-ng list-samples", run_environment=True)
