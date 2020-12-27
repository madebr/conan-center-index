from conans import ConanFile, tools
import os
import shutil


class TestPackgeConan(ConanFile):
    settings = "os", "arch"


    def build(self):
        if not tools.cross_building(self.settings):
            tools.mkdir(os.path.join(self.build_folder, "jni"))
            for fn in ("jni/Android.mk", "jni/test_package.c"):
                shutil.copy(os.path.join(self.source_folder, fn),
                            os.path.join(self.build_folder, fn))
            args = [
                "NDK_PROJECT_PATH='{}'".format(self.build_folder),
                "APP_ABI={}".format("arm64-v8a"),  # FIXME
                "APP_PLATFORM={}".format(20),  # FIXME
                "V=1",
            ]
            with tools.environment_append({"VERBOSE": "yes"}):
                self.run("ndk-build {}".format(" ".join(args)), run_environment=True)


    def test(self):
        if not tools.cross_building(self):
            self.run("ndk-build --version", run_environment=True)
