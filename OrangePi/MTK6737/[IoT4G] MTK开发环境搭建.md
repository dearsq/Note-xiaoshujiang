---
title: [IoT4G] MTK 开发环境搭建
tags: Bug,Android
grammar_cjkRuby: true
---
Hardware: MTK6737
Android: 6.0(API 23)
Kernel: Linux 3.4.67

[TOC]

## 安装编译环境并编译
#### 安装编译环境依赖包
2>ubuntu < 12.04
```
sudo apt-get install git-core gnupg flex bison ccache gperf libsdl1.2-dev libesd0-dev libwxgtk2.6-dev build-essential zip curl libncurses5-dev zlib1g-dev valgrind libc6-dev lib32ncurses5-dev x11proto-core-dev libx11-dev lib32readline-gplv2-dev lib32z1-dev libgl1-mesa-dev gcc-4.4 g++-4.4 g++-4.4-multilib g++-multilib mingw32 tofrodos python-markdown libxml2-utils xsltproc wine
```
3>ubuntu = 14.04
```
sudo apt-get install git-core gnupg flex bison ccache gperf libsdl1.2-dev libesd0-dev libwxgtk2.8-dev build-essential zip curl libncurses5-dev zlib1g-dev valgrind libc6-dev lib32ncurses5-dev x11proto-core-dev libx11-dev lib32readline-gplv2-dev lib32z1-dev libgl1-mesa-dev g++-multilib g++-4.8-multilib mingw32 tofrodos python-markdown libxml2-utils xsltproc libc6-dev-i386 lib32z1 lib32ncurses5 lib32bz2-1.0 lib32readline-gplv2-dev wine
```
安装无问题

ubuntu = 16.04
```
sudo apt-get install git-core gnupg flex bison ccache gperf libsdl1.2-dev libesd0-dev libwxgtk2.8-dev build-essential zip curl libncurses5-dev zlib1g-dev valgrind libc6-dev lib32ncurses5-dev x11proto-core-dev libx11-dev lib32readline-gplv2-dev lib32z1-dev libgl1-mesa-dev g++-multilib g++-4.8-multilib mingw32 tofrodos python-markdown libxml2-utils xsltproc libc6-dev-i386 lib32z1 lib32ncurses5 lib32bz2-1.0 lib32readline-gplv2-dev wine
```
报错有如下无法定位：
libwxgtk2.8-dev mingw32
lib32bz2-1.0 lib32readline-gplv2-dev

在 Ubuntu16.04 中 
libwxgtk2.8-dev 已经升级为 libwxgtk3.0-dev;
lib32bz2-1.0 已经升级为 libbz2-1.0:i386;
lib32readline-gplv2-dev 已经升级为  lib32readline6-dev;
所以：
```
sudo apt install libwxgtk3.0-dev  lib32readline6-dev libbz2-1.0:i386
```
mingw32 需要在 `sudo vi /etc/apt/sources.list`添加源：
```
deb http://us.archive.ubuntu.com/ubuntu trusty main universe
```
之后如下即可
```
sudo apt update
sudo apt install mingw32 
```

#### bootloader 和 kernel 编译
**全编译：**
```
cd runyee/scripts/
./auto.sh IoT_bd6737m_35g_b_m0_ry_smt_hd720_pcb_v1 v00 eng
```
了解到现在我们的模块 lunch 的是 bd6737m_35g_b_m0 这个 project 

**模块编译：**
首先通过 get_build_var 获得 project name：
```
get_build_var TARGET_DEVICE
op_project_name

get_build_var TARGET_BUILD_VARIANT
eng
```
分模块编译的时候可以传入
**preloader：**
1. 单独编译
```
make -j4 pl 2>&1 | tee pl_build.log
```
会生成 `bootable/bootloader/preloader/bin` 

2. build 脚本编译：
```
cd bootable/bootloader/preloader
TARGET_PRODUCT=$op_project_name ./build.sh 2>&1 | tee preloader_build.log
```

