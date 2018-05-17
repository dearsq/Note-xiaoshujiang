---
title: [Android6.0][MTK6737] 设置屏幕旋转 270 度
tags: 
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux4.10
HostOS: Ubuntu16.04

[TOC]


## 屏幕显示
### LK 部分
alps/vendor/mediatek/proprietary/bootable/bootloader/lk/project/br6737m_65_s_m0.mk
```
MTK_LCM_PHYSICAL_ROTATION = 270
```
### kernel 部分
kernel-3.18/arch/arm64/configs/br6737m_65_s_m0_debug_defconfig
```
CONFIG_MTK_LCM_PHYSICAL_ROTATION="270"
```

### MTK 定制的应用层
device/bror/br6737m_65_s_m0/ProjectConfig.mk
```
MTK_LCM_PHYSICAL_ROTATION = 270
```

### Android 官方的应用层
system.prop 中的 ro.sf.hwrotation 属性。
包括开机动画（bootanimation.zip）都是由这个控制的。
```
--- a/bror/br6737m_65_s_m0/system.prop
+++ b/bror/br6737m_65_s_m0/system.prop
@@ -61,6 +61,7 @@ ro.kernel.zio=38,108,105,16
 #ro.boot.selinux=disable
 
 ro.sf.lcd_density=240
+ro.sf.hwrotation=270
 ```

## TP坐标
### 通过交换 x y 坐标实现旋转
kernel-3.18/drivers/input/touchscreen/mediatek/
```
#define GTP_CHANGE_X2Y        1       //swap x  y  
#define TPD_WARP_X  
```
kernel-3.18/drivers/input/touchscreen/mediatek/
```
                 input_x = TPD_WARP_X(abs_x_max, input_x); // input_x = abs_x_max - 1 - input_x  
                 input_y = TPD_WARP_Y(abs_y_max, input_y); // input_y = input_y  
+                #if GTP_CHANGE_X2Y  
+                    GTP_SWAP(input_x,input_y);  
+                #endif  
   
                 #if GTP_WITH_HOVER  
                     id = coor_data[0];  
```

## 导航栏丢失
旋转 90/270 度之后系统导航栏丢失，并在右边产生有黑边。
是 MTK 的 Bug。解决办法参见另外一片博文。