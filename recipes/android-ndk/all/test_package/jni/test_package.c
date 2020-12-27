#include <android/log.h>

__attribute__((visibility("default")))
void test_package_log_message(const char *msg) {
    __android_log_print(ANDROID_LOG_DEBUG, "test_package", "%s", msg);
}
