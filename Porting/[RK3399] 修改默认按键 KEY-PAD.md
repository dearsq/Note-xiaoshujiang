---
title: [RK3399] 修改默认按键 KEY-PAD
tags: key
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4
Version: v2017.04


## 需求
需求是将 Menu 键修改为 Home 键。

## Key-Pad 原理
按键部分原理图如下

![](http://ww1.sinaimg.cn/large/ba061518gy1femdk1x3xoj20h00h6t9k.jpg)

可以看到不同按键串联的电阻值也不同。所以按下不同按键时 ADKEY_IN 的检测电压也会不同（不同阻值分压不同），平台端设计好接收不同电压时对应的功能，就实现了功能按键。


## 实现
### getevent 看是否获得按键上报
```
adb shell
getevent 
```
可以看到我们的 key pad 设备

![](http://ww1.sinaimg.cn/large/ba061518gy1femdsliah4j208001gglj.jpg)
按下我们需要修改的按键（现在的 MENU 键）

![](http://ww1.sinaimg.cn/large/ba061518gy1femgk316ecj209h01y0sk.jpg)

获得键值 0x003b，即 10 进制的 59

在 SDK/device/rockchip/common/rk29-keypad.kl 修改
```
vi SDK/device/rockchip/common/rk29-keypad.kl
-key 59    MENU
+key 59   HOME
-key 102   HOME
+key 102  MENU
key 114   VOLUME_DOWN
key 115   VOLUME_UP
key 116   POWER             WAKE
key 143   NOTIFICATION      WAKE
key 158   BACK
key 212   CAMERA
key 217   SEARCH
```

我们把 key 59 的功能改为 MENU

## 验证
按键生效。

## 后话
另外 adb pull /system/usr/keylayout/rk29-keypad.kl
修改后直接 push 进去也可以完成任务。