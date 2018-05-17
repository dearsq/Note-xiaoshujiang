---
title: [NFC] Android 平台（Linux3.10） NXP NFC 移植流程归纳
tags: nfc,android
grammar_cjkRuby: true
---
WPI ATU Younix @ 2016.7.28
**目录**
一、驱动部分
1. 添加驱动文件
pn544.c / pn544.h
Makefile
Kconfig
2. 修改平台配置
3. 其他

二、Android Middleware 的移植
1. Device 部分
2. external 部分
3. framework 部分
4. packages\app\Nfc
5. 选择 PN547 or PN548
6. ESE 开关
7. 添加 conf 与 .so 文件
8. 其他

三、附录
pn547_i2c_test 工具使用说明



## 一、驱动部分
### 1. 添加驱动文件
#### pn544.c / pn544.h
```
cd IDH/kernel/drivers/
mkdir pn544
# 并加入驱动文件：
# pn544.c
# pn544.h
```
#### Makefile
同目录下添加 Makefile 如下：
```makefile
#
# Makefile for nfc devices
#
obj-y	+= pn544.o
#obj-$(CONFIG_NFC_PN548)	+= pn544.o
ccflags-$(CONFIG_NFC_DEBUG) := -DDEBUG
```
父目录下 Makefile 中添加
```
obj-y		+= pn544/
```
#### Kconfig
同目录下添加 Kconfig 如下
```
#
# Near Field Communication (NFC) devices
#

menu "Near Field Communication (NFC) devices"
	depends on NFC

config PN544_NFC
	tristate "PN544 NFC driver"
	depends on I2C
	select CRC_CCITT
	default n
	---help---
	  Say yes if you want PN544 Near Field Communication driver.
	  This is for i2c connected version. If unsure, say N here.

	  To compile this driver as a module, choose m here. The module will
	  be called pn544.

endmenu
```
父目录下 Kconfig 添加：
```Kconfig
source “drivers/pn544/Kconfig"
```
###  2. 修改平台配置
#### rc
IDH/device/PLATFORM_NAME/xxx.rc
为节点添加权限
展讯平台是 IDH/device/sprd/scx35/init.sc8830.rc
在 on boot 之后添加
```rc
for nfc
	setprop ro.nfc.port "I2C"
    chmod	0660 /dev/pn544
    chown	nfc	nfc	/dev/pn544
```
在 on post-fs-data 之后 添加
```
mkdir /data/nfc 0770 nfc nfc
mkdir /etc/param
```
#### hardware
Sources\hardware\libhardware\include\hardware\nfc.h
也用我们 hardware 目录下的 .h 替换

#### dts
因为 Android 5.1 Android 6.0 的内核是 Linux3.10 以上的，所以和曾经修改 board_info 的形式有所区别，我们需要修改 dts。
以展讯平台为例，查阅硬件资料，我们了解到使用的是 i2c1 组总线，i2c地址是 0x28。
IRQ 用的 GPIO 是 229， VEN 用的 GPIO 是 226，固件下载管脚 DWN（firm-gpio）用的 GPIO 是 228。
在 dts 的 i2c1 中添加节点：
```dts
nfc-pn544@28{
	nfc-pn544@28{
			compatible = "nxp,nfc-pn544";
			reg = <0x28>;
			nxp,irq-gpio = <&d_gpio_gpio 229 0x00>;//MTRSTN
			nxp,ven-gpio = <&d_gpio_gpio 226 0x00>;//MTDI
			//interrupt-parent = <&d_gpio_gpio>;
			//interrupts = <229 0>;
			interrupt-names = "nfc_irq";
			//nxp,firm-gpio = <&d_gpio_gpio 228 0x00>;
			nxp,firm-gpio = <&d_gpio_gpio 225 0x00>; //MTDO
        };
```

修改完驱动部分后，进行编译，可以利用
```
make -32 2>&1|tee makeKernel.log
```
将编译日志导出到 makeKernel.log 中以便于分析编译错误。

编译完成 Kernel 部分后，
1. 请用 adb shell 进入设备查看 dev 目录下是否有 pn544 节点生成。
2. 并利用 pn547_i2c_test 工具检测 i2c 通信能否成功。（工具使用方法见附录）

请反馈给我们的工程师确认 Kernel 部分移植**无误后再进行上层部分的移植**，否则会增加不必要的工作量。谢谢。

### 3. 其他
**Hisi 平台**的 i2c 通信失败可能需要修改平台端 i2c 相关的代码。
**MTK 平台** 的 dts 请参考释放的资料包中的 dts。在移植**Middleware代码**的时候有一些额外的配置（除了正常移植步骤外，需要先注释掉平台自己实现的一套 NFC API） ，所以请先完成 Kernel 部分的移植后再进行 Middleware 部分的移植。
**RK 平台** dts 配置部分与本手册出入较大，请自行配置。
**Qcom 平台**无额外修改。

## 二、Android Middleware 的移植
根据 Android 版本的不同，获取到相应的 Middleware。
Android 5.1 获取的是
NFC_NCIHALx_ARF.3.3.0_L_FW08.01.26_FW10.01.14（Android5.1 无eSE）
NFC_NCIHALx_ARF.3.5.0_L_FW08.01.26_FW10.01.18（Android5.1 有eSE）
Android 6.0 获取的是
NFC_NCIHAL_AR0F.4.2.0_M（Android6.0）

**本文档只做客户移植参考使用**，更详细的 移植说明 与 宏定义设置 请参考
目录下的《ANxxxx-NCI_HALx_Setup_Guideline》文档。

### 1. Device 部分
在平台的 mk 文件中添加：
 例如展讯平台是 IDH/device/sprd/scx35/device.mk ：
