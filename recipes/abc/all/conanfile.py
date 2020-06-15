from conans import CMake, ConanFile, tools
import glob
import os


# abc has an embedded version of cudd.
# When patching the sources to use the upstream cudd project, dependencies of abc segfault.
# ==> keep the embedded cudd


class AbcConan(ConanFile):
    name = "abc"
    description = "System for Sequential Logic Synthesis and Formal Verification"
    topics = ["conan", "abc", "logic", "synthesis", "formal", "verification"]
    homepage = "http://www.eecs.berkeley.edu/~alanmi/abc"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_namespace": "ANY",
        "with_pthreads": [True, False],
        "with_readline": ["auto", True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_namespace": "None",
        "with_pthreads": True,
        "with_readline": "auto",
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _with_readline(self):
        """
        readline does not support Visual Studio, so when the readline option is set to auto,
        so disable readline in those cases, else enable.
        """
        if self.options.with_readline == "auto":
            if self.settings.compiler == "Visual Studio":
                return False
            return True
        return self.options.with_readline

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/1.2.11")
        if self._with_readline:
            self.requires("readline/8.0")
        if self.options.with_pthreads:
            if self.settings.compiler == "Visual Studio":
                self.requires("pthreads4w/3.0.0")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if not tools.which("make"):
            self.build_requires("make/4.2.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("abc-*")[0], self._source_subfolder)

    @property
    def _make_args(self):
        make_args = [
            "OPTFLAGS=",
        ]
        if not self.options.with_pthreads:
            make_args.append("ABC_USE_NO_PTHREADS=1")
        return make_args

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.options.with_namespace != "None":
            self._cmake.definitions["ABC_USE_NAMESPACE"] = self.options.with_namespace
        self._cmake.definitions["ABC_WITH_READLINE"] = self._with_readline
        self._cmake.definitions["ABC_MAKEARGS"] = ";".join(self._make_args)

        if self.settings.compiler == "Visual Studio":
            del self._cmake.definitions["CMAKE_MAKE_PROGRAM"]

        print(self._cmake.definitions)
        self.run("{} {} {}".format(self._cmake._cmake_program, self._cmake.command_line, self.source_folder.replace("\\", "/")), run_environment=True)
        # self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("copyright.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.h", src=os.path.join(self._source_subfolder, "src"), dst="include")

    @property
    def _libcxx_library(self):
        return {
            "libstdc++11": "stdc++",
            "libstdc++": "stdc++",
            "libc++": "c++",
        }.get(self.settings.compiler.get_safe("libcxx"))

    def package_id(self):
        self.info.options.with_readline = self._with_readline

    def package_info(self):
        self.cpp_info.libs = ["abc"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
            if self.options.with_pthreads:
                self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines.append("WIN32_NO_DLL")
        if self.options.with_namespace != "None":
            self.cpp_info.defines.append("ABC_NAMESPACE={}".format(self.options.with_namespace))
        if self._libcxx_library:
            self.cpp_info.system_libs.append(self._libcxx_library)

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        abc_bin = os.path.join(bin_path, "abc{}".format(".exe" if self.settings.os == "Windows" else ""))
        self.user_info.ABC = abc_bin
