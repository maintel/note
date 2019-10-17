<!-- TOC -->

- [概述](#概述)
- [举个例子](#举个例子)
- [编写JNI文件](#编写jni文件)
- [编译MK文件](#编译mk文件)

<!-- /TOC -->
# 概述

在`Android`开发中有时会遇到使用`JNI`调用`C/C++`函数库的场景。一般这个时候都是使用`NDK`将`C/C++`源代码编译出`so`文件，然后进行调用。但是有时候会遇到另外的情况：

    我们在NDK项目中还要再引入其他第三方的SO库

这个时候该怎么编译呢？

    通过使用动态函数库的调用方法，直接包含其头文件，便可以直接调用库中的类和方法。

具体使用过程可以分为两步：

- 编写JNI文件包含第三方库的头文件。

- 编写MK文件引入预编译库（即第三方库）。

# 举个例子

拿现在项目中遇到的一个具体情景：

现在手头有一个USB设备，公司要求实现在`windows`、`Android`、`Linux嵌入式`三平台通用的USB驱动库，然后各个平台只用做小量修改即可使用。经过评估决定使用git上的一个开源项目[libusb](https://github.com/libusb/libusb)来实现，当然可以直接使用源码来编译一个so出来，但是这样不够B格，而且实际使用过程中还要引入另外一个库文件，所以这里使用上面说的方式来调用，如下。

# 编写JNI文件

在要编写的源文件目录下新建`include`文件夹，将要使用的函数所在的头文件放入其中，如：libusb.h。

在我们的源码中包含这个头文件

```C
#include "include/libusb.h"
```

然后直接在需要使用的位置调用相应的函数即可：

```c
JNIEXPORT void JNICALL Java_com_usbtest_UsbTest_libUsbInit
        (JNIEnv *env, jclass jobj) {
    if (libusb_init(NULL) < 0)
	{
		LOGD("VeinSensorBase::Open(): libusb_init() <0\n");
	}
}
```
# 编译MK文件

首先将第三方库作为预编译引入

```
LOCAL_PATH := $(call my-dir)  

include $(CLEAR_VARS)  
LOCAL_MODULE := usb_pre   
LOCAL_SRC_FILES := usb/libusb-1.0.so
LOCAL_EXPORT_C_INCLUDES := include           
include $(PREBUILT_SHARED_LIBRARY)


include $(CLEAR_VARS)  
LOCAL_MODULE    := test 
LOCAL_SRC_FILES := usb_test.c
LOCAL_SHARED_LIBRARIES := usb_pre
LOCAL_LDLIBS := -llog  
include $(BUILD_SHARED_LIBRARY)  
```
其中：

- `LOCAL_MODULE := usb_pre` 给这个第三方库取一个名字，不需要与原来的名字相同。

- `LOCAL_SRC_FILES := usb/libusb-1.0.so` 表示这个库的路径，是在MK文件的目录下的`usb`目录中。

- `LOCAL_EXPORT_C_INCLUDES := include` 引用的第三方so库的头文件位置。

- `PREBUILT_SHARED_LIBRARY` 表示这是一个共享库，即so库。

- `LOCAL_SHARED_LIBRARIES := usb_pre` 这一步则表示此模块依赖于上面命名的预编译库。

然后执行`ndk-build`编译即可，此时在libs文件夹中会生成两个so文件，分别为`libtest.so`和`libusb-1.0.so`,都拷贝到项目中就可以了。
