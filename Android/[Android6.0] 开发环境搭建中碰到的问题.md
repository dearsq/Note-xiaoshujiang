---
title: [Android6.0] 开发环境搭建中碰到的问题
tags: Bug,Android
grammar_cjkRuby: true
---


OS：Ubuntu16.04

[TOC]

## 参考文献

http://blog.csdn.net/fuchaosz/article/details/51487585
这篇文章中涵盖了大部分编译问题


## 问题汇总

### clang: error: linker command failed with exit code 1

解决方法：
代码 `art/build/Android.common_build.mk` 中
```
-- ifneq ($(WITHOUT_HOST_CLANG),true)
++ ifneq ($(WITHOUT_HOST_CLANG),false)
```


### 中文路径问题
SDK 路径中请不要包含中文