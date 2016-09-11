---
title: NFC 客户 Support 流程
tags: 
grammar_cjkRuby: true
---
WPI ATU Younix @ 2016.7.25

## 驱动部分问题
### 测试程序用法

Pn547_i2c_test 为测试程序 
测试程序的使用方法如下 
1.  将 pn547_i2c_test.rar 解压到 external 目录下 mm 编译 
2.  将生成的 pn547_i2c_test push 到 system/bin 
执行 adb shell 
cd system/bin 
chmod 777 pn547_i2c_test 
./pn547_i2c_test  
**利用本工具确认 KERNEL 部分正常通信后**，再按文档《NFC_NCIHALx_ARF.3.3.0_L_FW08.01.26_FW10.01.14.rar》中的步骤移植上层部分

### 再还未移植上层内容前，执行测试程序后 NoACK

1.       从原理图上看 I2C 的地址是 0x28,这组 I2C 上是否有其他设备是冲突的，请检查 DTS 中 I2C 的地址是否配置正确
2.       请问是系统时钟还是晶振，采用外部晶振请保证是 27.12MHZ
3.       请抓取  I2C 的波形，并请看确认一下 IRQ 管脚的状态
4.       Dev/pn544 是否生成了 
5.       检查供电、固件下载管脚电平高低是否正常

### 不慎移植了上层后，但还未确认底层是否移植成功，需要先删除移植上层所产生的内容
请务必删除移植的上层内容后再使用测试程序
因为移植了上层代码后，在开机过程中，上层代码会去调用设备节点，所以此时运行 i2c_test 工具肯定是会失败的。
请删除上层编译结果后，再用 测试工具 进行测试：
1. 备份版本后并作如下修改：
删除 system/lib 下的 libnfc-nci.so  和 libnfc_nci_jni.so
删除 system/lib/hw 下的nfc_nci.pn54x.default.so 文件
删除 system/app/NfcNci 整个文件夹
删除 system 下 frameworks/native/data/etc/com.nxp.mifare.xml:system/etc/permissions/com.nxp.mifare.xml
frameworks/native/data/etc/com.android.nfc_extras.xml:system/etc/permissions/com.android.nfc_extras.xml
frameworks/native/data/etc/android.hardware.nfc.xml:system/etc/permissions/android.hardware.nfc.xml
frameworks/native/data/etc/android.hardware.nfc.hce.xml:system/etc/permissions/android.hardware.nfc.hce.xml
删除system/vendor/firmware/libpn547ad_fw.so
删除 system/etc/libnfc-brcm.conf
删除 system/etc/libnfc-nxp.conf
重新编译后，烧录 system.img
2. 重启机器
3. 利用 I2C_test 工具测试 I2C 现在是否能够正常通信，并将测试工具显示的信息发送给我。

### 设备节点权限
```
设备节点没权限，加一下权限 
请在平台的 rc 文件中添加
on boot 
# NFC 
   setprop ro.nfc.port "I2C" 
   chmod 0660 /dev/pn544 
chown nfc nfc /dev/pn544 
```
### 海思平台的驱动问题
1. 修改 I2C 的驱动实现
```
diff -Naru new/i2c-drv/std_i2c/drv_i2c.c old/i2c-drv/std_i2c/drv_i2c.c 
       --- new/i2c-drv/std_i2c/drv_i2c.c  2016-05-17 14:31:06.269986000 +0800 
       +++ old/i2c-drv/std_i2c/drv_i2c.c 2016-05-11 16:41:40.000000000 +0800 
       @@ -1040,7 +1040,7 @@ 
            u32Len = g_astI2CBuff[I2cNum].u32Len; 
            g_astI2CBuff[I2cNum].stDataExchange[u32Len].u32Direction = 1; 
            g_astI2CBuff[I2cNum].stDataExchange[u32Len].u8Data = I2cDevAddr & WRITE_OPERATION; 
       -    g_astI2CBuff[I2cNum].stDataExchange[u32Len].u32Command = I2C_WRITE; 
       +    g_astI2CBuff[I2cNum].stDataExchange[u32Len].u32Command = I2C_WRITE | I2C_START; 
            g_astI2CBuff[I2cNum].u32Len++;
```            

