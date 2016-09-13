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
1. 上电后，PC 指向 ROM 的零地址，开始执行 bootloader（汇编部分）
2. 配置 EMI 寄存器（存储器地址 & 存取规则）
3. 配置电源模块，使各个模块上电
4. 为了提高执行效率，将 Nor Flash 中的代码复制到内存中
5. 将启动代码的


### 2. Bootloader 引导程序
#### 2.1 定义和种类
简单地说，BootLoader是在操作系统运行之前运行的一段程序，它可以将系统的软硬件环境带到一个合适状态，为运行操作系统做好准备。
Bootloader 阶段通常都包含有处理器厂商开发的上电引导程序 + u-boot（一个通用的 Bootloader）。
u-boot 大致包括两个阶段，汇编代码（start.S） & C 代码。
### 3. Linux 内核
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