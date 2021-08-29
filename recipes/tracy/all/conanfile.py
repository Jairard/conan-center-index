import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class TracyConan(ConanFile):
    name = "tracy"
    license = "3-clause BSD"
    homepage = "https://github.com/wolfpld/tracy"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ frame profiler "
    topics = ("gamedev", "library", "performance", "profiler", "performance-analysis",
              "profiling", "gamedev-library", "profiling-library", "gamedevelopment")
    settings = "os", "compiler", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    version = "cci.20210829"

    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(
            self._source_subfolder, "CMakeLists.txt")

        tools.replace_in_file(cmakelists,
                              """
target_link_libraries(
    TracyClient
    PUBLIC
        Threads::Threads
        ${CMAKE_DL_LIBS}
)
""",
                              """
target_link_libraries(
    TracyClient
    PUBLIC
        Threads::Threads
        ${CONAN_LIBS}
)
""")

        tools.save_append(cmakelists, """
install(TARGETS TracyClient
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    FRAMEWORK DESTINATION lib
)
        """)

    def _get_or_configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._get_or_configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._get_or_configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "tracy"
        self.cpp_info.names["cmake_find_package_multi"] = "tracy"

    def deploy(self):
        self.copy("*", dst="lib", src="lib")
