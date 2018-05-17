---
title: [Android6.0][RK3399] 开发环境搭建中碰到的问题
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
   # By default, host builds use clang for better warnings.
--  ART_HOST_CLANG := true
++  ART_HOST_CLANG := false
```


### 中文路径问题
SDK 路径中请不要包含中文


### RK upgrade_tool 
```
./upgrade_tool: error while loading shared libraries: libudev.so.1: cannot open shared object file: No such file or directory
```
```
sudo apt-get install libudev-dev
```
not work
```
➜  rockdev sudo dpkg -S libudev | grep libudev.so
libudev1:amd64: /lib/x86_64-linux-gnu/libudev.so.1.6.4
libudev-dev:amd64: /usr/lib/x86_64-linux-gnu/libudev.so
libudev1:amd64: /lib/x86_64-linux-gnu/libudev.so.1
```
```
➜  x86_64-linux-gnu ls -al libudev.so.1
lrwxrwxrwx 1 root root 16 10月 27 18:12 libudev.so.1 -> libudev.so.1.6.4
```

Dont do this:
```
sudo ln -sf /lib/x86_64-linux-gnu/libudev.so.0 /lib/x86_64-linux-gnu/libudev.so.1
```