### 64位平台问题
```
64 bit 编译，按如下修改后进行编译
1.       添加编译选项 
#ifeq (&(TARGET_ARCH),arm64) 
    LOCAL_MULTLIB :=64 
#endif 
2.  LOCAL_MODULE_PATH :=$(TARGET_OUT_SHARED_LIBRARIES)/hw 改成 LOCAL_MODULE_RELATIVE_PATH := hw
```

### 想用 NXP CLK 控制 PMIC 的 CLK
```
现在想用NXP CLK REQ信号去控制PMIC CLK，但测量不到NXP CLK REQ的信号，一直是低电平，请问这个需要怎么设置吗？
解决方法： 
驱动将 CLK REQ 设成输入即可，之前提供给贵司的驱动已经有做这个 
另外 libnfc-nxp.conf 里 
NXP_CORE_CONF_EXTN={20, 02, 43, 10,  
        A0, 02, 01, 01, 使能CLK REQ 
        A0, 07, 01, 03,           
```

### 安全模块
安全模块部分， 首先 是需要第三方的厂商来协助完成 绑卡以及发卡 APP 的制作 （参考 三星pay 的 NFC 软件）。
另外,安全模块有两种， TEE 和 REE。
REE 指的 是在 RichOS（Android） 中实现的 安全保护措施。
TEE 指的 是 与 RichOS 并 行 的运行环境，为 OS 提供安全服务。
详细的可以参 考：http://blog.csdn.net/braveheart95/article/details/8882322
两种都是实现 安全 模块的方式，区别在于 TEE 安 全级别更高。
从移植过程中来看，
REE 基于 我们 的代码还需要添加 .so 的 库文件。
TEE 还需 要调 通 SPI 总 线。
但是无论是哪 一种 都需要先将我们的上层移植完毕。


## 移植上层部分
### 固件和配置文件的问题
conf 文件需要对应硬件修改一些配置。
请问
1. 采用的是 系统时钟 还是 外部晶振？如果采用的是系统时钟的话请问频率是多少？
2. 平台是 64bit 还是 32bit 的呢？
请将附件中的 .so 文件放到 /system/vendor/firmware目录下。 

### NFC APP 中需要修改的地方
```
packages\apps\Nfc\nci\jni\Android.mk  
#### Select the CHIP ####  
NXP_CHIP_TYPE :=$(PN547C2)  
 
external\libnfc-nci\Android.mk  
#### Select the CHIP #### 
D_CFLAGS += -DNFC_NXP_CHIP_TYPE=PN547C2  
 
external\libnfc-nci\halimpl\pn54x\Android.mk  
#### Select the CHIP #### 
LOCAL_CFLAGS += -DNFC_NXP_CHIP_TYPE=PN547C2  
packages\apps\Nfc\nci\jni 
NFC_NXP_ESE:= FALSE 
packages\apps\Nfc\nci\jni\NativeNfcAla.cpp做了如下修改： 
修改前： 
extern "C" 
{ 
#if (NFC_NXP_ESE == TRUE) 
#include "AlaLib.h" 
#include "IChannel.h" 
#include "phNxpConfig.h" 
#endif 
} 
修改后 
extern "C" 
{ 
#if (NFC_NXP_ESE == TRUE) 
#include "AlaLib.h" 
#include "IChannel.h" 
#else 
#include "phNxpConfig.h" 
#endif 
} 
另 libpn547_fw.so 需要放到 system/vendor/firmware 目录下 
```

