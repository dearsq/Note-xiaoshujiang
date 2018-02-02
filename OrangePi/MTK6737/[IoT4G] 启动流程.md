---
title: [IoT4G] 启动流程
tags: 
grammar_cjkRuby: true
---

OS:Android6.0
Hardware:MTK6737

[TOC]

## 启动流程概览

### BootRom
固化在 CPU 内部。
负责从外部的存储器中加载 Preloader。
负责 USB Download。

### Preloader
属于 Bootloader 的第一部分。
负责 MTK Licensed
负责 基础 Module 的 初始化，比如 eMMC，PLL，DRAM 等。
负责 加载 LittleKernel（LK）

### LK
属于 Bootloader 的第二部分。
负责 设备的初始化。
负责 加载 Linux Kernel。
支持 fastboot 更新。

### Kernel
负责 设备初始化 / 内核初始化。
负责 引导启动内核态 init 进程。

### Android
负责 引导启动用户态 init 进程。
负责 Zygote 启动。
负责 Framework 初始化等。

![](http://ww1.sinaimg.cn/large/ba061518ly1fnqiixhnp3j20gs0bfjts.jpg)


以上基本可以化为三个部分：Bootloader（Preloader+LK）、Kernel、Android。
后面我们深入代码逐个分析。