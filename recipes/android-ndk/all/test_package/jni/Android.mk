LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := test_package
LOCAL_SRC_FILES := test_package.c
LOCAL_LDLIBS := -llog

include $(BUILD_SHARED_LIBRARY)
