---
title: [Android6.0][MTK6737] 移植 Modem
tags: modem
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux4.10
HostOS: Ubuntu16.04

## 一 移植步骤
### 1. 先解压 modem 压缩包
### 2. 安装 modem 编译需要的环境
```
*******************************************
recommended Build Environment
*******************************************
* [OS]                : Linux
* [PERL]              : v5.10.1 or v5.14.2
* [MAKE]              : GNU Make v3.81
* [SHELL]             : GNU bash v4.1.5
* [GCC-ARM-NONE-EABI] : v4.6.2 or above
* [NATIVE GCC(UBUNTU)]: v4.5 or above
```
### 3. 进行编译
```
younix@younixVB:~/WorkSpace2/MTK6737/mcu$ ./make.sh "BR6737M_65_S_M0(LTG_DSDS).mak" new


*******************************************
recommended Build Environment
*******************************************
* [OS]                : Linux
* [PERL]              : v5.10.1 or v5.14.2
* [MAKE]              : GNU Make v3.81
* [SHELL]             : GNU bash v4.1.5
* [GCC-ARM-NONE-EABI] : v4.6.2 or above
* [NATIVE GCC(UBUNTU)]: v4.5 or above
project_name = BR6737M_65_S_M0
flavor = LTG_DSDS
clean build/BR6737M_65_S_M0/LTG_DSDS/tmp/*.*
concatenate make/modem_spec/MTK_MODEM_LTG.mak
concatenate make/custom_config/BR6737M_65_S_M0(LTG_DSDS)_EXT.mak
concatenate_proj_mak = build/BR6737M_65_S_M0/LTG_DSDS/bin/~BR6737M_65_S_M0(LTG_DSDS).mak
*******************************************
recommended Build Environment
*******************************************
* [OS]                : Linux
* [PERL]              : v5.10.1 or v5.14.2
* [MAKE]              : GNU Make v3.81
* [SHELL]             : GNU bash v4.1.5
* [GCC-ARM-NONE-EABI] : v4.6.2 or above
* [NATIVE GCC(UBUNTU)]: v4.5 or above

*******************************************
 Start checking current Build Environment  
*******************************************
* [PERL]              : v5.18.2            [NOT RECOMMENDED] !!!
* [MAKE]              : GNU Make v3.81     [OK] !!!
* [SHELL]             : GNU bash v4.3.11    [HIGHER THAN RECOMMENDED] !!!
sh: 1: tools/GCC/4.6.2/linux/bin/arm-none-eabi-gcc: not found
* [GCC-ARM-NONE-EABI] : [UNKNOWN VERSION] !!!
* [NATIVE GCC(UBUNTU)]: gcc (Ubuntu/Linaro 4.6.4-6ubuntu2) 4.6.4  [OK] !!!

current Build Env. is not recommendation 
To avoid unexpected errors , please install the recommended Tool Chain.
*******************************************
  Build Environment is NOT RECOMMENDED!
*******************************************

```
### 4. 拷贝 modem 固件到 alps SDK 中

接下来利用 pl 脚本自动重命名 modem 固件.
```
perl device/mediatek/build/build/tools/modemRenameCopy.pl ../modem "BR6737M_65_S_M0(LTG_DSDS)"
```
这个脚本会自动将 `../modem` 中的内容 copy 并 rename 到 vendor 中的 modem 子目录中, 并构建 Android.mk 

## 错误汇总
###  ia32-libs
```
start Drv feature check...
get feature list from drv_features.h...
get feature list from drv_features_option.h...
generate feature check file...
validate features...
infoFilename = ././build/BR6737M_65_S_M0/LTG_DSDS/bin/log/info.log
make: *** [drv_feature_check] Error 1

```
关键错误在 
sh: 1: tools/GCC/4.6.2/linux/bin/arm-none-eabi-gcc: not found

但是实际上该路径是有此 编译工具链的.

原因在于我们所使用的ubuntu应该是64位的，而运行的可执行程序是32位的，问题就出在这里，我们需要安装''ia32-libs''， 具体命令就是 sudo apt-get install ia32-libs.
会进一步提示 , 软件包已经被替代了, 我们改为安装 lib32z1
```
However the following packages replace it:
  lib32z1 lib32ncurses5 lib32bz2-1.0

E: Package 'ia32-libs' has no installation candidate
younix@younixVB:~/WorkSpace2/MTK6737/mcu$ sudo  apt-get install lib32z1
```

### libgcc_s.so.1
```
error while loading shared libraries: libgcc_s.so.1
```
解决方法:
sudo apt install gcc-multilib


### libstdc++.so.6
```
./build/BR6737M_65_S_M0/LTG_DSDS/bin/log/DbgInfoGen.log
tools/DbgInfoGen: error while loading shared libraries: libstdc++.so.6: cannot open shared object file: No such file or directory

```
解决方法:
```
sudo apt-get install lib32stdc++6
```


## 参考脚本
```
#!/bin/bash

# $1 -- TAG string
function print_err(){
    echo -e "\e[0;31;1m$1\e[0m"
}
function print_war(){
    echo -e "\e[0;33;1m$1\e[0m"
}
function print_log(){
    echo -e "\e[0;32;1m$1\e[0m"
}
export -f print_err
export -f print_war
export -f print_log

if [ ! -d "./BINS" ]; then
    print_log "mkdir -p ./BINS"
    mkdir -p ./BINS
fi

#print_err "please switch gcc to 4.4.3 ++++"

./make.sh BR6735_65C_L1\(LTTG_DSDS\).mak new
./../modemRenameCopy.pl . BR6735_65C_L1\(LTTG_DSDS\)
mv temp_modem ./BINS/temp_modem_lttg_$1


./make.sh BR6735_65C_L1\(LWG_DSDS\).mak new
./../modemRenameCopy.pl .  BR6735_65C_L1\(LWG_DSDS\)
mv temp_modem ./BINS/temp_modem_lwg_$1

#print_err "please switch gcc to 4.4 ----"
#sudo /root/switchGCC.sh

tar cjvpf ./BINS/temp_modem_$1.tar.bz2 ./BINS/temp_modem_lttg_$1 ./BINS/temp_modem_lwg_$1

exit 0
```