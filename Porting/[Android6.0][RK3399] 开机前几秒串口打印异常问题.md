---
title: [Android6.0][RK3399] 开机前几秒串口打印异常问题
tags: uart,rockchip
grammar_cjkRuby: true
---



## 问题现象

开机 0-3 s 串口打印异常，log 大致如下：

```
 CPLWC�+lH�ؐL)�������ꁳ�ݵ��}�ɽ��������������r���͑�����j郵���rŽ��Ց����͕͕͑͑́ 
с���ɕ��́�Â��j���r�ʺ���¢��oꁵ������j�������������:�UŠ���r��:¥�jR� 
[ 1.973752] resource: 0x000c00000 -- 0x001c00000 (16 MB)
[ 1.973761] kernel: 0x001c00000 -- 0x002c00000 (16 MB)
[ 1.973769] boot: 0x002c00000 -- 0x004c00000 (32 MB)
[ 1.973777] recovery: 0x004c00000 -- 0x006c00000 (32 MB)
```


## 调试步骤

### 抓取串口波形

在 0-3s 串口波形异常。

### 检查上电

![](http://ww1.sinaimg.cn/large/ba061518ly1fj300v7lkoj20u70el41f.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gy1fj30i7jk33j20se08t759.jpg)

APIO4 = 3.0V
PMUIO2 = 3.0V

参考 rk 文档
kernel/Documentation/devicetree/bindings/power/rockchip-io-domain.txt
设置方法如下：
```
Possible supplies for rk3399:
- bt656-supply:  The supply connected to APIO2_VDD.
- audio-supply:  The supply connected to APIO5_VDD.
- sdmmc-supply:  The supply connected to SDMMC0_VDD.
- gpio1830       The supply connected to APIO4_VDD.

Possible supplies for rk3399 pmu-domains:
- pmu1830-supply:The supply connected to PMUIO2_VDD.
```

检查 dts 中的设置为

```
&io_domains {
	status = "okay";

	bt656-supply = <&vcc_3v0>;		/* bt656_gpio2ab_ms */
	audio-supply = <&vcca1v8_codec>;	/* audio_gpio3d4a_ms */
	sdmmc-supply = <&vcc_sd>;		/* sdmmc_gpio4b_ms */
	gpio1830-supply = <&vcc_3v0>;		/* gpio1833_gpio4cd_ms */
};


&pmu_io_domains {
	status = "okay";
	pmu1830-supply = <&vcc_3v0>;
};
```

正确无误。


### 获取 kernel 起来后实际配置的 pmu io 电压

```
root@rk3399_mid:/ # io -4 -r 0xFF320180
ff320180:  00000100
```
![](http://ww1.sinaimg.cn/large/ba061518gy1fj32mbbyd4j20h602zjrr.jpg)

所以实际起作用是 3v，没问题。

### 获取开机阶段实际配置的 pmu io 电压

获取 uboot 阶段中寄存器的配置可以这样做，在如下地方添加打印
```
void  __iomem *base_addr;
unsigned long p_addr = 0x????????;
unsigned long size = 0x??;


base_addr = ioremap(p_addr , size );
printk("lml#####: gpio0_A0's direction = 0x%x", readl(base_addr));
iounmap(base_addr);
```
但是我们串口有问题啊！
添加了打印也看不到任何信息。

没辙！

### 检查 PMUIO2 power domain 部分电压是否正常

![](http://ww1.sinaimg.cn/large/ba061518gy1fj32z4njbjj20p107dwkb.jpg)

既然为 3.0V 需要上拉电阻来进行驱动强度选择。

![](http://ww1.sinaimg.cn/large/ba061518gy1fj33okmr0yj211409qjtl.jpg)

所以这个 R90029 应该贴了才行。
但是实际没贴。

贴上后串口打印正常。问题解决。
