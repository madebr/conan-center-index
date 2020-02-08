from conans import ConanFile, tools
import os


class NSISConan(ConanFile):
    name = "nsis"
    description = "NSIS (Nullsoft Scriptable Install System) is a professional open source system to create Windows installers"
    license = "???"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://nsis.sourceforge.io"
    topics = ("conan", "nsis", "installer", "windows")
    settings = "os_build", "arch_build", "compiler"
    exports_sources = "SConstruct"
    generator = "scons"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        if not tools.which("scons"):
            self.build_requires("scons/3.1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("nsis-{}-src".format(self.version), self._source_subfolder)

    def build(self):
        os.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            scons_args = {
                "ZLIB_W32": self.deps_cpp_info["zlib"].lib_paths[0],
            }
            self.run("scons -C {nsis_dir} {args}".format(
                nsis_dir=os.path.join(self.source_folder, self._source_subfolder),
                args=" ".join("{}={}".format(k, v) for k, v in scons_args.items()),
            ))

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._build_subfolder):
            pass

        # tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler
        # FIXME: should the vendor be included in the package_id?

    def package_info(self):
        pass
        # bindir = os.path.join(self.package_folder, "bin")
        # self.output.info("Appending PATH environment variable: {}".format(bindir))
        # self.env_info.PATH.append(bindir)
        #
        # target_bindir = os.path.join(self._exec_prefix, self._triplet_target, "bin")
        # self.output.info("Appending PATH environment variable: {}".format(target_bindir))
        # self.env_info.PATH.append(target_bindir)
