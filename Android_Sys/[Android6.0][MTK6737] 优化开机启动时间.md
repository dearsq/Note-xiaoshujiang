---
title: [Android6.0][MTK6737] 优化开机启动时间
tags: android,mtk
grammar_cjkRuby: true
---

Hardware:MTK6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

[TOC]

Google 的文档:
https://source.android.com/devices/tech/perf/boot-times

## 一 Zygote 部分优化
预加载class、resources；加载的多了，会影响开机时间；
`./mobilelog/APLog_2015_0101_000107/bootprof`
```
     47630.014113 : Zygote:Preload Start
     47790.882882 : Zygote:Preload Start
     58315.969138 : Zygote:Preload 3831 classes in 8957ms
     58590.519831 : Zygote:Preload 3831 classes in 9260ms
     59647.350141 : Zygote:Preload 342 obtain resources in 1327ms
     59693.352987 : Zygote:Preload 41 resources in 44ms
     59935.724526 : Zygote:Preload 342 obtain resources in 1341ms
     59976.014450 : Zygote:Preload 41 resources in 38ms
     60671.346067 : Zygote:Preload End
     61208.389453 : Zygote:Preload End
     63385.657304 : Android:SysServerInit_START ## 用时 17-6=11s
     66214.698003 : Android:PackageManagerService_Start
     66652.701927 : Android:PMS_scan_START
     84856.281124 : Android:PMS_scan_data_done:/system/framework
    111793.129112 : Android:PMS_scan_data_done:/system/priv-app
    145123.168422 : Android:PMS_scan_data_done:/system/app
    154266.032828 : Android:PMS_scan_data_done:/system/vendor/operator/app
    155273.061292 : Android:PMS_scan_data_done:/system/plugin
    155287.398831 : Android:PMS_scan_data_done:/data/app
    160380.926612 : Android:PMS_scan_END
    162821.175926 : Android:PMS_READY
    176850.152113 : Android:SysServerInit_END
```
### 1.1 裁剪加载类
`./frameworks/base/preloaded-classes` 少加载会影响 App 启动速度 , 此地优化空间不大
`./frameworks/base/core/res/` 会被打包成 framework-res.apk，确保没有冗余的资源图片，可以挨个检查图片、XML是否在系统中有用到；

## 二 Build 预提取 odex 

通常手机升级后会显示 `正在优化第*个应用，总共 * 个应用` 这个就是在对 APK 做 `dexopt` 的优化。

`odex` 是 APK 中提取出来的可运行文件.
APK 中的 class.dex 会在 dex 优化过程众被转化为 odex 文件存放.

正常的开机过程中 , 系统需要在开机过程中从 APK 提取 dex 再运行. 
所以我们可以在 Build 过程中预先提取 dex 将其优化为 odex , 进而达到加快启动速度的目的.

### 2.1 对于内置 SourceCode 的 APK
在`Android.mk`中都会通过`include $(BUILD_PACKAGE)`来编译，会调用到`package.mk`来提取 `odex`. 

### 2.2 对于通过 prebuilt 方式内置的 APK
通过 prebuilt 方式预置的 APK , 默认不会被提取 `odex`.


### 2.3 设置方法

**2.3.1** 对于 App  的`Android.mk`
```
LOCAL_DEX_PREOPT := false
```
如果设置为 `false` 可以使整个系统使用提前优化的时候，某个app不使用提前优化。
如果设置为 `true` 则编译生成的文件有 oat 文件, 即在 build 过程中被提前优化.


**2.3.2** 对于 system.img 如果设置了:
```
WITH_DEXPREOPT := true
```
打开这个宏之后，无论是有源码还是无源码的预置apk预编译时都会提取odex文件。
如有发现user版本未提取odex，请检查device.mk文件配置：
```
   ifeq ($(TARGET_BUILD_VARIANT),user)
       WITH_DEXPREOPT := true
       DONT_DEXPREOPT_PREBUILTS := true  //此句注释掉
   endif 
```
对于64bit的芯片,若apk只有32bit的lib或者只能作为32bit运行，请在预置apk时在android.mk中添加下边的TAG标记此apk为32bit：
```
LOCAL_MULTILIB :=32
```
但是这个会导致 system.img 中的所有东西都被 pre-optimized , 即 system.img 会变得很大. 此时可能需要调大 system.img 的大小限制.
在编译的时候，/system/framework/ 目录下面的jar包，和 /system/app，/system/priv-app/，/system/vendor/app 下面的apk文件，都会在编译时，做odex优化。


**2.3.3** 对于 jar 包 , 如果不想jar包做odex优化，可以在/buid/core/java_library.mk文件中设置：
```
LOCAL_DEX_PREOPT := false
```
这样在编译时，jar包就不会做odex优化。


## 三 开机动画
bootanimation 时间
1. 最好不要超过 system_server 启动时间 (11s) ( 63385.657304 : Android:SysServerInit_START 到 Android:SysServerInit_END)
2. 不要播放 mp3
3. bootanimation.zip 图片越少越好

## 四 无用的服务
`/frameworks/base/services/java/com/android/server/SystemServer.java`
比如：DropBoxManagerService和调试相关，可以异步加载或者直接阉割掉;
比如：PinnerService没有配置相关则可以去除;
其他Service可以挨个排查.
非必要的服务可以放在 system_server 进程外启动.

## 五 App 的优化
### 5.1 App 本身优化
尽量少把APP设置为persist；
优化每一个有源码的persist APP；使他们启动尽可能快；
```
com.android.systemui(PersistAP)
com.mediatek.ims(PersistAP)
com.android.phone(PersistAP)
com.android.settings
```
精简apk包；
（1）删除没有用到的，图片、资源文件、没有用到的jar包文件、不需要使用的so文件；
（2）预置自己的APP，假如设备只会加载drawable-xxhdpi中的资源，那么可以在drawable包重复的资源可以直接删除；
（3）预置自己的APP，假如设置只支持英文，values-da、values-fa这样的多语言支持资源都可以删除；
（4）apk中只保留和系统适配的so文件，比如：armv7和arm64的so文件；

Application的onCreate方法中不要有耗时的代码段；

通过修改--compiler-filter 为 speed、quick、speed-profile来提高 APK 的启动速度；
speed 模式优化的类较多，这时优化后的vdex、odex的文件较大，应用启动过程包括映射apk文件的过程，文件偏大导致有一定的时间损耗；
但 speed 模式优化后，Java类执行更快；所以这个需要针对具体的应用多次验证，没有普适性；

### 5.2 系统 App 裁剪
PackageManagerService
scanDirTracedLI
（1）减少预置APP的数量（对开机速度会有较为明显的提升）；
（2）删除没有必要的apk包；
（3）单线程scan分区里面的apk并不一定能充分使用IO资源，尝试改为多线程异步scan；
（4）精简系统，把系统中用不到的apk包、有重复功能的apk移除，这样既可以使系统有更大的剩余存储空间又可以减少scan的时间，加快开机；

## 六 定频定核 
调高 CPU 频率, 副作用是带来功耗
```
/system/core/rootdir/init.rc
on early-init
#mtk begin
write /proc/ppm/policy/ut_fix_core_num "4 4"
write /proc/ppm/policy/ut_fix_freq_idx "0 0"
#mtk end

on property:sys.boot_completed=1
bootchart stop
#mtk begin
write /proc/ppm/policy/ut_fix_core_num "-1 -1"
write /proc/ppm/policy/ut_fix_freq_idx "-1 -1"
#mtk end
```