```
# nxp nfc
PRODUCT_PACKAGES += \
	libnfc-nci \
	libnfc_nci_jni \
	nfc_nci.pn54x.default \
	NfcNci \
	Tag \
	com.android.nfc_extras

PRODUCT_COPY_FILES += \
	frameworks/native/data/etc/com.nxp.mifare.xml:system/etc/permissions/com.nxp.mifare.xml \
    frameworks/native/data/etc/com.android.nfc_extras.xml:system/etc/permissions/com.android.nfc_extras.xml \
	frameworks/native/data/etc/android.hardware.nfc.xml:system/etc/permissions/android.hardware.nfc.xml \
	frameworks/native/data/etc/android.hardware.nfc.hce.xml:system/etc/permissions/android.hardware.nfc.hce.xml
```
请注意，续航符" \ "后不要加空格，否则编译时会报错。

### 2. external 部分
释放的代码有两个文件夹：
dta 与 libnfc-nci ，前者不需要管，后者：
删除平台原有的 libnfc-nci
```
rm external/libnfc-nci -rf
```
用我们所释放的对应代码替换之。

### 3. framework 部分
1. 将释放代码中的 framework/base/core/java/com 下的 nxp 与 vzw 替换平台代码中的相应文件夹（若没有则添加）
2. 将释放代码中的 framework/base/core/java/android/ 下的 nfc 文件夹替换平台代码中的相应文件夹
3. 修改 frameworks/base/Android.mk ：用 BeyondCompare 等对比软件对比修改，主要是添加 nfc 相关的内容

### 4. packages\app\Nfc 整个目录删除后替换。

### 5. 选择 PN547 芯片还是 PN548 芯片
完成 external 和 packages 部分的移植后请确认如下三个地方的内容：
external\libnfc-nci\Android.mk
```
#### Select the CHIP ####
D_CFLAGS += -DNFC_NXP_CHIP_TYPE=PN548C2
```
external\libnfc-nci\halimpl\pn54x\Android.mk
```
#### Select the CHIP ####
LOCAL_CFLAGS += -DNFC_NXP_CHIP_TYPE=PN548C2
```
packages\apps\Nfc\Nci\jni\Android.mk
```
#### Select the CHIP ####
NXP_CHIP_TYPE := $(PN548C2)
```
释放的代码默认是 PN548，代表 PN548 或 PN66T
如果采用的是 PN547 或者 PN65T，请将 **PN548C2** 修改为  **PN547C2**。

### 6. ESE 开关
修改如下两处确认打开 eSE
packages\apps\Nfc\nci\jni\Android.mk
NFC_NXP_ESE:= TRUE
external\libnfc-nci\Android.mk
NFC_NXP_ESE:= TRUE
若关闭，请将如上改为 FALSE，并且在
packages\apps\Nfc\nci\jni\NativeNfcAla.cpp 中添加
```
extern "C"
{
#if (NFC_NXP_ESE == TRUE)
    #include "AlaLib.h"
    #include "IChannel.h"
    #include "phNxpConfig.h"
#endif
}
```
### 7. 添加 conf 与 .so 文件
在释放的代码 external\libnfc-nci\halimpl\pn54x 目录下我们可以看到
libnfc-brcm_sample.conf
libnfc-nxp-PN547C2_example.conf
libnfc-nxp-PN548C2_example.conf
三个文件。
将 libnfc-brcm_sample.conf 改名为 libnfc-brcm.conf
选取符合自己情况的 libnfc-nxp-PN54xC2_example.conf 并改名为 libnfc-nxp.conf
在平台目录（如展讯平台是 device\sprd\scx35）下添加配置文件 conf 与 .so ：
libnfc-brcm.conf
libnfc-nxp.conf
libpn548ad_fw.so 或者 libpn547_fw.so （在释放的 Firmware 目录下）
并修改 device.mk 文件（如展讯平台是 IDH/device/sprd/scx35/device.mk ）：
```
# 其中请自行修改固件名
NFC_FW_PATCH := device/sprd/scx35/libpn548ad_fw.so
PRODUCT_COPY_FILES += \
    $(NFC_FW_PATCH):system/vendor/firmware/libpn548ad_fw.so

NFC_CONFIG_PATCH :=device/sprd/scx35/libnfc-brcm.conf
PRODUCT_COPY_FILES += \
    $(NFC_CONFIG_PATCH):system/etc/libnfc-brcm.conf

NFC_CONFIG_NXP_PATCH :=device/sprd/scx35/libnfc-nxp.conf
PRODUCT_COPY_FILES += \
    $(NFC_CONFIG_NXP_PATCH):system/etc/libnfc-nxp.conf
```
对于 **PN7120** 则不需要配置 固件 .so 路径。因为 PN7120 不需要下载固件。

### 8. 其他

**MTK 平台**的额外配置请根据 《MTK平台修改配置.txt》来进行修改。

至此，已完成 Middleware 部分的移植。
更多问题，请邮件咨询我们的工程师。
移植编译问题请附上 make 的 log，驱动问题请附上 Kernel log，Middleware 问题请附上 Android log，谢谢！

## 三、附录
### pn547_i2c_test 工具使用说明
pn547_i2c_test 为测试程序
测试程序的使用方法如下
1.  将 pn547_i2c_test.rar 解压到 external 目录下 mm 编译
2.  将生成的 pn547_i2c_test push 到 system/bin
adb shell
cd system/bin
chmod 777 pn547_i2c_test
./pn547_i2c_test 
务必利用本工具确认 KERNEL 部分正常通信后，再移植 Middleware 部分。
