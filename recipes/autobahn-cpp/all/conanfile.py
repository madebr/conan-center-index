from conans import ConanFile, tools
import os


class AutobahnCppConan(ConanFile):
    name = "autobahn-cpp"
    description = "WAMP for C++ in Boost/Asio"
    topics = ("conan", "autobahn", "wamp", "asio", "distributed", "pubsub", "rRPC")
    license = "BSL-1.0"
    homepage = "https://crossbar.io/autobahn/"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_sources = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.73.0")
        self.requires("msgpack/3.2.1")
        self.requires("websocketpp/0.8.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "autobahn"), dst=os.path.join("include", "autobahn"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        pass
