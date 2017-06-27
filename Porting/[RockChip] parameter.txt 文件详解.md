---
title: [RockChip] parameter.txt 文件详解
tags: RockChip
grammar_cjkRuby: true
---

Platform: RK3399
OS: Android 6.0
Version: v2016.08

[TOC]

Parameter 最大为 64KB。
其中的参数由 Bootloader 解析。

## parameter 分析

固件版本，打包 update.img 用到。升级工具据此识别固件版本
**FIRMWARE_VER: 6.0.1**
#机型，打包 update.img 用到。用于升级工具显示。
**MACHINE_MODEL: RK3399**
#产品ID，为数字或字母组合，打包 update.img 使用。
**MACHINE_ID: 007**
#机型，打包 update.img 用到。用于升级工具显示。
**MANUFACTURER: RK3399**
#无法修改
**MAGIC: 0x5041524B**
#无法修改
**ATAG: 0x00200800**
#无法修改，内核识别用
**MACHINE: 3399**
#无法修改
**CHECK_MASK: 0x80**

#PWR_HLD:0,0,C,7,1 //控制 GPIO0C7 输出高电平
#PWR_HLD:0,0,C,7,2 //控制 GPIO0C7 输出低电平
#PWR_HLD:0,0,A,0,3 //配置 PWR_HLD 为 GPIO0A0,在 Loader 需要锁定电源时,输出高电平锁定电源
最后一位是电平判断，解释:
1:= 解析 parameter 时,输出高电平
2:= 解析 parameter 时,输出低电平
3:= 在 Loader 需要控制电源时,输出高电平
0:= 在 Loader 需要控制电源时,输出低电平
这里是控制 GPIO0 A0 输出高电平
**PWR_HLD: 0,0,A,0,1**

#内核地址，bootloader 将加载此地址，如果 kernel 编译地址改变，需要修改此值
**#KERNEL_IMG: 0x00280000**

**#FDT_NAME: rk-kernel.dtb**
#按键类型 0 普通按键，GPIO 定义 （三位），电平判断
比如 0,4,C,5,0 代表 普通按键，GPIO4 C5, 低电平有效
#按键类型 1 AD按键，AD 定义 （三位），保留
比如 1,1,0,20,0 代表 AD按键，ADC 通道，下限值为 00，上限值为 200 即 AD值在 0～200 之间的按键都认为是 RECOVER_KEY
**#RECOVER_KEY: 1,1,0,20,0**

**#in section; per section 512(0x200) bytes**
**CMDLINE:**
**androidboot.baseband=N/A**
**androidboot.selinux=disabled** 安全强化 Linux 是否打开
**androidboot.hardware=rk30board** 硬件平台
**androidboot.console=ttyFIQ0** 串口定义
**init=/init**
#MTD分区 RK30xx、RK29xx 和 RK292x 都是用 rk29xxnand 做标识
**mtdparts=rk29xxnand:0x00002000@0x00002000(uboot),0x00002000@0x00004000(trust),0x00002000@0x00006000(misc),0x00008000@0x00008000(resource),0x00008000@0x00010000(kernel),0x00010000@0x00018000(boot),0x00010000@0x00028000(recovery),0x00038000@0x00038000(backup),0x00040000@0x00070000(cache),0x00200000@0x000B0000(system),0x00008000@0x002B0000(metadata),0x00002000@0x002B8000(baseparamer),-@0x002BA000(userdata)**

@符号前是分区的大小
@符号后是分区的起始地址
括号中是分区的名字
单位都是 sector（512Bytes）
比如 uboot 起始地址为 0x2000 sectors （4MB）的位置，大小为 0x2000 sectors（4M）
另外 flash 最大的 block 是 4M（0x2000 sectors），所以每个分区需要 4MB 对齐，即每个分区必须为 4MB 的整数倍。

,0x00038000@0x00038000(backup)
backup 分区前的分区为固件区 uboot、trust、misc、resource、kernel、boot、recovery 。
后续升级时不能修改分区大小
backup 分区后的分区 cache、system、metadata、baseparamer、userdata
是可以读写的，可以调整分区大小。但是修改分区大小后需要进入 recovery 系统格式化 cache

## 常见问题
### 1. system 分区改为 ext3 后，parameter 中 mtd 分区如何定义
ext3 为可写文件系统，system 分区需要定义在 backup 后。
### 2. 系统固件变大，backup 分区起始位置和大小变大，系统异常
backup 之前的分区只可改小，不可变大，所以请预留足够空间。
出现问题后，按住 recovery 进入 loader 升级模式，“修复模式升级固件” 或者 擦出 idb 功能低格 flash 后再升级。
另外现在 backup 已经不再备份 system.img 了。