### MTK 平台上层会遇到的问题
1. 看这个“PN547 ON  MTK 移植文档.pdf”里面的的一些目录结构，这个文档是针对android 6.0以下版本的指导说明书。里面一些路径跟android6.0的无法对应 ？
需要关掉平台原生的 NFC 相关的代码。具体请参考附件《MTK平台修改配置.txt》。 

2. MTK 平台新老版本代码有差异：请确认务必修改如下代码
external\libnfc-nci\halimpl\pn547\dnld\ 目录 下的  phDnldNfc_Internal.h
#define PHDNLDNFC_CMDRESP_MAX_BUFF_SIZE (0x100U)   ==> **(0xF0U)**

3. MTK 平台报错 Not Found
MTK 由于 package  里的文件系统，相册，设置 等应用使用了 MTK P2P 的接口，主要是这个接口没定义而导致报错，替换后会出现编译到时根据提示一个一个注释即可，
因为MTK 平台有自己的一套 NFC 实现，我们的移植是删掉后并采用 NXP 的这一套。
但是由于 MTK 平台的 其他 app 中（比如 setting） 会调用到这些他们自己实现的接口。
所以报错 cannot find 的时候需要对应去报错的文件中将该接口注释掉就可以了。

### 测试 APK
有一款用于测试的 APK（TagInfo），见附件，可以在完成上层代码移植后用于测试。
语句注释掉就可以了。
       
        
## NFC 菜单
### 可以出现，可以正常切换，但是无法刷卡
确认时钟是晶振还是系统，固件是否最新，天线匹配。调出波形为13.56M 附近。 
###  可以出现，可以正常切换，A B卡（身份证）交替识别读写很快无法识别任意一种卡片
 ```
 目前测试（使用NFC TagInfo软件）发现两个问题： 
 1. NPC100在S5P4418平台上识别到A类卡后，读取卡片信息的速度明显比手机（nexus4）慢； 
 2. 交替用A类卡和B类卡（身份证）进行识读，很快就无法再识别任何一种卡片了，如果只用一种类型的卡进行识读就不会出现问题；
解决方法：
打补丁：
NPC100芯片今天的测试结果如下： 
         1. A卡反复识读正常 
         2. B卡反复识读正常 
         3. B卡识读后换A卡识读正常 
         4. A卡识读后换B卡识读必定异常（表现为1：choose an action对话框不断闪现 2. 设置中的NFC菜单此时无法正常关闭） 
解决方法： 
修改 packages/apps/Nfc/nci/jni/NativeNfcTag.cpp 中的以下内容： 
          1. 
         --  static tNFA_HANDLE  sNdefTypeHandlerHandle = NFA_HANDLE_INVALID; 
         ++//static tNFA_HANDLE  sNdefTypeHandlerHandle = NFA_HANDLE_INVALID;  
          2. 
             sCurrentConnectedTargetType = natTag.mTechList[i]; 
         ++    sCurrentConnectedHandle = targetHandle;  
             if(natTag.mTechLibNfcTypes[i] == NFC_PROTOCOL_T3BT) 
             { 
                 goto TheEnd; 
             } 
         -- sCurrentConnectedHandle = targetHandle; 
         ++ // sCurrentConnectedHandle = targetHandle; 
             if (natTag.mTechLibNfcTypes[i] != NFC_PROTOCOL_ISO_DEP) 
             {
```

## 硬件知识与其他

### 硬件
####  CLK_REQ 和 XTAL 区别
CLK_REQ和XTAL1引脚都是时钟相关的引脚，在使用上有什么区别呢？ 
一般在使用 BB 输出的时钟信号，会使用CLK REQ  这个脚，直接接到 PMIC 上 使能 GPIO ，用于控制时钟的开关 
一般 XTAL1 接的是 BB 端输出的时钟，需要使用 CLK_REQ 这个脚。
XTAL1 接的是晶体的话，CLK_REQ 脚悬空。

