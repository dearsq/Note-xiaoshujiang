---
title: [Android6.0][MTK6737] 长按 Power 没有真正关机 (MTK IPO 功能)
tags: mtk,android
grammar_cjkRuby: true
---

Hardware:MT6737 
DeviceOS:Android6.0 
Kernel: Linux3.18 
HostOS: Ubuntu16.04

# 需求
正常开机 45s. 
长按 Power 键进行关机后, 在 5s 内立即按住 Power 键进行开机
虽然会正常出现开机动画, 但是会继续之前退出时的状态.

比如正在放歌, 关机, 立即开机, 会出现开机动画, 但是在开机动画界面会继续放关机前的歌, 并回到关机前的界面.
这是因为 MTK 有 IPO  快速开关机功能导致的.
我们并不需要 IPO 功能, 所以将其裁剪掉.

# 关掉 IPO 功能

## device

-MTK_IPOH_SUPPORT = yes
+MTK_IPOH_SUPPORT = no
 MTK_IPO_MDRST_SUPPORT = no
-MTK_IPO_SUPPORT = yes
+MTK_IPO_SUPPORT = no
 MTK_IPTV_SUPPORT = no
 MTK_IPV6_SUPPORT = yes
 MTK_IPV6_TETHER_NDP_MODE = no


## vendor

## kernel

# 关掉电池检测和温度检测功能

## device
device/bror/br6737m_65_s_m0/ProjectConfig.mk
```
MTK_DISABLE_POWER_ON_OFF_VOLTAGE_LIMITATION=yes
```

## vendor
./vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/br6737t_35g_s_m0/br6737t_35g_s_m0.mk
```
MTK_DISABLE_POWER_ON_OFF_VOLTAGE_LIMITATION=yes
```
## kernel
kernel-3.18/arch/arm64/configs/br6737m_65_s_m0_defconfig
```
CONFIG_MTK_DISABLE_POWER_ON_OFF_VOLTAGE_LIMITATION=y
```
