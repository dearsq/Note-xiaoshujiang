---
title: [IoT3G] MTK 开发环境搭建
tags: Bug,Android
grammar_cjkRuby: true
---
Hardware: MTK6572
Android: 4.4(API 19)
Kernel: Linux 3.4.67

#### **Check SDK Version**

```
vi build/core/version_defaults.mk

  PLATFORM_VERSION := 4.4.2    
  PLATFORM_SDK_VERSION := 19   #Android4.4
  
vi kernel/Makefile
VERSION = 3
PATCHLEVEL = 4
SUBLEVEL = 67
```

#### 安装编译环境

对于Ubuntu14.04 
需要安装 openjdk-6-jdk （jdk1.6）
```
sudo apt install openjdk-6-jdk
sudo update-alternatives --config java
There are 4 choices for the alternative java (providing /usr/bin/java).

  Selection    Path                                                 Priority   Status
------------------------------------------------------------
* 0            /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java        1071      auto mode
  1            /usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java        1061      manual mode
  2            /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java        1071      manual mode
  3            /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java        1069      manual mode
  4            /xspace/Public/App/Java1.6_SDK/jdk1.6.0_31/bin/java   300       manual mode
```

需要 gcc4.4
```
## 安装 gcc4.4
$ sudo apt install gcc-4.4
## 查看系统内现有 gcc 版本并切换
$ ls /usr/bin/gcc-4*
/usr/bin/gcc-4.4  /usr/bin/gcc-4.6  /usr/bin/gcc-4.8

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.4 50

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.6 40

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 20

$ sudo update-alternatives --config gcc
There are 3 choices for the alternative gcc (providing /usr/bin/gcc).

  Selection    Path              Priority   Status
------------------------------------------------------------
* 0            /usr/bin/gcc-4.4   50        auto mode
  1            /usr/bin/gcc-4.4   50        manual mode
  2            /usr/bin/gcc-4.6   40        manual mode
  3            /usr/bin/gcc-4.8   20        manual mode

Press enter to keep the current choice[*], or type selection number: 
```
这里我们要选 gcc 4.4。



#### MTK 原生编译命令

```
./mk --help
```

#### 脚本编译

```
$ cd /orangepi/scripts/
$ ./auto.sh IoT03_mt6572_emmc_b1258_32g4g_ry_smt v00 eng

```