### PN65T
#### 只做读卡功能需要 UICC 么
PN65T本身集成一个安全单元，可以做卡模拟，也可以外接一个 UICC SIM 卡做卡模拟。
只做读卡不需要 UICC。
#### SPI 引脚作用
用于主控和 SE 之间的通信及 SE OS 的升级


### 固件下载失败
```
在pn544_dev_read 函数中添加 
if (copy_to_user(buf, tmp, ret)) { 
printk("%s : failed to copy to user space\n", __func__); 
return -EFAULT; 
} 
++   printk("IFD->PC:"); 
++   for(i = 0; i < ret; i++){ 
++       printk(" %02X", tmp[i]); 
++   } 
++   printk("\n"); 
wake_lock_timeout(&pn544_dev->read_wake, 2*HZ); 
return ret; 
fail: 
  
在 pn544_dev_write函数中添加 
  
/* Write data */ 
     ret = i2c_master_send(pn544_dev->client, tmp, count); 
     if (ret != count) { 
     printk("%s : i2c_master_send returned %d\n", __func__, ret); 
     ret = -EIO; 
     goto exit; 
} 
++     printk("PC->IFD:"); 
++     for(i = 0; i < count; i++){ 
++              printk(" %02X", tmp[i]); 
++     } 
++     printk("\n"); 

exit:

然后根据 Log 观察，固件下载失败。 
20 01 00 为下载固件的指令， 
正常应该下载到 8.1.26版本的固件，实际上固件版本为 8.1.8 
 
解决方法： 
提供 Android Log，并分析配置文件。 
固件版本采用错了，换成 32位固件后，解决问题。
```

## 常见 AndroidLog 分析
### NxpHal  : phTmlNfc_Init Failed   
//节点未生成   
检查名字是否正确 
检查节点权限——> adb 直接看/dev/pn54x 的节点权限 
### nfcManager_doInitialize; ver=NFCDROID-AOSP_L_00.01 nfa=NFA_PI_1.03.66+ NCI_VERSION=0x10
I/NfcService( 1640): Enabling NFC // App 的 NFC 打开 
D/BrcmNfcJni( 1640): nfcManager_doInitialize: enter; ver=NFCDROID-AOSP_L_00.01 nfa=NFA_PI_1.03.66+ NCI_VERSION=0x10 
//ver=NFCDROID-AOSP 指的是 Android 5.0或者5.1   NFC_VERSION = 0x10 指的是 PN547 或者 65T  0x11 指的是 PN548 或者 66T
### D/BrcmNfcJni( 6290): NAME_NXP_DEFAULT_NFCEE_DISC_TIMEOUT not found 
跟踪代码 
/etc/libnfc_brcm.conf 没有找到
### E HAL     : load: id=nfc_nci.pn54x != hmi->id=nfc_nci_pn547 
HAL 层 id 与 HMI id 不对应 
修改 HAL 层 id 是在 
libhardware\include\hardware\nfc.h   #define NFC_NCI_NXP_PN54X_HARDWARE_MODULE_ID "nfc_nci.pn54x"   
修改 HMI id 是在 配置文件 libnfc-brcm.conf  
```
# NCI Hal Module name 
NCI_HAL_MODULE 宏是否为"nfc_nci.pn54x"  
```
### E/NfcAdaptation( 4800): NfcAdaptation::InitializeHalDeviceContext: fail hw_get_module 
应该是HAL 层的一个 nfc_nci.default.so 没编译出来 
external\libnfc-nci\halimpl\pn547\Android.mk 里 
LOCAL_MODULE := nfc_nci_pn547.$(HAL_SUFFIX) 
改成 
LOCAL_MODULE := nfc_nci_pn547.default 
PRODUCT_PACKAGES += \  
    NfcNci \  
    libnfc-nci \  
    libnfc_nci_jni \  
   nfc_nci_pn547.default \  
    com.android.nfc_extras 
请确认这两处保持一致，在system/lib/hw 会有nfc_nci_pn547.default.so 生成，现在应该没生成 。
 

