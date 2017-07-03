---
title: [Android6.0][RK3399] PCIe 接口 4G模块 EC20 调试记录
tags: usb,rockchip,ec20
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 
4G Module: EC20-CE

[TOC]

## 一、基本概念

### 1. USB 部分的功能接口

Quectel 3G/4G模块（UMTS/HSPA/LTE）的 USB 部分包括了几个不同的功能接口。

**USB Serial** 
ttyUSB0 代表 DM
ttyUSB1 代表 GPS NMEA （GPS导航设备统一的RTCM标准协议）信息输出
ttyUSB2 代表 AT commands
ttyUSB3 代表 PPP 连接

**GobiNet**
 在移植了 GobiNet 驱动后，会产生一个网络设备和一个 QMI channel。
网络设备叫做 ethX（在内核版本2.6.39前叫做 usbX）QMI channel 叫做 /dev/qcqmiX 的节点。
网络设备用来进行数据传输，QMI 通道用来进行 QMI 信息交互。
Qualcomm [Gobi][1] is a family of embedded mobile broadband modem products by Qualcomm. Gobi technology was designed to allow for any product with the embedded solution to connect to the internet anywhere a wireless carrier provides data coverage. One of the more notable products that contain a Gobi modem is the iPhone 4 for Verizon, which contains a MDM6600™, however it does not take advantage of the support for HSPA+

**QMI WWAN**
当移植了 QMI WWAN 驱动后，驱动将会创建网络设备和 QMI channel，网络设备被称作 wwanX，QMI 通道被命名为 /dev/cdc-wdmX。
网络设备用来进行数据传输，QMI 通道用来进行 QMI 数据交互。


**CDC ACM**
在移植完了 CDC ACM 驱动后，将会在 /dev 下创建如下节点
ttyACM0 用于 PPP连接器 或者 AT命令
ttyACM1 用于 Trace1
ttyACM2 用于 Trace2
ttyACM3 用于 AT commands
ttyACM4 用于 AT commands

USB 的 CDC 类是 USB 通信设备类 （Communication Device Class）的简称。
CDC 类 是 USB 组织定义的一类专门给各种通信设备（电信通信设备和中速网络通信设备）使用的 USB 子类。
 
### 2. APN
APN 指一种网络接入技术，是通过手机上网时必须配置的一个参数，它决定了手机**通过哪种接入方式来访问网络**。


  
## 二、驱动移植

### 1. USB Driver
主要参考官方文档《Quectel_WCDMA&LTE_Linux_USB_Driver_User_Guide_V1.5.pdf》
精简版的移植手册可以参考 http://blog.csdn.net/hnjztyx/article/details/72495433  这篇，三星平台 Android5.1 的，写的比较清晰。
  
另外有部分地方需要强调一下。
  
1. 如果是 EC20 需要将其 VendorID 和 ProductID 打印出来看一下，因为有的 EC20 是有两个版本的，分别是 EC20-C 和 EC20-CE。
EC20-C  IDVendor=0x05c6 IDProduct=0x9215
EC20-CE IDVendor=0x2c7c IDProduct=0x0125
插拔设备出现信息如下：
` [  723.730113] usb 1-1: New USB device found, idVendor=2c7c, idProduct=0125 `
可见我的设备是 EC20-CE。
务必确认好自己的物料版本。
2. 移植的时候最好先控制变量，第一步只移植 USB Serial Driver 部分。完成这部分的移植后 /dev/下就应该生成 ttyUSB0-ttyUSB4 。一次添加的东西多了如果出现问题不好定位问题出现的地方。
 

  
### 2. GobiNet Driver 或者 QMI WWAN 
GobiNet Driver 和 QMI WWAN 两者的作用相同，只不过一个是在 Kernel Space 实现，一个是在 Userspace 实现。
对于 GobiNet Driver，需要在 Kernel 中添加 供应商提供的 GobiNet 的源码;
对于 QMI WWAN ，默认 Android 6.0 中已经实现了这种方式，我们只需要添加 ID 即可，所以我选择的后者。
调试完成后会在 /dev 下生成cdc-wdmX节点。


### 3. PPP 拨号配置
在驱动部分参考手册打开对应的宏即可。
下面是关于 APN 的配置，在我们完成 RIL 的移植后进行。

> APN : Access Point Names 。
> ChinaUnicom 联通 3gnet ，ChinaMobile 移动 cmnet，ChinaTelecom 电信 ctnet。






## 三、RIL 移植

  RIL 在 Android 中的位置如下图
  
  ![RIL 在 Android 架构中的位置][2]
  
可以看到，RIL 在 Android 架构中的位置处于 Kernel 和 Framework 之间。
**Libraries 中的 RIL** 被分为两个部分，RILD 和 Vendor RIL。
RILD 负责 Socket 和 Framework 之间的通信。
Vendor RIL 负责 和 Radio 的通信（通过 AT command channel 与 Packet data channel(PDCH)）。AT command channel 用来直接和 Radio 通信，PDCH 用以 data service。
**Java framework 中的 RIL** 也被分为来两个部分，一部分是 RIL module 另一部分是 Phone module。
The RIL modeule 用来和底层的 RILD 通信，The Phone module 直接为应用层（Application）提供电话功能的接口。

### 1. RIL Driver Integration