**lk:**
```
make -j4 lk 2>&1 | tee lk_build.log
```
会生成 `bootable/bootloader/lk/build-xx`

**Kernel:**
1. 单独编译
```
cd kernel-3.18
mkdir out
make -j4 O=out 2>&1 | tee kernel_build.log
```
会生成  kernel-3.18/out/arch/arm64/boot/Image.gz-dtb

2. build 脚本编译
```
make -j8 n k && make -j8 r bootimage
```

**clean:**
```
# Clean ALL
make clean
# Clean PL
make clean-pl
# Clean lk
make clean-lk
# Clean kernel
make clean-kernel
```

#### Android 编译
```
# 1. 环境变量
source build/envsetup.sh
# 2. 选择工程
lunch full_bd6737m_35g_b_m0-eng
# 3. MTK 环境变量
source mbldev.sh
# 4. 编译
make -j4 2 > &1 | tee mtk_build.log
```
#### 打包
```
# pack boot image
make -j4 bootimage

# pack system image 根据依赖规则重新生成所有要打包的文件
make -j4 systemimage

# pack system image 快速打包 system image
# （如果所修改模块与其他模块没有依赖关系，直接 build 对应模块并用 snod 命令打包）
make -j4 snod 

# pack ota image
make -j4 otapackage
```

## 硬件参数

https://versus.com/en/mediatek-mt6735-vs-mediatek-mt6737

#### MTK6737
4 x 1.3GHz   28nm
LTE supported
GPU: MailT720

#### Check SDK Version
```
vi build/core/version_defaults.mk

  PLATFORM_VERSION := 6.0    
  PLATFORM_SDK_VERSION := 23   #Android6.0
  
vi kernel/Makefile
VERSION = 3
PATCHLEVEL = 18
SUBLEVEL = 19
```

### 编译中碰到的问题
#### clang 问题
```
clang: error: linker command failed with exit code 1 (use -v to see invocation)
build/core/host_shared_library_internal.mk:51: recipe for target 'out/host/linux-x86/obj/lib/libart.so' f
ailed
make: *** [out/host/linux-x86/obj/lib/libart.so] Error 1
```
解决方法：
代码 `art/build/Android.common_build.mk` 中
```
   # By default, host builds use clang for better warnings.
--  ART_HOST_CLANG := true
++  ART_HOST_CLANG := false
```

#### STATIC_LIBRARIES  SHARED_LIBRARIES 类型的问题
比如下面这些
```
make: *** No rule to make target 'out/target/product/bd6737m_35g_b_m0/obj/STATIC_LIBRARIES/libcam.halmemory_intermediates/export_includes', needed by 'out/target/product/bd6737m_35g_b_m0/obj/SHARED_LIBRARIES/libcam_platform_intermediates/import_includes'。 停止。
make: *** 正在等待未完成的任务....
target thumb C++: libcam.device3.base <= vendor/mediatek/proprietary/hardware/mtkcam/legacy/v3/device/Cam3DeviceFactory.cpp
```

```
make: *** No rule to make target 'out/target/product/bd6737m_35g_b_m0/obj/STATIC_LIBRARIES/libcam.halmemory_intermediates/export_includes', needed by 'out/target/product/bd6737m_35g_b_m0/obj/SHARED_LIBRARIES/libcam_platform_intermediates/import_includes'。 停止。
make: *** 正在等待未完成的任务....
target StaticLib: libcam.device3.base (out/target/product/bd6737m_35g_b_m0/obj/STATIC_LIBRARIES/libcam.device3.base_intermediates/libcam.device3.base.a)
```
可以参考 安装编译环境依赖包 进行安装必要的包


## 烧录

Linux 下的烧录工具为 SP_Flash_Tool_v5.1644_Linux.zip
使用方法：http://spflashtools.com/linux/sp-flash-tool-v5-1644-linux

