---
title: [IoT4G] MTK DCT 工具介绍
tags: 
grammar_cjkRuby: true
---


OS:Android6.0
Hardware:MTK6737

[TOC]


## MTK 的 DCT
Driver Customization Tool
MTK 为 GPIO、I2C 等配置制作了一个工具叫做 **DCT** ， 可以直接在 UI 里面配置好 I2C 相关定义（codegen.dws 文件中），配好后编译会自动生成一些相关的 DTS 文件和头文件（如 cust_i2c.dtsi）。

### 运行流
该工具的运行流如下：
1. 硬件原理图 
2. 描述硬件配置的 Excel
3.1 SA / Baseband 工程师 负责在 DCT 中 Key in
3.2 描述文件（.fig .cmp）将被加载到 DCT 中
4. DCT 将生成定制化的源码（.c .h） 也将生成 工程文件（.dws）

### .fig 为芯片级定制文件（比如 mt6737.fig）
其中将描述和这个芯片相关的硬件定制信息，比如
1. GPIO pin 数，支持的 mode，上拉下拉状态
2. ADC 通道个数
3. 外部中断管脚
4. 矩阵键盘大小

### .cmp 为元件描述文件（比如 \*.cmp）
对于每个 DCT 所支持的元件（比如 GPIO EINT ADC keypad 和 UEM），都会有一个元件变量文件

### DCT 文件清单
工具在如下目录中
./vendor/mediatek/proprietary/bootable/bootloader/preloader/tools/dct
./vendor/mediatek/proprietary/bootable/bootloader/lk/scripts/dct
./kernel-3.18/tools/dct

配置文件在如下目录
Codegen.dws
Preloader: bootable/bootloader/preloader/custom/${PROJECT}/dct/dct
LK: bootable/bootloader/lk/target/${PROJECT} /dct/dct
Kernel: kernel-3.10/drivers/misc/mediatek/mach/mt6735/${PROJECT}/dct/dct
Vendor: vendor/mediatek/proprietary/custom/ ${PROJECT}/kernel/dct
比如：
./vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/bd6737m_35g_b_m0/dct/dct/codegen.dws
./vendor/mediatek/proprietary/bootable/bootloader/lk/target/bd6737m_35g_b_m0/dct/dct/codegen.dws
./kernel-3.18/drivers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws
./vendor/mediatek/proprietary/custom/bd6737m_35g_b_m0/kernel/dct/dct/codegen.dws
其中所有的 codegen.dws 应该完全相同。

