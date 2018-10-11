---
title: [Android7.1][RK3399] 插上 TypeC 为 USB_FLOATING_CHARGER 模式
tags: android
grammar_cjkRuby: true
---

Author: Kris_Fei
Platform: RK3399  
OS: Android 7.1  
Kernel: v4.4.83

[TOC]


## 问题描述 
插上 TypeC 后 log 显示为 USB_FLOATING_CHARGER , 正常的应该是 USB_SDP_CHARGER

```
[   35.192416] rk818-charger: pmic: plug in
[   35.679779] phy phy-ff770000.syscon:usb2-phy@e450.1: charger = USB_FLOATING_CHARGER
[   35.688995] rk818-charger: receive type-c notifier event: AC...
[   35.700366] rk818-charger: ac=1 usb=0 dc=0 otg=0 v=4350 chrg=3000 input=3000 virt=0
[   35.702589] healthd: battery l=46 v=3825 t=18.8 h=2 st=2 c=-30 chg=a
[   35.727454] healthd: battery l=46 v=3825 t=18.8 h=2 st=2 c=-30 chg=a
```


## 解决方案

由于usb 3.0的type-c接口需要支持不同电压的外设(5V, 12V等)，如果不做控制，那么设置12V接5V的外设将会出问题。 
fusb302可以实现此控制，根据不同的外设电压来调整电流。 

FUSB302 框图:

![](https://ws1.sinaimg.cn/large/ba061518gy1fw490kmjkoj20cr08q3zv.jpg)

参考设计:

![](https://ws1.sinaimg.cn/large/ba061518gy1fw491e0z61j20mu0ejtav.jpg)

其中要注意的是INT_N引脚，此pin会接到processor端的gpio，当有usb插拔时，INT_N pin会被拉低，以通知cpu通过I2C去读取USB状态信息，如果dts中gpio配置得不对，usb也将无法被识别。


![](https://ws1.sinaimg.cn/large/ba061518gy1fw492rtaxxj20zu03idgw.jpg)


![](https://ws1.sinaimg.cn/large/ba061518gy1fw492x1s4nj20k00ccwgc.jpg)



调试的时候可以看下/proc/interrupts中有没有fusb302的中断信息，或者直接在驱动(drivers/mfd/fusb302.c)中加Log。

rk3399-mid-818-android.dts：
```
    fusb0: fusb30x@22 {
        compatible = "fairchild,fusb302";
        reg = <0x22>;
        pinctrl-names = "default";
        pinctrl-0 = <&fusb0_int>;
        int-n-gpios = <&gpio1 1 GPIO_ACTIVE_HIGH>; 
		//我用的是gpio1 A1, RK参考设计为 gpio1 A2
        status = "okay";
    };
    //这里也要一起修改
    fusb30x {
        fusb0_int: fusb0-int {
            rockchip,pins =
                <1 1 RK_FUNC_GPIO &pcfg_pull_up>;
        };
    };
```

正常 Log 如下:
```
[ 3479.628913] fusb302 4-0022: CC connected in 0 as UFP
[ 3479.635870] cdn-dp fec00000.dp: [drm:cdn_dp_pd_event_work] Not connected. Disabling cdn
[ 3479.728151] rk818-charger: pmic: plug in
[ 3479.797379] phy phy-ff770000.syscon:usb2-phy@e450.1: charger = USB_SDP_CHARGER
[ 3479.799540] rockchip-dwc3 usb@fe800000: USB peripheral connected
[ 3479.805475] rk818-charger: receive type-c notifier event: USB...
[ 3479.807465] rk818-charger: ac=0 usb=1 dc=0 otg=0 v=4350 chrg=3000 input=450 virt=0
[ 3479.819669] healthd: battery l=45 v=3801 t=18.8 h=2 st=2 c=-4 chg=u
[ 3479.834338] healthd: battery l=45 v=3801 t=18.8 h=2 st=2 c=-4 chg=u
[ 3479.993106] type=1400 audit(1358504472.310:17): avc: denied { read } for pid=313 comm="AudioOut_D" name="audioformat" dev="sysfs" ino=19061 scontext=u:r:audioserver:s0 tcontext=u:object_r:sysfs:s0 tclass=file permissive=1
[ 3479.993605] type=1400 audit(1358504472.310:18): avc: denied { open } for pid=313 comm="AudioOut_D" path="/sys/devices/platform/display-subsystem/drm/card0/card0-HDMI-A-1/audioformat" dev="sysfs" ino=19061 scontext=u:r:audioserver:s0 tcontext=u:object_r:sysfs:s0 tclass=file permissive=1
[ 3479.993759] type=1400 audit(1358504472.310:19): avc: denied { getattr } for pid=313 comm="AudioOut_D" path="/sys/devices/platform/display-subsystem/drm/card0/card0-HDMI-A-1/audioformat" dev="sysfs" ino=19061 scontext=u:r:audioserver:s0 tcontext=u:object_r:sysfs:s0 tclass=file permissive=1
[ 3480.096724] android_work: sent uevent USB_STATE=CONNECTED
```