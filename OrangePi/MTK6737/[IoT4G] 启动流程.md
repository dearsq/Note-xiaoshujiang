---
title: [IoT4G] 启动流程
tags: 
grammar_cjkRuby: true
---

OS:Android6.0
Hardware:MTK6737

[TOC]

## 一、启动流程概览

### 1. BootRom
固化在 CPU 内部。
负责从外部的存储器中加载 Preloader。
负责 USB Download。

### 2. Preloader
属于 Bootloader 的第一部分。
负责 MTK Licensed
负责 基础 Module 的 初始化，比如 eMMC，PLL，DRAM 等。
负责 加载 LittleKernel（LK）

### 3. LK
属于 Bootloader 的第二部分。
负责 设备的初始化。
负责 加载 Linux Kernel。
支持 fastboot 更新。

### 4. Kernel
负责 设备初始化 / 内核初始化。
负责 引导启动内核态 init 进程。

### 5. Android
负责 引导启动用户态 init 进程。
负责 Zygote 启动。
负责 Framework 初始化等。

![](http://ww1.sinaimg.cn/large/ba061518ly1fnqiixhnp3j20gs0bfjts.jpg)


以上基本可以化为三个部分：Bootloader（Preloader+LK）、Kernel、Android。
后面我们深入代码逐个分析。

## 二、Bootloader 引导
Bootloader 部分主要功能包括 设置处理器和内存频率、指定调试信息端口、可引导的存储设备等。完成可执行环境创建后，把 software 装载到内存并执行。除了装载 software ，外部工具也可以和 bootloader 握手，指示设备进入不同的操作模式（比如 USB 下载模式和 META 模式）。就算没有外部工具的握手，也可以通过自定义按键，使 bootloader 进入这些模式。

由于不同芯片商对 arm core 封装差异比较大，所以不同的 arm 处理器,对于上电引导都是由特定处理器芯片厂商自己开发的程序,这个上电引导程序通常比较简单,会初始化硬件,提供下载模式等,然后才会加载通常的 bootloader （uboot）。

对于 MTK 平台，其 bootloader 分为两个部分
1. preloader ，依赖平台
2. LK（little kernel），作用和 uboot 类似，依赖操作系统，负责引导 linux 系统和 Android 框架

![](http://ww1.sinaimg.cn/large/ba061518ly1fo1w4c5g6dj20md0llthr.jpg)

我们结合前面的那张图，更加详细的看一下**启动过程**中 Bootloader 部分的动作：
1. 设备上电，BootROM 开始运行。
2. BootROM 初始化软件堆栈 （SoftwareStack）、通信端口和可引导存储设备（NAND/EMMC）。
3. BootROM 从存储器中加载 pre-loader 到内部 SRAM（ISRAM）中，因为这时候还没有初始化外部的 DRAM。
4. BootROM 跳转 pre-loader 入口并执行。
5. pre-loader 初始化 DRAM 并加载 u-boot 到 RAM中
6. pre-loader 跳转到 u-boot 中执行，u-boot 开始做初始化，比如显示初始化
7. u-boot 从存储器中加载引导镜像（boot image）包括 linux kernel 和 ramdisk
8. u-boot 跳转到 linux kernel 并执行。

### 2.1 preloader 启动过程
#### 2.1.1 preloader 的功能
1. 负责在芯片组平台准备好可执行环境
2. 如果检测到外部工具，会试图通过 uart 或者 usb 与外部工具握手
3. 从 NAND/EMMC 加载 u-boot ，并跳转到 u-boot
4. 使用工具握手,设备能够触发进入下载模式来下载需要的镜像,或是进入工厂/测试模式,比如 META 模式和 ATE 工厂模式,在这些模式下可以测试模块,或是通过传递引导参数给 U-Boot 和 linux kernel 来校准设备 (device calibration)
#### preloader 中的硬件部分
**PLL 模块**
调整处理器和外部内存频率。PLL 模块初始化后，处理器和外部内存的频率由 26MHZ/26MHZ 增加到 1GHZ/192MHZ。

**UART 模块**
用于调试或是 META 模式下的握手。
默认情况下 UART4 初始化波特率为 9216000bps ，用于调试信息输出。
UART1 初始化为 115200bps 和作为 UART META 默认端口。不过 UART1 也可以被作为调试或者是 UART META 端口。

**计时器 timer 模块**
用于计算硬件模块所需要的延时或是超时时间。

**内存模块**
preloader 由 bootROM 加载和芯片组内部的 SRAM 中执行，因为外部的 DRAM 还没有初始化。
接下来 preloader 采用内置的内存设置来初始化 DRAM，这样 u-boot 就可以被加载到 DRAM 中并执行。

**GPIO**

**PMIC**

**RTC**
当通过 power 按键开机后，preloader 拉高 RTC 的 PWBB 来保持设备一直有电，并继续引导 u-boot。
RTC alarm 可能是设备开机的启动源，这种情况，设备不需要按 power 按键就可以自启动。

**USB**

**NAND**

**MSDC**
pre-loader 可以从 NAND Flash 或者是 EMMC 中加载 u-boot，两种选其一
#### 2.1.2 preloader 启动代码
代码流程如下图：

![](http://ww1.sinaimg.cn/large/ba061518ly1fo1wuezzjxj20mv0l8wk5.jpg)


### 2.2 LK 启动过程
LK （Little Kernel）也是一种 bootloader ，作用和 u-boot 差不多。
MTK它由 preloader 引导并执行，因为 preloader 中已经完成了硬件模块，所以不需要在 lk 中重新配置这些模块了。但部分模块会在 lk 中重新被复位来配置硬件寄存器，这样可以创造一个干净的环境。比如计时器模块，在 lk 中，timer 被重新复位清零硬件计数来对计时进行复位。

#### 2.2.1 LK 中的上电情景
LK 加载后，电池将检查 power 按键是否按下，
如果当前启动的原因是 USB 充电器，而不是 power 按键，电池模块将等待用户按下 power 按键启动;
```
// lk/platform/mt6735/mtk_key.c
BOOL mtk_detect_key(unsigned short key)  /* key: HW KeyCode */
```
`key` 表示要检查的按键码，返回值表示这个按键是否按下，此函数来判断指定的按键是否按下。

#### 2.2.2 LK 中的充电情景

![](http://ww1.sinaimg.cn/large/ba061518ly1fo227amhrrj20tv0mgakl.jpg)

#### 2.2.3 LK 中的其他启动模式
**Factory mode**
出厂模式，用于批量生产

**META mode**
META 模式，用于批量生产的功能性测试

**Advanced META mode**
META 高级模式，用于批量生产时的功能性测试，用以测试多媒体功能，和 android 启动共存
恢复模式，用于 SD 卡镜像升级

**ATE Factory boot**
自动测试环境出场模式。通过 PC 的 ATE 工具发送命令测试产品特性。

**Alarm boot**
RTC 闹钟启动

**Fastboot**
刷机

**download boot**
下载时，支持 logo 显示

**sw reboot**
启动原因是重启

#### 2.2.4 LK 启动代码
代码流程如下图：

![](http://ww1.sinaimg.cn/large/ba061518ly1fo1y6bd3wrj20pq0mcn2k.jpg)

![](http://ww1.sinaimg.cn/large/ba061518ly1fo1y6fawx0j20pb0ib0w8.jpg)

 lk/arch/arm/crt0.S
 
 ![](http://ww1.sinaimg.cn/large/ba061518ly1fo22fxyx8mj20gl03ogll.jpg)

lk/kernel/main.c

```c
/* called from crt0.S */
void kmain(void) __NO_RETURN __EXTERNALLY_VISIBLE;
void kmain(void)
{
#if !defined(MACH_FPGA) && !defined(SB_LK_BRINGUP)
        boot_time = get_timer(0);
#endif

        // get us into some sort of thread context
        thread_init_early();

        // early arch stuff
        arch_early_init();  // 使能 MMU、cache

        // do any super early platform initialization
        platform_early_init();  // 使能 Uart、中断、定时器、DRAM Banks、wot、display

#if defined(MACH_FPGA) || defined(SB_LK_BRINGUP)
        boot_time = get_timer(0);
#endif

        // do any super early target initialization
        target_early_init(); // 空，可以在这里实现一些定制的超级初始化

        dprintf(INFO, "welcome to lk\n\n");

        // deal with any static constructors
        dprintf(SPEW, "calling constructors\n");
        call_constructors();

        // bring up the kernel heap
        dprintf(SPEW, "initializing heap\n");
        heap_init();

        // initialize the threading system
        dprintf(SPEW, "initializing threads\n");
        thread_init();

        // initialize the dpc system
        dprintf(SPEW, "initializing dpc\n");
        dpc_init();

        // initialize kernel timers
        dprintf(SPEW, "initializing timers\n");
        timer_init();

#ifdef  MTK_LK_IRRX_SUPPORT
   mtk_ir_init(0);
#endif

#if (!ENABLE_NANDWRITE)
        // create a thread to complete system initialization
        dprintf(SPEW, "creating bootstrap completion thread\n");
        thread_resume(thread_create("bootstrap2", &bootstrap2, NULL, DEFAULT_PRIORITY, DEFAULT_STACK_SIZE));

        // enable interrupts
        exit_critical_section();

        // become the idle thread
        thread_become_idle();
#else
        bootstrap_nandwrite();
#endif
}
```

这里会创建一个 bootstrap2 线程
```c
static int bootstrap2(void *arg)
{
        dprintf(SPEW, "top of bootstrap2()\n");

        arch_init(); // 空

        // XXX put this somewhere else
#if WITH_LIB_BIO
        bio_init();
#endif
#if WITH_LIB_FS
        fs_init();
#endif

        // initialize the rest of the platform
        dprintf(SPEW, "initializing platform\n");
        platform_init(); // 启动模式选择电池、显示 Logo、背光打开、设置软件的环境变量

        // initialize the target
        dprintf(SPEW, "initializing target\n");
        target_init(); // 空

        dprintf(SPEW, "calling apps_init()\n");
        apps_init();

        return 0;
}

```

