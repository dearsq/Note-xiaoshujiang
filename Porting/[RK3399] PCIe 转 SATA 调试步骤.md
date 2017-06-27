---
title: [RK3399] PCIe 转 SATA 调试步骤
tags: rockchip,pcie
---

Platform: RK3399
OS: Android 6.0
Kernel: 4.4
Version: v2017.04

## PCI 基本调试手段
### busybox lspci
`lspci` 命令查看 pci 设备。出现如下信息：
```
0c:00.0 0100: 1000:0056 (rev 02)
```
0c：00.0 表示含义为 bus number： device number.function number 三者组合成一个 16bit 的识别码
1. bus number：8bits 最多连接到 256 个 bus
2. device number：6bits 最多连接到 32 种装置
3. function number：3bits 最多每种装置有 8 种功能
0100: 1000:0056 表示含义为 Class ID： Vendor ID  Device ID

通过如下命令可以获取 pci 的速度
```
#lspci -n -d 1000:0056 -vvv |grep -i width
```
### cat /proc/partitions
可以查看分区信息。

### mount
调试 PCIe 转 SATA 设备，还需要在生成设备节点后将硬盘的设备节点挂载到我们系统的目录上。

## PCIe 调试步骤
1. 在 menuconfig 中
打开相应的调试宏：BUS Support -> PCI Debugging
打开相应 PCIe 总线驱动： BUS Support -> PCI Support
打开其热插拔功能（Hot Plug）：BUS Support -> Support for PCI Hotplug

2. 在 PCIe 设备没有插上的情况下开机，得到如下 log
	```
	[    1.157185] rockchip-pcie f8000000.pcie: no vpcie3v3 regulator found
	[    1.157207] rockchip-pcie f8000000.pcie: no vpcie1v8 regulator found
	[    1.157223] rockchip-pcie f8000000.pcie: no vpcie0v9 regulator found
	[    1.691995] rockchip-pcie f8000000.pcie: PCIe link training gen1 timeout!
	[    1.692059] rockchip-pcie: probe of f8000000.pcie failed with error -110
	```
	我们 PCIe 设备还未连接，出现如上 Log 为正常。
3. 将 PCIe 的设备插在板子上后。利用 busybox lspci 查看现在的 pci 设备。
	```
	shell@rk3399_mid:/ $ busybox lspci
	00:00.0 Class 0604: 17cd:0000
	01:00.0 Class 0106: 1b21:0612
	```
	可以看到有几个 ID，可以根据 ID 确认设备是否被识别到。
	比如我们根据官方的 datasheet 知道，1b21 即 ASMEDIA 厂商的 Vendor ID，0612 即 Product ID。

4. 之后就是加载设备驱动的时候，会根据 VENDOR_ID 进行匹配。识别成功后才能加载 probe。

5. 如果没有进入 probe ，有一种情况是设备已经被一个驱动占有了，找到这个设备使用的驱动，并且去除即可。

### 调试 PCIe 转 SATA 设备
对于调试转 SATA 设备，还需要提供设备驱动的支持：

打开 PCIe 转 SATA 小板的设备驱动：Device Driver -> Serial ATA and Parallel ATA driverrs(libata) -> AHCI SATA support

确认方法为
```shell
# ls dev/block/sd*
sda
sda1
```
可以看到多出来了 sda 与 sda1，sda 即为 sata 硬盘，sda[n] 即为其分区号。
