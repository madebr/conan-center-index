from conans import ConanFile, tools
from conans.errors import ConanException
from io import StringIO
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _gold(self):
        try:
            # FIXME: hasattr or get_safe doesn't work
            return self.options["binutils"].gold
        except ConanException:
            return False

    def test(self):
        bins = ["ar", "as", "nm", "objcopy", "objdump", "ranlib", "readelf", "strip"]
        if self.options["binutils"].bfd:
            bins.append("ld.bfd")
        if self._gold:
            bins.append("ld.gold")
        if self.options["binutils"].bfd or self._gold:
            bins.append("ld")
        for bin in bins:
            bin_path = os.path.realpath(tools.which(bin))
            assert bin_path.startswith(self.deps_cpp_info["binutils"].rootpath)
            if not tools.cross_building(self.settings):
                output = StringIO()
                self.run("{} --version".format(bin_path), run_environment=True, output=output)
                text = output.getvalue()
                print(text)
                assert str(self.requires["binutils"].ref.version) in text
