---
title: [RK3399]OTA差异包制作方法
tags: RockChip,OTA
grammar_cjkRuby: true
---
Platform: RK3399
OS: Android 6.0
Version: v2016.08

[TOC]

#### 一、全编
```
make -j32
./mkimage.sh ota
```
#### 二、生成原始的 OTA 完整包
```
make otapackage
```
会在 out/target/product/rk3399_disvr/ 下生成 rk3399_disvr-ota-user.younix.20161116.102654.zip

所生成的这个 rk3399_disvr-ota-user.younix.20161116.102654.zip 改名为 update.zip 即可用于固件升级

将这个改名为 ×-old.zip 用来作为后面差异 OTA 包的 target file
rk3399_disvr-ota-user.younix.old.zip
```
mv 
~/3399/out/target/product/rk3399_disvr/obj/PACKAGING/target_files_intermediates/rk3399_disvr-ota-user.younix.20161116.102654.zip
~/3399/out/target/product/rk3399_disvr/obj/PACKAGING/target_files_intermediates/rk3399_disvr-ota-user.younix.old.zip
```

#### 三、修改了一些内容
...

#### 四、生成 OTA 差异包
**生成差异包命令格式: 
ota_from_target_files   
–v –i  用于比较的前一个 target file   
–p host 主机编译环境 
‐k  打包密钥 
用于比较的后一个 target file 
最后生成的 ota 差异包**   
```
//1. 生成新的 ota 包
make otapackage
//生成了 rk3399_disvr-ota-user.younix.20161116.104037.zip

//2. 生成差异包
./build/tools/releasetools/ota_from_target_files   
‐v –i 
~/3399/out/target/product/rk3399_disvr/obj/PACKAGING/target_files_intermediates/rk3399_disvr-ota-user.younix.old.zip
‐p out/host/linux‐x86   
‐k build/target/product/security/testkey   
~/3399/out/target/product/rk3399_disvr/obj/PACKAGING/target_files_intermediates/rk3399_disvr-ota-user.younix.20161116.104037.zip
~/3399/out/target/product/rk3399_disvr/rk3399_disvr-ota-user.younix.zip
```
~/3399/out/target/product/rk3399_disvr/rk3399_disvr-ota-user.younix.zip
即为差异包