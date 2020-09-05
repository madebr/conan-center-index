from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _tls_backends(self):
        res = []
        if self.options["glib-networking"].with_openssl:
            res.append("openssl")
        if self.options["glib-networking"].with_gnutls:
            res.append("gnutls")
        return res

    def build(self):
        cmake = CMake(self)
        cmake.definitions["STATIC_BACKEND"] = not self.options["glib-networking"].shared
        cmake.definitions["TLS_BACKENDS"] = ";".join(self._tls_backends)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            for backend in self._tls_backends:
                bin_path = os.path.join("bin", "test_package_{}".format(backend))
                self.run(bin_path, run_environment=True)

