---
title: [OrangePi] RK Linux 平台启动过程（5个阶段）详解
tags: linux,rockchip
grammar_cjkRuby: true
---
Hardware Platform: RK3399

[TOC]

## Boot Stage
包括两种启动方式：
一、U-Boot SPL
二、RK idbLoader （由 RK DDR init bin 和 miniloader bin 组成）

![RK 启动 5 阶段示意图][1]
 
 
  所以从不同介质（eMMC / SD Card / U-Disk / net）启动的时候，实际上是不同的概念：
 Stage 1 在芯片内固化的 Boot ROM 中。它将引导启动 Stage 2 ，有可能引导 Stage 3（仅当使能 SPL_BACK_TO_BROM 选项的时候）。
 从 eMMC 或 SDCard 启动的时候，所有固件（stage 2,3,4,5）都在 eMMC 或 SD Card。
 从 SPI Flash 启动的时候，stage 2 和 stage 3（只有 SPL 和 U-Boot）在 SPI Flash 中，stage 4 和 stage 5 在其他的地方。
 从 U-Disk 启动的时候，stage 4 和 stage 5（不包括 SPL 和 U-boot）是在 U-Disk 中的，只有 5 可供选择。
 从 net/tftp 启动的时候，stage 4 和 stage 5（不包括 SPL 和 U-boot）是在 网络 上的。
 
 ## Package Option
 下面是 stage 2～4 package 的 file list。
 
 从源码编译出来的：
 U-Boot 编译出 u-boot-spl.bin, u-boot.bin(可以用 u-boot-nodtb.bin 和 u-boot.dtb 替代）
 Kernel 编译出 kernel Image/zImage, kernel dtb
 ATF 编译出 bl31.bin
 
 从 rkbin 文件夹中提供的：
 ddr、usbplug、miniloader、bl31 
    
### idbspl.img
这个 img 是 U-Boot SPL, SPL_BACK_TP_BROM 选项**禁能**。
```
./tools/mkimage -n rkxxxx -T rksd -d spl/u-boot-spl.bin idbspl.img
```
将 idbspl.img 烧写到偏移地址 0x40 处，在此引导 stage 2 ，还需要烧写 stage 3  的 image 到 0x200  (由 CONFIG_SYS_MMCSD_RAW_MODE_U_BOOT_SECTOR 定义)。
Stage 3 image 可能只需要 u-boot.bin (如果没有 ATF 要求，比如 armv7), 或者 FIT image bl3.itb(对于从 SPL 加载的 ATF，包括了bl31.bin, u-boot-nodtb.bin and u-boot.dtb)。


### idbloader.img
这个 img 是 U-Boot SPL, SPL_BACK_TP_BROM 选项**使能**。
前面有说，如果使能，就会引导 Stage 3。
```
./tools/mkimage -n rkxxxx -T rksd -d spl/u-boot-spl.bin idbloader.img
cat u-boot.bin >> idbloader.img
```
接下来烧录  idbloader.img 到偏移地址 0x40 处，就会启动 stage 2 和 stage 3。
从 rkbin 中打包镜像：
```
dd if=rkxx_ddr_vx.xx.bin of=ddr.bin bs=4 skip=1
./tools/mkimage -n rkxxxx -T rksd -d ddr.bin idbloader.img
rm ddr.bin
cat rkxx_miniloader_vx.xx.bin >> idbloader.img
```
烧录 idbloader.img 到偏移地址 0x40 处，下面你会需要用以启动 stage 3 的 uboot.img。

### bl3.itb 
当使用 SPL 来加载 ATF，打包 bl31.bin ,u-boot-nodtb.bin , uboot.dtb 到 one FIT image
```
./tools/mkimage -f fit4spl.its -E bl3.itb
```
烧写 bl3.itb 到偏移位置 0x200 处，它依赖于 烧录到 0x40 的 idbspl.img 

### uboot.img 
当使用 来自 RK miniloader 的  idbLoader 时，需要通过 Rockchip 工具 loaderimage 将 u-boot.bin 打包成 miniloader 的可加载格式。
```
./tools/loaderimage --pack --uboot u-boot.bin uboot.img
```
将 uboot.img 烧录到 0x4000， stage 3。.

### trust.img 
当使用 idbLoader 时，为了使用 miniloader，需要通过 Rockchip 工具 trustmerge 将  bl31.bin 打包成 miniloader 的可加载格式。
```
./tools/trustmerge tools/rk_tools/RKTRUST_RKXXXXTRUST.ini
```
将 trust.img 烧录到 0x6000，为了使用 miniloader。

### rkxx_loader_vx.xx.xxx.bin
这个 bin 文件是 RK 以二进制文件提供，是用来以 upgrade_tool 或是 rkdeveloptool 工具 进行 eMMC 烧录的时候使用的。
它打包了 ddr.bin，usbplug.bin，miniloader.bin。RK 烧录工具的 DB 命令可以让 usbplug.bin 在已经处于 Rockusb mode 的目标设备上运行。

### boot.img
boot.img 将  kernel image 和 dtb 文件的打包成一个已知的文件系统。
它将被烧录在 0x8000，stage 4。

### rootfs.img
烧录 rootfs.img 到 0x40000，stage 5。


```flow
st=>start: BootROM
rootfs=>end: rootfs
0x40000

spl=>condition: SPL_BACK_TP_BROM
idbloader=>operation: idbloader.img
spl/u-boot-spl.bin + u-boot.bin
0x40

idbspl=>operation: idbspl.img
spl/u-boot-spl.bin
0x40

uboot=>operation: uboot.img
0x4000
trust=>operation: trust.img
0x6000

bl3=>operation: bl3.itb
bl3.bin + u-boot-nodtb.bin + uboot.dtb
0x4000

boot=>end: boot.img
0x8000

st->spl
spl(yes)->idbloader
spl(no)->idbspl
idbloader->uboot->trust->boot
idbspl->bl3->boot
boot->rootfs
```

## 不同选择情况下的 Image 准备
对于 armv8 采用 SPL：
idbspl.img
bl3.itb
boot.img or boot folder with Image, dtb and exitlinulx inside
rootfs.img

对于 armv8 采用 miniloader：
idbLoader.img
uboot.img
trust.img
boot.img or boot folder with Image, dtb and exitlinulx inside
rootfs.img

## 从 eMMC 启动
1. 我们需要进入 maskrom 模式
2. usb 线连接开发板和主机
3. 烧录 image 到 eMMC

实例：
```bash
# 最开始烧录 loader 和 gpt 分区参数
rkdeveloptool db rk3399_loader_v1.08.106.bin
rkdeveloptool gpt parameter_gpt.txt
```
对于 armv8 使用 SPL：
```bash
rkdeveloptool db rk3399_loader_v1.08.106.bin
rkdeveloptool wl 0x40 idbspl.img
rkdeveloptool wl 0x200 bl3.itb
rkdeveloptool wl 0x8000 boot.img
rkdeveloptool wl 0x40000 rootfs.img
rkdeveloptool rd
```

对于 armv8 使用 miniloader：
```bash
rkdeveloptool db rk3399_loader_v1.08.106.bin
rkdeveloptool wl 0x40 idbloader.img
rkdeveloptool wl 0x4000 uboot.img
rkdeveloptool wl 0x6000 trust.img
rkdeveloptool wl 0x8000 boot.img
rkdeveloptool wl 0x40000 rootfs.img
rkdeveloptool rd
```

## 从 SD/TF Card 启动
//TODO

## 从 U-Disk 启动
//TODO

## 从 Network 启动
//TODO


  [1]: http://wx4.sinaimg.cn/large/ba061518ly1ff191zccg6j20o10bnabh.jpg "RK 启动阶段示意图"