---
title: [Android6.0][RK3399] 设置系统默认不会休眠
tags: rockchip,android
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Version: v2017.04

[TOC]

## 需求
默认系统开机休眠时间为 60000 ms，需要设置为 Never （不会休眠）。

## 原理
设置 ro.rk.screenoff_time 参数。
和网上所说的设为 -1 不同，rk 平台应该设为 2147483647 。

## 步骤
```
$ grep screenoff_time ./device/ -nir
```
看到
```
./device/rockchip/common/device.mk:484:    ro.rk.screenoff_time=2147483647
./device/rockchip/common/device.mk:487:    ro.rk.screenoff_time=60000
```
```
$ vi ./device/rockchip/common/device.mk +484
481 ifeq ($(strip $(TARGET_BOARD_PLATFORM_PRODUCT)), box)
482 include device/rockchip/common/samba/rk31_samba.mk
483 PRODUCT_PROPERTY_OVERRIDES += \
484     ro.rk.screenoff_time=2147483647
485 else
486 PRODUCT_PROPERTY_OVERRIDES += \
487     ro.rk.screenoff_time=60000
488 endif

```
可见，默认产品为 box 的时候， ro.rk.screenoff_time 为 2147483647 这个值。
其他的产品默认为 60000（1 min）。
我们将也修改为 2147483647。

## 调用
./packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
```
loadSetting(stmt, Settings.System.SCREEN_OFF_TIMEOUT,
                     SystemProperties.getInt("ro.rk.screenoff_time", mContext.getResources().getIntege     r(R.integer.def_screen_off_timeout)));
```
将属性值存储到 stmt 数据库中的  Settings.System.SCREEN_OFF_TIMEOUT 字段中。
再供其他 app 如 hdmisetting、displaysetting 等进行调用。

## 其他
另外我尝试在 system.prop 中去添加这个属性。
但是没有起作用，adb pull 出 build.prop 后发现，system.prop 中设置的值在前面。
PRODUCT_PROPERTY_OVERRIDES 设置的值在后面，会覆盖掉前面的设置。

所以研究了一下系统属性加载优先级。
这篇文章很好：
http://blog.csdn.net/thl789/article/details/7014300

总的来说，顺序如下
1. 追加 system.prop 的内容到 build.prop
2. 追加 ADDITIONAL_BUILD_PROPERTIES 设定的属性值到 build.prop
3. 追加 PRODUCT_PROPERTY_OVERRIDES 设定的属性值到 build.prop

作为标准的配置而言，最好是加到 device/platform/product/system.prop 中，
但是最好先去 device.mk 文件中搜一下有没有设置过这个属性。如果有的话就在 device.mk 中修改吧。

而添加到 PRODUCT_PROPERTY_OVERRIDES 中的属性，因为是最后追加到 build.prop 的。可以保证成功。
