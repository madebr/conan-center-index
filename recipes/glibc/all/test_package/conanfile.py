from conans import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        for tool in ("getent", "iconv", "ldd", "locale", "makedb", "xtrace"):
            tool_path = tools.which(tool)
            assert tool_path
            tool_path = os.path.realpath(tool_path)
            assert tool_path.startswith(self.deps_cpp_info["glibc"].rootpath)
            if not tools.cross_building(self.settings):
                output = StringIO()
                self.run("{} --version".format(tool_path), output=output, run_environment=True)
                text = output.getvalue()
                print(text)
                assert str(self.requires["glibc"].ref.version) in text
