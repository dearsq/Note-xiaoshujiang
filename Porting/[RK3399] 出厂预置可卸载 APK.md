---
title: [RK3399] 出厂预置可卸载 APK
tags: 
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04

[TOC]

## 官方文档中的方法
```
mkdir device/rockchip/rk3399/preinstall
cp test.apk device/rockchip/rk3399/preinstall/
```
重新编译即可

编译后会在 out/target/product/rk3399/system/ 下生成 preinstall 文件夹，其中包含了预置的第三方 APK。
烧录后系统将自动安装应用到 data/app 目录，所以他们是可以卸载的。

不过即使卸载后，恢复出厂设置后，这些 APP 还是会存在的。
希望卸载后，恢复出厂设置时，这些 APP 不存在的话，将上述文件夹名字改为 preinstall_del 即可。

## 出现问题
我的 out/target/product/rk3399/system/  并没有生成 preinstall 文件夹

## 解决思路
应该会有某个 mk 对 preinstall 进行操作。
```
$ grep preinstall ./device/rockchip/ -nir
./common/device.mk:21:    $(shell python device/rockchip/common/auto_generator.py $(TARGET_DEVICE_DIR) preinstall)
./common/device.mk:22:    $(shell python device/rockchip/common/auto_generator.py $(TARGET_DEVICE_DIR) preinstall_del)
./common/device.mk:23:    -include $(TARGET_DEVICE_DIR)/preinstall/preinstall.mk
./common/device.mk:24:    -include $(TARGET_DEVICE_DIR)/preinstall_del/preinstall.mk
./common/device.mk:422:# for preinstall
./common/device.mk:424:    $(LOCAL_PATH)/preinstall_cleanup.sh:system/bin/preinstall_cleanup.sh
./common/preinstall_cleanup.sh:2:log -t PackageManager "Start to clean up /system/preinstall_del/"
./common/preinstall_cleanup.sh:4:rm system/preinstall_del/*.*
./common/auto_generator.py:19:    preinstall_dir = os.path.dirname(argv[0])
./common/auto_generator.py:20:    preinstall_dir = os.path.join(preinstall_dir, '../../../' + argv[1] + '/' + argv[2])
./common/auto_generator.py:21:    if os.path.exists(preinstall_dir):
./common/auto_generator.py:23:        makefile_path = preinstall_dir + '/Android.mk'
./common/auto_generator.py:25:        include_path = preinstall_dir + '/preinstall.mk'
./common/auto_generator.py:36:        for root, dirs, files in os.walk(preinstall_dir):
```
看起来 device.mk 中有点相关
```
vi common/device.mk +21
```
```bash
 17 # Prebuild apps
 18 ifneq ($(strip $(TARGET_PRODUCT)), )
 19     TARGET_DEVICE_DIR=$(shell test -d device && find device -maxdepth 4 -path '*/$(TARGET_PRODUCT)/Boa    rdConfig.mk')
 20     TARGET_DEVICE_DIR := $(patsubst %/,%,$(dir $(TARGET_DEVICE_DIR)))
 21     $(shell python device/rockchip/common/auto_generator.py $(TARGET_DEVICE_DIR) preinstall)
 22     $(shell python device/rockchip/common/auto_generator.py $(TARGET_DEVICE_DIR) preinstall_del)
 23     -include $(TARGET_DEVICE_DIR)/preinstall/preinstall.mk
 24     -include $(TARGET_DEVICE_DIR)/preinstall_del/preinstall.mk
 25 endif
```
哦，原来他是会去找 TARGET_DEVICE_DIR 目录下的 preinstall 啊
**所以对于我的 TARGET_DEVICE_DIR 路径应该是 device/rockchip/rk3399/rk3399_64/preinstall**
重新按官方方法添加 APK 后验证成功。


另外在上面 mk 中也可以看到 在找到了 preinstall 或者 preinstall_del 后会调用 device/rockchip/common/auto_generator.py 这个脚本来生成一些 mk 文件（Android.mk 和 preinstall.mk）

实际上最终处理 preinstall 文件夹下 Apk 的逻辑是在生成的 preinstall.mk 中的
重新编译后我们可以看到
```bash
vi device/rockchip/rk3399/rk3399_64/preinstall/preinstall.mk
```
preinstall.mk 中有
```bash
  PRODUCT_PACKAGES += MyAPK
```

