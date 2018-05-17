---
title: [RK3399][Android6.0] Uboot 编译规则
tags: 
grammar_cjkRuby: true
---

Author: Younix 
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.07

[TOC]

RK 的文档中有说到 其 Uboot 是给予 2014.10 官方版本进行开发的，同步更新了主分支的一些关键性更新。

## 一、Uboot 的编译
编译 Uboot 我们所采用的命令如下：
```
make rk3399_defconfig
make ARCHV=aarch64
```
我们从编译命令入手，分析 Uboot。

### Uboot 配置文件 ×_defconfig
`rk3399_defconfig` 为 uboot 的配置文件，uboot 的配置文件都在 configs 中
```bash
➜  u-boot git:(fcfc325) ls configs/rk3399*
configs/rk3399_box_defconfig  configs/rk3399_defconfig  configs/rk3399-fpga_defconfig
```
可以看到一共有三种形态，BOX、MID、FPGA。
首先以 rk3399_defconfig 为例：
```
CONFIG_SYS_EXTRA_OPTIONS="RKCHIP_RK3399,PRODUCT_MID,NORMAL_WORLD,SECOND_LEVEL_BOOTLOADER,BAUDRATE=1500000"
# RKCHIP_RK3399 定义芯片类型
# PRODUCT_MID 定义产品形态
# NORMAL_WORLD 定义 Uboot 运行在 Normal World
# SECOND_LEVEL_BOOTLOADER 定义 Uboot 为二级 loader 模式（采用 Nand Flash 的项目以安全框架驱动时，需要定义该选项。
CONFIG_ARM=y
CONFIG_ROCKCHIP_ARCH64=y
CONFIG_PLAT_RK33XX=y
```
> 该选项内的配置会被优先编译成宏定义并在相关的项前面自动添加 CONFIG_,可以在
U-BOOT 自动生成的配置文件 (include/config.h) 中看到生成的宏定义,会优先系统的配置文件,
可以支配系统的配置文件。

什么意思呢，比如说 PRODUCT_MID ，他会被加上 CONFIG_ 成为 CONFIG_PRODUCT_MID 被定义。
然后通过这个宏来控制一些功能的开关。
正好，我们也可以对比看看 BOX 形态的产品的 configs：
我们对比 BOX 和 MID 的 configs 可以发现
```
➜  configs git:(fcfc325) diff rk3399_box_defconfig rk3399_defconfig 
1c1
< CONFIG_SYS_EXTRA_OPTIONS="RKCHIP_RK3399,PRODUCT_BOX,NORMAL_WORLD,SECOND_LEVEL_BOOTLOADER,BAUDRATE=1500000"
---
> CONFIG_SYS_EXTRA_OPTIONS="RKCHIP_RK3399,PRODUCT_MID,NORMAL_WORLD,SECOND_LEVEL_BOOTLOADER,BAUDRATE=1500000"
```
即在 CONFIG_SYS_EXTRA_OPTIONS 参数中的 PRODUCT_* 有差别
全局搜索 PRODUCT_BOX 根据 PRODUCT_BOX、PRODUCT_MID 的差别会影响部分功能的开关。
比如 ./include/configs/rk33plat.h:375 中
```
/* if box product, undefine fg and battery */
#ifndef CONFIG_PRODUCT_BOX
#define CONFIG_POWER_FG
#define CONFIG_POWER_BAT
#endif /* CONFIG_PRODUCT_BOX */
```
比如 ./include/configs/rk_default_config.h: 中，BOX 形态不需要电源管理系统，需要 HDMI 和 TVE
```
#ifndef CONFIG_PRODUCT_BOX
/* rk pm management module */
#define CONFIG_PM_SUBSYSTEM
#endif

#ifdef CONFIG_PRODUCT_BOX
/* rk deviceinfo partition */
#define CONFIG_RK_DEVICEINFO

/* rk pwm remote ctrl */
#define CONFIG_RK_PWM_REMOTE
#endif

#ifndef CONFIG_PRODUCT_BOX
#define CONFIG_RK_PWM_BL
#endif

#ifdef CONFIG_PRODUCT_BOX
#define CONFIG_RK_HDMI
#define CONFIG_RK_TVE
#endif
```
### Uboot 配置文件 rk33plat.h
其中有关键性的系统配置
```
 55  *              define uboot loader addr.
 56  * notice: CONFIG_SYS_TEXT_BASE must be an immediate,
 57  * so if CONFIG_RAM_PHY_START is changed, also update CONFIG_SYS_TEXT_BASE define.
 58  *
 59  * Resersed 2M space(0 - 2M) for Runtime ARM Firmware bin, such as bl30/bl31/bl32 and so on.
 60  *
 61  */
 62 #ifdef CONFIG_SECOND_LEVEL_BOOTLOADER
 63        #define CONFIG_SYS_TEXT_BASE    0x00200000 /* Resersed 2M space Runtime Firmware bin. */
 64 #else
 65        #define CONFIG_SYS_TEXT_BASE    0x00000000
 66 #endif
```

