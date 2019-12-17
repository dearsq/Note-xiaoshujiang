---
title: [Android7.1][RK3399] 修改system分区大小由1.5G到3G
date: 2019-12-17 21:00:00
tags: android,rk3399,system
---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.126




## 调试步骤
修改 BOARD_SYSTEMIMAGE_PARTITION_SIZE 的宏定义
```
diff --git a/rk3399_mid_pi/BoardConfig.mk b/rk3399_mid_pi/BoardConfig.mk
index c90c56c..1f14714 100755
--- a/rk3399_mid_pi/BoardConfig.mk
+++ b/rk3399_mid_pi/BoardConfig.mk
@@ -19,5 +19,5 @@ else
 BOARD_SYSTEMIMAGE_PARTITION_SIZE := 3221225472
 endif
 else
-BOARD_SYSTEMIMAGE_PARTITION_SIZE := 1610612736
+BOARD_SYSTEMIMAGE_PARTITION_SIZE := 3221225472
 endif
 ```

## 修改 parameter 分区表的内容
修改的方法参见：
[RK3399] Rockchip 平台 parameter.txt 文件详解
https://blog.csdn.net/dearsq/article/details/53185809

 ```
diff --git a/rk3399_mid_pi/parameter.txt b/rk3399_mid_pi/parameter.txt
index c34e7f2..755e890 100755
--- a/rk3399_mid_pi/parameter.txt
+++ b/rk3399_mid_pi/parameter.txt
@@ -11,4 +11,4 @@ PWR_HLD: 0,0,A,0,1
 #FDT_NAME: rk-kernel.dtb
 #RECOVER_KEY: 1,1,0,20,0
 #in section; per section 512(0x200) bytes
-CMDLINE: console=ttyFIQ0 androidboot.baseband=N/A androidboot.selinux=permissive androidboot.hardware=rk30board androidboot.console=ttyFIQ0 init=/init mtdparts=rk29xxnand:0x00002000@0x00002000(uboot),0x00002000@0x00004000(trust),0x00002000@0x00006000(misc),0x00008000@0x00008000(resource),0x0000C000@0x00010000(kernel),0x00010000@0x0001C000(boot),0x00020000@0x0002C000(recovery),0x00038000@0x0004C000(backup),0x00040000@0x00084000(cache),0x00300000@0x000C4000(system),0x00008000@0x003C4000(metadata),0x00000040@0x003CC000(verity_mode),0x00002000@0x003CC040(reserved),0x00000400@0x003CE040(frp),-@0x003CE440(userdata)
+CMDLINE: console=ttyFIQ0 androidboot.baseband=N/A androidboot.selinux=permissive androidboot.hardware=rk30board androidboot.console=ttyFIQ0 init=/init mtdparts=rk29xxnand:0x00002000@0x00002000(uboot),0x00002000@0x00004000(trust),0x00002000@0x00006000(misc),0x00008000@0x00008000(resource),0x0000C000@0x00010000(kernel),0x00010000@0x0001C000(boot),0x00020000@0x0002C000(recovery),0x00038000@0x0004C000(backup),0x00040000@0x00084000(cache),0x00600000@0x000C4000(system),0x00008000@0x006C4000(metadata),0x00000040@0x006CC000(verity_mode),0x00002000@0x006CC040(reserved),0x00000400@0x006CE040(frp),-@0x006CE440(userdata)
```