以 Quectel 的 EC20 为例。
Quectel 以源码形式提供了 RIL driver（package/reference-ril）。我们只需要拷贝到我们的 Android 源码的正确路径并编译即可。

相应 Android 源码路径为：
hardware/ril/reference-ril ，用代理商提供的代码替换即可。

并且修改 init.rc 
```
service ril-daemon /system/bin/rild -l /system/lib/libreference-ril.so
    class main
    socket rild stream 660 root radio 
    socket rild-debug stream 666 radio system 
    user root 
    group radio cache inet misc audio sdcard_rw log
```
禁能切换用户 hardware/ril/rild/rild.c
```
OpenLib:
    #endif
      //switchUser();
```

如果需要在 非root 下进行调试的话，还可以在 common/ueventd.rockchip.rc 中加上：
```
# for radio
/dev/ttyUSB0              0666   radio		radio
/dev/ttyUSB1              0666   radio		radio
/dev/ttyUSB2              0666   radio		radio
/dev/ttyUSB3              0666   radio		radio
```
重新编译即可。

### 2. 抓取 Android Log
```
# 只看 RIL module 的 log
adb logcat -b radio -v time
```

### 3. RIL 移植问题汇总
#### 1. 代码出现大量 error
EC20 的代理代码释放有误，Android6.0 对应的代码是《Quectel_Android_RIL_SR01A41V17》。

#### 2. 出现模块冲突报错：
```
build/core/base_rules.mk:157: *** hardware/ril/reference-ril: MODULE.TARGET.EXECUTABLES.chat alread defined by external/ppp/chat。
```
直接删除 rk 的 chat 模块即可
```
rm externel/ppp/chat -rf 
```
#### 3. RIL 没有生效（完成了 RIL 部分的移植后，看起来 4G 模块没有起作用）
1）确认 RIL 进程有没有运行
```
# getprop init.svc.ril-daemon
应该得到 Running ，如果得到的是 Stopped 或者 Restarting，则需要重新检查移植步骤
```
2）看一下 lib 是否是 Quectel 的
```
# getprop gsm.version.ril-impl
如果是 Quectel 的应该是
Quectel_Android_RIL_SR 开头的
```
如果这里显示的是
RIL_RK_DATA_V3.6_android6.0 //说明调用到 rk 自己的 ril 库了，去下一步确定 init.rc 的修改有没有成功，如果没成功参照 第4点。
如果这里显示的是 空
说明 库 和平台不兼容，检查是不是调用和自己平台兼容的库，
比如 32 位是在 system/lib 下，64位 是在 system/lib64 下

3）确认一下 init.rc 中的修改有没有成功
```
cat init.rc | grep ril-daemon
```
没有成功请参照后面的第4点。

4）确认 SELinux 没有打开
```
# getenforce 来获取 SELinux 的状态

# setenforce 0 将其设置为 Permissive
```

#### 4. init.rc 中的修改没有生效
在 device/rockchip/rk3399/init.rc 中的修改没有生效
去 out/.../rk3399_mid/root/init.rc 中看，并没有产生我们需要的修改

在 rk3399/device.mk 中可以看到
```
#ifeq ($(strip $(TARGET_BOARD_PLATFORM_PRODUCT)), tablet)
#PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/rk3399_32/init.rc:root/init.rc
#endif
```
如果是 tablet 产品，会 copy rk3399_32 中的 init rc 到 mid/init.rc 中。
所以这个地方的逻辑修改为 
```
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/init.rc:root/init.rc
```

另外，在3399 平台，会在 device.mk 中追加一次 lib 的路径
./rockchip/common/device.mk:588:    rild.libpath=/system/lib64/libril-rk29-dataonly.so
它会将之前我们指定的库的路径覆盖，需要将这一行删掉。

#### 5. 不修改 init.rc ，修改 system.prop 的方式指定 lib 库
有些产品，比如 vr、box 会在 system.prop 中指定 rild.libpath 。。所以我们也可以参考 RK 提供的做法来完成 库 路径的指定：
比如我是 mid 产品，指定 lib 路径为 64 bit 的库路径：
```
vi device/rockchip/rk3399/rk3399_mid/system.prop
-- rild.libpath=/system/lib/libril-rk29-dataonly.so
-- rild.libargs=-d /dev/ttyACM0
++ rild.libpath=/system/lib64/libreference-ril.so
++ rild.libargs=-d /dev/ttyUSB0

```
#### 6. SIM 卡 ABSENT
如果出现如下 Log
```
01-18 08:50:21.678 D/ATC ( 225): AT> AT+CPIN?
01-18 08:50:21.679 D/ATC ( 225): AT< +CME ERROR: 10
01-18 08:50:21.681 D/RILJ ( 731): [3664]< GET_SIM_STATUS IccCardState 
{CARDSTATE_ABSENT,PINSTATE_UNKNOWN,num_apps=0,gsm_id=8,cdma_id=8,ims_id=8} [SUB0]
“CARDSTATE_ABSENT”
```
说明可能是 SIM 卡卡座有问题。
检查 SIM 卡卡座与 SIM 卡，发现 SIM 卡插反了。


  [1]: https://en.wikipedia.org/wiki/Qualcomm_Gobi
  [2]: http://wx1.sinaimg.cn/large/ba061518ly1fh13zv9nprj20mt0j4gnu.jpg