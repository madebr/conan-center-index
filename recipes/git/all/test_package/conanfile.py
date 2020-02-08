from conans import ConanFile
from io import StringIO


class TestPackageConan(ConanFile):

    def test(self):
        output = StringIO()
        self.run("git --version", run_environment=True, output=output)
        text = output.getvalue()
        print(text)
        assert self.requires["git"].ref.version in text
