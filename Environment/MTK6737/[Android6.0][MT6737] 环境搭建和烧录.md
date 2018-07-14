---
title: [Android6.0][MT6737] 环境搭建和烧录
tags: android6.0,mtk6737
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

## 编译问题@Ubuntu16.04

### teei_daemon.te ERROR
```
#allow osi tmpfs:lnk_file read;
device/mediatek/common/sepolicy/teei_daemon.te:30:ERROR 'unknown type teei_client_device' at token ';' on line 25309:
#define for mlsconstrain
typeattribute teei_client_device mlstrustedobject;
checkpolicy:  error(s) encountered while parsing configuration
out/host/linux-x86/bin/checkpolicy:  loading policy configuration from out/target/product/br6737m_65_s_m0/obj/ETC/sepolicy.recovery_intermediates/policy_recovery.conf
external/sepolicy/Android.mk:96: recipe for target 'out/target/product/br6737m_65_s_m0/obj/ETC/sepolicy.recovery_intermediates/sepolicy.recovery' failed
make: *** [out/target/product/br6737m_65_s_m0/obj/ETC/sepolicy.recovery_intermediates/sepolicy.recovery] Error 1
```
```
device/mediatek/common/sepolicy/teei_daemon.te 
# 去掉最后一行
-- typeattribute teei_client_device mlstrustedobject；
```

### clang 报错
修改  alps/art/build/android.common_build.mk 大概81行
```
-- ifneq ($(WITHOUT_HOST_CLANG),true)
++ ifeq ($(WITHOUT_HOST_CLANG),false)
```
如果解决，那么 OK。
如果没有解决。还需要如下修改：
```
# 请自行做好原始 ld 的备份
cp /usr/bin/ld.gold prebuilts/gcc/Linux-x86/host/x86_64-linux-glibc2.11-4.6/x86_64-linux/bin/ld
make update-api
make -j8 # 重新编译
```

如果仍然有报错，
那么回退上述的所有修改，修改 build/core/clang/HOST_x86_common.mk：
```bash
CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_CFLAGS := \
  -integrated-as

CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_CFLAGS += -fstack-protector-strong
endif

ifeq ($(HOST_OS),linux)
CLANG_CONFIG_x86_LINUX_HOST_EXTRA_ASFLAGS := \
  --gcc-toolchain=$($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG) \
  --sysroot $($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG)/sysroot \
## 上面一行最后加上换行符 并添加下面这行
  -B$($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG)/x86_64-linux/bin

CLANG_CONFIG_x86_LINUX_HOST_EXTRA_CFLAGS := \
  --gcc-toolchain=$($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG)

CLANG_CONFIG_x86_LINUX_HOST_EXTRA_CFLAGS += -fstack-protector-strong

ifneq ($(strip $($(clang_2nd_arch_prefix)HOST_IS_64_BIT)),)
CLANG_CONFIG_x86_LINUX_HOST_EXTRA_CPPFLAGS := \
  --gcc-toolchain=$($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG) \
  --sysroot $($(clang_2nd_arch_prefix)HOST_TOOLCHAIN_FOR_CLANG)/sysroot \
```

### libcam 无法编译的问题
错误信息：
```
make: *** No rule to make target 'out/target/product/br6737m_65_s_m0/obj_arm/STATIC_LIBRARIES/libcam.halmemory_intermediates/export_includes', needed by 'out/target/product/br6737m_65_s_m0/obj_arm/SHARED_LIBRARIES/libcam_platform_intermediates/import_includes'.  Stop
```
解决方法：
```
aiiage@repo:~/alps$ cp -a vendor/mediatek/proprietary/hardware/mtkcam/legacy/platform/mt6735m/hal/memory vendor/mediatek/proprietary/hardware/mtkcam/legacy/platform/mt6735m/entry/
```

## 烧录问题@Linux

### S_BROM_CMD_JUMP_DA_FAIL
是由于 Ubuntu14.04 / 16.04 环境问题。

![enter description here](./images/1522658476893.jpg)

 是由于modemmanager包在ubuntu 14.04 或是更高版本中对于MTK的Flash 工具支持不完全，所造成的，如果想使用MTK的Flash工具，就要卸载这个包 
```
sudo apt-get remove modemmanager    //卸载modemmanager包
sudo service udev restart       //从启udev

# 卸载这个服务之后可能会造成内核模块　cdc_acm　不可用．执行以下命令进行检查
lsmod | grep cdc_acm            //检查    

# 执行后出现：
	cdc_acm                36864  0     //表示可用

# 如果没有任何输出：
	sudo modprobe cdc_acm           //智能安装cdc_acm

ok
```
如果出现pmt changed for the rom; it must be downloaded这个错误，则选择固件升级，便可以下载。

### S_INVALID_BBCHIP_TYPE
芯片类型不匹配

![enter description here](./images/1522658598110.jpg)

可能是 lunch 错工程。