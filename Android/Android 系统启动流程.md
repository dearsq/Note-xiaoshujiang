---
title: Android 启动流程
tags:
grammar_cjkRuby: true
---
[TOC]

## 一、Android 底层启动流程
### 1. 系统上电并执行 ROM 引导代码
#### 1.1 由 PC 引出 Android 
PC 系统启动机制我们比较熟悉。
1. 系统上电
2. BIOS 被载入到硬盘的扇区 MBR
3. 运行启动程序 BIOS 并开始引导系统
Android 系统很类似
#### 1.2 Android 底层启动流程
1. CPU 上电
2. PC 指针指向 ROM 启动代码（零地址），即 Bootloader
3. 直接执行启动代码 / 将代码载入到 RAM 后执行
两种执行方式取决于是由 Nor Flash 还是 Nand Flash 存储 Bootloader。
#### 1.3 Nor Flash 与 Nand Flash 中的 Bootloader
Nor Flash 支持字节寻址，可以直接在 ROM 中执行。
Nand Flash 不支持字节寻址，需要将 Bootloader 加载到 RAM 中后才能执行。
具体 Bootloader 的定义和种类放在下一节细表。
##### Nor Flash
1. 上电后，PC 指向 ROM 的零地址，开始执行Bootloader（汇编部分）
2. 配置 EMI 寄存器（存储器地址 & 存取规则）
3. 配置电源模块，使各个模块上电
4. 为了提高执行效率，将 Nor Flash 中的代码复制到内存中
5. PC 指针指向 RAM 中映射的地址，并开始执行 Bootloader（c 部分）
##### Nand Flash
1. 上电后，DMA 将 Nand Flash 中的 Bootloader 启动代码复制到 **CPU 内部的 RAM** 中
2.  PC 指向 RAM 代码的首地址，执行 Bootloader（汇编部分）
3.  Bootloader 中设置中断向量和设置硬件配置
4.  计算 Bootloader 大小，预留空间，将执行代码搬运到 SDRAM 或者 DD-RAM 等**外部 RAM** 中。
5.  设置 Remap，映射 零地址 到 SDRAM 或者 DDRAM 中的首地址
6.  设置 PC 指针到 零地址，开始执行 Bootloader（c 部分）

### 2. Bootloader 引导程序
#### 2.1 作用
**简单地说**，BootLoader是在操作系统运行之前运行的一段程序，它可以将系统的软硬件环境带到一个合适状态，为运行操作系统做好准备。
**微观地说**，Bootloader 负责初始化硬件设备，建立内存空间映射图，为内核启动准备好软件、硬件环境。

Bootloader 阶段通常都包含有处理器厂商开发的上电引导程序 + u-boot（一个通用的 Bootloader）。
#### 2.2 处理器厂商的上电引导程序
不同厂商可能会自己定制一部分内容（对 arm core 进行封装），差异比较大，所以不同的arm处理器，对于上电引导都是由特定处理器芯片厂商自己开发的程序，这个上电引导程序通常比较简单，会初始化硬件，提供下载模式等，然后才会加载通常的 Bootloader（u-boot）。
#### 2.3 U-boot
u-boot 大致包括两个阶段，汇编代码（start.S） & C 代码。

### 3. Linux 内核
#### 3.1 内核（Kernel）的启动流程
1. Kernel 初始化
2. 设备驱动初始化
3. Kernel 启动
4. 挂载文件系统
5. 启动用户空间进程
#### 3.2 Kernel 初始化




### 4. init 初始化系统服务
## 二、Android 上层启动流程
### 1. 上层系统启动简介
### 2. 启动 Native Service 本地服务
### 3. Zygote 进程启动
### 4. Android SystemService 启动
### 5. 启动 HomeActivity 主界面



### （一）系统上电
#### Android 系统执行的操作
上电流程：CPU 上电 ——> PC 指向 ROM 启动代码零地址 ——> 执行将启动代码载入 RAM 后执行。
CPU 上电：Android 系统的







## 参考文献
[1][Android系统启动流程 -- bootloader](http://blog.csdn.net/lizhiguo0532/article/details/7017503)