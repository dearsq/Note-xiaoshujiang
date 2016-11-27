---
title: [RK3399] Type-C 驱动流程分析
tags: TypeC
grammar_cjkRuby: true
---

[TOC]

## 基本概念
### USB 控制器
#### OHCI（Open Host Controller Interface）
是**支持USB1.1的标准**，但它不仅仅是针对USB，还支持其他的一些接口，比如它还支持Apple的火线（Firewire，IEEE 1394）接口。与UHCI相比，OHCI的硬件复杂，硬件做的事情更多，所以实现对应的软件驱动的任务，就相对较简单。主要用于非x86的USB，如扩展卡、嵌入式开发板的USB主控。
#### UHCI（Universal Host Controller Interface）
**是Intel主导的对USB1.0、1.1的接口标准，与OHCI不兼容。**UHCI的软件驱动的任务重，需要做得比较复杂，但可以使用较便宜、较简单的硬件的USB控制器。Intel和VIA使用UHCI，而其余的硬件提供商使用OHCI。
#### EHCI（Enhanced Host Controller Interface）
**是Intel主导的USB2.0的接口标准。**
#### XHCI（eXtensible Host Controller Interface）
**是最新的USB3.0的接口标准**，它在速度、节能、虚拟化等方面都比前面3中有了较大的提高。
xHCI支持所有种类速度的USB设备（USB 3.0 SuperSpeed, USB 2.0 Low-, Full-, and High-speed, USB 1.1 Low- and Full-speed）。xHCI的目的是为了替换前面3种（UHCI/OHCI/EHCI）。
#### DWC3（DRD ）
is a SuperSpeed (SS) USB 3.0 Dual-Role-Device (DRD) from Synopsys.
特性：
The SuperSpeed USB controller features:
Dual-role device (DRD) capability:
Same programming model for SuperSpeed (SS), High-Speed (HS), Full-Speed (FS), and Low-Speed (LS)
Internal DMA controller
LPM protocol in USB 2.0 and U0, U1, U2, and U3 states for USB 3.0 

#### USB HOST、USB HSIC、USB OTG
**USB2.0 HOST（EHCI&OHCI）**：只能做主机（接电脑无法识别，因为电脑也是 HOST）。
**USB HSIC（EHCI）**：输出的不是普通的USB信号，而是XhsicSTROBE1，和XhsicDATA1的信号，必须接USB信号转换出来。
**USB2.0/3.0 OTG（DWC3/XHCI）**：既能做主机也能做从机，因为有USB的ID脚，可以识别是主机从机。

#### TypeC Phy

![](https://ws4.sinaimg.cn/large/ba061518gw1fa446ld799j20dl0brjsk.jpg)


## 驱动代码
先看一下 typec_phy 的结构体
```
struct rockchip_typec_phy {
	struct device *dev;
	void __iomem *base;
	struct extcon_dev *extcon;
	struct regmap *grf_regs;
	struct clk *clk_core;
	struct clk *clk_ref;
	struct reset_control *uphy_rst;
	struct reset_control *pipe_rst;
	struct reset_control *tcphy_rst;
	struct rockchip_usb3phy_port_cfg port_cfgs;
	/* mutex to protect access to individual PHYs */
	struct mutex lock;

	bool flip;
	u8 mode;
};
```

rockchip_typec_phy_probe
    typec_phy_pre_init(tcphy);





## 参考
[USB - wikipedia](http://en.wikipedia.org/wiki/Host_controller_interface_(USB,_Firewire)#USB)
