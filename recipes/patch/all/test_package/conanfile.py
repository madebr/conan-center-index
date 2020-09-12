from conans import ConanFile, tools
from conans.errors import ConanException
import os
import shutil
import textwrap


class TestPackageConan(ConanFile):
    def test(self):
        shutil.copy(os.path.join(self.source_folder, "source.c"),
                    os.path.join(self.build_folder, "source.c"))
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("patch <{}".format(os.path.join(self.source_folder, "some-patch.diff")), run_environment=True)
        text = tools.load("source.c")
        ref = textwrap.dedent("""\
            #include <stdio.h>

            int main () {
                printf("Hello world from test_package.c\\n");
                return 1;
            }
            """)
        if text != ref:
            raise ConanException("Patch not applied correctly")

