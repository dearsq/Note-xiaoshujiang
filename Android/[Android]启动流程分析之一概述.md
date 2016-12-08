---
title: [Android]启动流程分析之一概述
tags: Android
grammar_cjkRuby: true
---
Android启动流程如下图：

![Android启动流程图][1]

  [1]: ./images/1481162352165.jpg "Android 启动流程图"

总得来看有这样几个阶段：
1. BootROM 上电
2. BootLoader 引导
3. Linux 内核
4. init 进程
5. Native 服务启动
6. System Server、Android Service 启动
7. Home Launcher 启动


## BootROM
按下电源后，引导芯片代码从预定义的地方（固化在 ROM）开始执行。
加载引导程序到 RAM，然后执行引导程序（bootloader）。

## Bootloader 引导程序
Bootloader 有很多，最常见的就是 uboot。

引导程序分为两个阶段：
1. 检测外部的 RAM 以及加载对第二阶段有用的程序。
2. 引导程序设置网络、内存等等。这些对于运行内核是必要的，为了达到特殊的目标，引导程序可以根据配置参数或者输入数据设置内核。

## Linux 内核

## init 进程
init 进程是用户态所有进程的祖先。
作用：
1. 子进程终止处理。
2. 应用程序访问设备驱动时，生成设备结点文件。
3. 提供属性服务，保存系统运行所需要的环境变量。


init 进程先 fork() 来创建子进程
**首先 fork 出 Daemon 进程（守护进程）。** 包括 USB 守护进程、Debug 进程、无线通信连接守护进程;
**然后 fork 出 Context Manager。** Android System 提供的所有 Service 都需要 Context Manager 注册，然后其他的进程才能够调用这个服务。
**然后 fork 出 Media Server。** 这是 Native 服务，不是 Java 服务，所以不需要 VM。包括 Audio Flinger、Camera Service。
**然后 fork 出 Zygote。** 和它的中文（受精卵）一样，它是所有 Android 应用程序的祖先。用它来孵化 Java 系统服务，同时孵化应用程序。
### Zygote 孵化出 System Server 和 App
它是 Android System 的核心进程，提供了应用程序声明周期管理，地理位置信息等各种 Service（这些 Service 同样需要注册到 Context Manager）。






  ## 参考
  1. 《Android启动过程深入解析》 http://blog.jobbole.com/67931/
  2. 