### 交叉编译工具链
`ARCHV=aarch64` 指明了 rk3399 的平台架构，在 Makefile 中会根据其指定编译工具链。
交叉编译工具链的指定是由 CROSS_COMPILE 宏确定，可以在 make 的时候声明。
```makefile
ifeq ($(ARCHV),aarch64)

ifneq ($(wildcard ../toolchain/aarch64-linux-android-4.9),)
CROSS_COMPILE   ?= $(shell pwd)/../toolchain/aarch64-linux-android-4.9/bin/aarch64-linux-android-
endif
ifneq ($(wildcard ../prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin),)
CROSS_COMPILE   ?= $(shell pwd)/../prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-
endif

else

ifneq ($(wildcard ../toolchain/arm-eabi-4.8),)
CROSS_COMPILE   ?= $(shell pwd)/../toolchain/arm-eabi-4.8/bin/arm-eabi-
endif
ifneq ($(wildcard ../toolchain/arm-eabi-4.7),)
CROSS_COMPILE   ?= $(shell pwd)/../toolchain/arm-eabi-4.7/bin/arm-eabi-
endif
ifneq ($(wildcard ../toolchain/arm-eabi-4.6),)
CROSS_COMPILE   ?= $(shell pwd)/../toolchain/arm-eabi-4.6/bin/arm-eabi-
endif
ifneq ($(wildcard ../prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/bin),)
CROSS_COMPILE   ?= $(shell pwd)/../prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/bin/arm-eabi-
endif
ifneq ($(wildcard ../prebuilts/gcc/linux-x86/arm/arm-eabi-4.7/bin),)
CROSS_COMPILE   ?= $(shell pwd)/../prebuilts/gcc/linux-x86/arm/arm-eabi-4.7/bin/arm-eabi-
endif
ifneq ($(wildcard ../prebuilts/gcc/linux-x86/arm/arm-eabi-4.6/bin),)
CROSS_COMPILE   ?= $(shell pwd)/../prebuilts/gcc/linux-x86/arm/arm-eabi-4.6/bin/arm-eabi-
endif

endif # ARCHV=aarch64
```
因为 RK3399 ARCHV==aarch64, 所以编译工具链为 4.9 版本
```makefile
ifneq ($(wildcard ../toolchain/aarch64-linux-android-4.9),)
CROSS_COMPILE   ?= $(shell pwd)/../toolchain/aarch64-linux-android-4.9/bin/aarch64-linux-android-
endif
ifneq ($(wildcard ../prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin),)
CROSS_COMPILE   ?= $(shell pwd)/../prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9/bin/aarch64-linux-android-
endif
```

## 二、Uboot 目录结构
```
include/configs/rk_default_config.h: 
rk平台公共配置，默认打开所有需要的功能

include/configs/rk33plat.h: 
rk33xx系列平台配置，根据不同的芯片进行细节配置，比如内存地址、简配一些功能模块的配置

arch/arm/include/asm/arch-rk33xx/: 
rk33xx系列平台架构头文件

arch/arm/cpu/armv8/rk33xx/: 
rk33xx系列平台架构文件, 包括clock, irq, timer等实现。

board/rockchip/rk33xx: 
板级平台核心文件，主要是rk33xx.c，里面有熟悉的kernel要用的machine type.

drivers: 
各种接口驱动文件，如lcd, rtc, spi, i2c,usb等驱动。
```

## 三、RK 平台 Uboot 	生成方式
RK Uboot 有两种生成方式。参看 RK wiki。
一种是 Uboot 作 first level bootloader，比如原来的 RK3288 平台，这种情况下，uboot 生成的固件为单独的 .bin 文件， RK3288UbootLoader_V2.30.10.bin 。
另一种是 Uboot 作为 second level bootloader，比如 RK3399 平台，这种情况下，uboot 生成的固件为 .img，比如 uboot.img。

在 Uboot 的代码中，configs/rk3399_defconfig 中有定义
```
CONFIG_SYS_EXTRA_OPTIONS="RKCHIP_RK3399,PRODUCT_MID,NORMAL_WORLD,SECOND_LEVEL_BOOTLOADER,BAUDRATE=1500000"
```
我们可以通过设置 CMDLINE 中的 CONFIG_SECOND_LEVEL_BOOTLOADER 宏来控制是否将其作为 second level bootloader。
CONFIG_SECOND_LEVEL_BOOTLOADER 会打开 CONFIG_MERGER_MINILOADER 宏。
它控制的功能是合并 MINIALL.ini 配置文件（tools/rk_tools/RKBOOT/RK3399MINIALL.ini ）与 miniloader.bin（tools/rk_tools/bin/rk33/rk3399_miniloader_v1.06.bin ），最终输出为 rk3399_loader_v1.08.106.bin。
代码逻辑如下：
```
ifdef CONFIG_SECOND_LEVEL_BOOTLOADER
    $(if $(CONFIG_MERGER_MINILOADER), ./tools/boot_merger ./tools/rk_tools/RKBOOT/$(RKCHIP)MINIALL.ini &&) \
    $(if $(CONFIG_MERGER_TRUSTIMAGE), ./tools/trust_merger $(if $(CONFIG_RK_TRUSTOS), --subfix) \
                            ./tools/rk_tools/RKTRUST/$(RKCHIP)TRUST.ini &&) \
    $(if $(CONFIG_MERGER_TRUSTOS), ./tools/loaderimage --pack --trustos $(RK_TOS_BIN) trust.img &&) \
    ./tools/loaderimage --pack --uboot u-boot.bin uboot.img
else
    ./tools/boot_merger --subfix "$(RK_SUBFIX)" ./tools/rk_tools/RKBOOT/$(RKCHIP).ini
endif # CONFIG_SECOND_LEVEL_BOOTLOADER
```
