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
