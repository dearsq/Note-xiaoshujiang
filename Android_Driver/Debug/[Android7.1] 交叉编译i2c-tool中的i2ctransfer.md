title: [Android7.1] 交叉编译i2c-tool中的i2ctransfer
date: 2020-1-15 21:00:00
tags: Android

---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.126

[TOC]

## 需求分析
在 rk3399 平台分析 i2c 从设备的时候，调试的从设备寄存器地址是 16bit　的．
之前用的 i2cdump 等工具只适用于 8bit 的分析．
查看 i2c-tools 官方了解到，在 i2c-tools 的 4.0 版本，已经对 16bit 进行了支持．

## 下载
```
git clone git://git.kernel.org/pub/scm/utils/i2c-tools/i2c-tools.git
```
参考　https://i2c.wiki.kernel.org/index.php/I2C_Tools


## 源码编译
源码编译有两种方式．
一，找到 Android SDK 的交叉编译工具链．
修改源码根目录下的 Makefile 编译规则：
将 CC AR STRIP 编译工具链改为交叉编译工具链．
工具链在 SDK 的 `/prebuilt/linux-x86/toolchain/arm-eabi-4.8/` 下．

二，直接利用 Android 的 Android.mk 进行编译
将源码拷贝到 SDK 的 external 中：
```
cp -a i2c-tools /SDK/external/
```
我们采用第二种

### 编写编译规则 Android.mk
```
# external/i2c-tools/Android.mk

LOCAL_PATH:= $(call my-dir)
 
include $(CLEAR_VARS)
  
LOCAL_MODULE_TAGS := optional
LOCAL_C_INCLUDES += $(LOCAL_PATH)/include $(LOCAL_PATH)/../$(KERNEL_DIR)/include
LOCAL_SRC_FILES := tools/i2cbusses.c tools/util.c
LOCAL_MODULE := i2c-tools
include $(BUILD_STATIC_LIBRARY)
 
include $(CLEAR_VARS)
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES:=tools/i2ctransfer.c
LOCAL_MODULE:=i2ctransfer
LOCAL_CPPFLAGS += -DANDROID
LOCAL_SHARED_LIBRARIES:=libc
LOCAL_STATIC_LIBRARIES := i2c-tools
LOCAL_C_INCLUDES += $(LOCAL_PATH)/include $(LOCAL_PATH)/../$(KERNEL_DIR)/include
include $(BUILD_EXECUTABLE)
```

### 进行编译
```
$mm -B -j32
```
编译的结果会生成在 out 目录下：
`out/target/product/rk3399_mid_pi/system/bin/i2ctransfer`

## 工具用法
用法不再赘述，不加任何后缀可以看到用法：
```shell
adb push i2ctransfer /system/bin/


rk3399_mid_pi:/ # i2ctransfer                                                
Usage: i2ctransfer [-f] [-y] [-v] [-V] [-a] I2CBUS DESC [DATA] [DESC [DATA]]...
  I2CBUS is an integer or an I2C bus name
  DESC describes the transfer in the form: {r|w}LENGTH[@address]
    1) read/write-flag 2) LENGTH (range 0-65535) 3) I2C address (use last one if omitted)
  DATA are LENGTH bytes for a write message. They can be shortened by a suffix:
    = (keep value constant until LENGTH)
    + (increase value by 1 until LENGTH)
    - (decrease value by 1 until LENGTH)
    p (use pseudo random generator until LENGTH with value as seed)

Example (bus 0, read 8 byte at offset 0x64 from EEPROM at 0x50):
  # i2ctransfer 0 w1@0x50 0x64 r8
Example (same EEPROM, at offset 0x42 write 0xff 0xfe ... 0xf0):
  # i2ctransfer 0 w17@0x50 0x42 0xff-

```