from conans import ConanFile, tools
from io import StringIO
import os


class TestPackageConan(ConanFile):

    def test(self):
        for tool in ("ar", "as", "ld", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"):
            tool_path = os.path.realpath(tools.which(tool))
            assert tool_path.startswith(self.deps_cpp_info["binutils"].rootpath)
            if not tools.cross_building(self.settings):
                output = StringIO()
                self.run("{} --version".format(tool_path), run_environment=True, output=output)
                text = output.getvalue()
                print(text)
                assert str(self.requires["binutils"].ref.version) in text
