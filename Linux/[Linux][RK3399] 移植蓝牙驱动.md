---
title: [Linux][RK3399] 移植蓝牙驱动
tags: bluetooth,rockchip
grammar_cjkRuby: true
---


参考文章：http://blog.csdn.net/linuxheik/article/details/51924026
[TOC]

## 内核配置

[*] Networking support  --->                
<*>   Bluetooth subsystem support  --->  //蓝牙子系统必须选择
<*>   L2CAP protocol suppor      
//逻辑链路控制和适配协议。
<*>   SCO links support           
//蓝牙语音和耳机支持
<*>   RFCOMM protocol suppor      
//面向流的传输协议，支持拨号网络等
[*]   RFCOMM TTY support          
<*>   BNEP protocol support      
 //蓝牙网络封装协议，自组网支持
[*]   Multicast filter support   
 //蓝牙多播，支持支持BNEP
[*]   Protocol filter support //蓝牙多播，支持支持支持BNEP
<*>   HIDP protocol support       
//基本支持协议
Bluetooth device drivers  --->
<*> HCI USB driver              
//USB蓝牙模块支持
<M>HCI UART driver              
//基于串口，CF卡或PCMCIA的蓝牙
<*> HCI BlueFRITZ! USB driver
<*> HCI VHCI (Virtual HCI device) driver
其余的选项，根据自己的蓝牙设备进行调整。

[B]     蓝牙协议栈移植
a)       需要的软件包
可以在http://sourcearchive.com/下载多用到的所有软件包
 (1) D-Bus library 提供简单的应用程序互相通讯
下载地址：http://www.freedesktop.org/wiki/Software/dbus#Download
 (2) GLib library    GLib是GTK+和GNOME工程的基础底层核心程序库，是一个综合用途的实用的轻量级的C程序库，它提供C语言的常用的数据结构的定义、相关的处理函数，有趣而实用的宏，可移植的封装和一些运行时机能，如事件循环、线程、动态调用、对象系统等的API。它能够在类UNIX的操作系统平台（如linux， HP-UNIX等），WINDOWS，OS2和BeOS等操作系统台上运行。
下载地址：http://ftp.gnome.org/pub/gnome/sources/glib/2.26/
(3) USB library (optional) 是一个用c语言开发的跨平台的USB设备访问接口库。
下载地址：http://www.libusb.org/
(4) Lexical Analyzer (flex或 lex)          词法分析器
下载地址：http://linux.softpedia.com/get/Programming/Interpreters/Flex-23296.shtml
(5)YACC (yacc, bison, byacc)           Unix/Linux上一个用来生成编译器的编译器(编译器代码生成器)
下载地址：http://invisible-island.net/byacc/byacc.html
(6) alsa-libALSA 应用
下载地址：http://www.alsa-project.org/
b)        解压编译
在编译之前，首先将下载的所有包都放在 bluetooth 文件夹下。并在该文件夹下建立 bluetooth-build 文件夹，并将其输出到环境变量。
#cd  Bluetooth
#mkdir  bluetooth-build
#blue=$PWD/bluetooth-build
#export blue
#export          //检查是否包含blue环境变量
(1)     编译 alsa-lib 库
#tar  -jxvf alsa-lib-1.0.24.1.tar.bz2
#cd alsa-lib-1.0.24.1
#./configure --prefix=$blue CC=arm-linux-gcc --host=arm-linux --disable-Python
#make
#make install
(2)     编译 expat
#tar –zxvf expat-2.0.1.tar.gz
#cd expat-2.0.1
#./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux
#make
#make install
(3)     D-Bus
#tar  dbus-1.4.1.tar.gz
#cd  dbus-1.4.1
配置configure:
#echo ac_cv_have_abstract_sockets=yes>arm-linux.cache
#./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux--cache-file=arm-linux.cache --with-x=no
(4)     编译 glib 库
#vi arm-linux.cache
在其中输入如下内容：
glib_cv_long_long_format=ll
glib_cv_stack_grows=no
glib_cv_working_bcopy=no
glib_cv_sane_realloc=yes
glib_cv_have_strlcpy=no
glib_cv_va_val_copy=yes
glib_cv_rtldglobal_broken=no
glib_cv_uscore=no
ac_cv_func_posix_getpwuid_r=yes
ac_cv_func_nonposix_getpwuid_r=no
ac_cv_func_posix_getgrgid_r=no
glib_cv_use_pid_surrogate=no
ac_cv_func_printf_unix98=no
ac_cv_func_vsnprintf_c99=no
ac_cv_path_GLIB_COMPILE_SCHEMAS=yes
或者不建立arm-linux.chach文件，直接输入如下命令也可以：
echo glib_cv_long_long_format=ll>arm-linux.cache
echo glib_cv_stack_grows=no>>arm-linux.cache
echo glib_cv_working_bcopy=no>>arm-linux.cache
echo glib_cv_sane_realloc=yes>>arm-linux.cache
echo glib_cv_have_strlcpy=no>>arm-linux.cache
echo glib_cv_va_val_copy=yes>>arm-linux.cache
echo glib_cv_rtldglobal_broken=no>>arm-linux.cache
echo glib_cv_uscore=no>>arm-linux.cache
echo ac_cv_func_posix_getpwuid_r=yes>>arm-linux.cache
echo ac_cv_func_nonposix_getpwuid_r=no>>arm-linux.cache
echo ac_cv_func_posix_getgrgid_r=no>>arm-linux.cache
echo glib_cv_use_pid_surrogate=no>>arm-linux.cache
echo ac_cv_func_printf_unix98=no>>arm-linux.cache
echo ac_cv_func_vsnprintf_c99=no>>arm-linux.cache
echo ac_cv_path_GLIB_COMPILE_SCHEMAS=yes>>arm-linux.cache
 
然后保存退出。如果不创建该文件，编译总出现…can’t run test program …错误
#./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux --cache-file=arm-linux.cache
如果继续出错，记录下提示error错误行的上一行，如：
checking abstract socket namespace...
configure: error: cannot run test program while cross compiling
注意到abstract socket namespace在configure中查找abstract socket可以看到类似这样的结构
echo "$as_me:$LINENO: checking abstract socket namespace" >&5
echo $ECHO_N "checking abstract socket namespace... $ECHO_C" >&6
if test "${ac_cv_have_abstract_sockets+set}" = set; then
echo $ECHO_N "(cached) $ECHO_C" >&6
其中ac_cv_have_abstract_sockets是我们要查找的变量。然后在当前目录下的arm-linux.cache中加入：echo ac_cv_have_abstract_sockets=yes
 
#make
出现如下错误：
(process:18811): GLib-Genmarshal-WARNING **: unknown type: VARIANT
make[2]: *** [stamp-gmarshal.h] 错误 1
make[2]: Leaving directory `/root/mywork/mini2440/bluetooth/glib-2.26.0/gobject'
make[1]: *** [all-recursive] 错误 1
make[1]: Leaving directory `/root/mywork/mini2440/bluetooth/glib-2.26.0'
make: *** [all] 错误 2
出现如上错误好像是文件格式错误引起的。解决办法如下：
第一次出错：将其中唯一的一行注释掉！
#vi gobject/stamp-gmarshal.h
第二次出错：将如下文件的开头空行删除。
#vi gobject/gmarshal.c
这时候，继续编译就通过了。！
#vi tests/gobject/stamp-testmarshal.h
什么也不输入，保存退出即可。
(5)     编译 bluez
#tar  -zxvf  bluez-4.87.tar.gz
#cd  bluez-4.87
# ./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux
#make
#make  install
编译顺利，没初现错误。
(6)     编译YACC
#tar  -zxvf  byacc.tar.gz
#cd  byacc-20101127
# ./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux
#make
#make  install
(7)     编译USB library
#tar  -zxvf  libusb-1.0.8.tar.bz2
#cd  libusb-1.0.8
# ./configure --prefix=$blue CC="arm-linux-gcc -I$blue/include -L$blue/lib " --host=arm-linux
#make
#make  install
至此，所有的软件包都编译完成！
(8)     复制生成的软件到开发板
1)      将bluetooth-build/sbin下的文件复制到开发板的/sbin下
#cp  bluetooth-build/sbin/*    ROOTFS/sbin               //ROOTFS自己指定
#cp  bluetooth-build/bin/hcitool         ROOTFS/bin/
#cp  bluetooth-build/bin/rfcomm              ROOTFS/bin/
#cp  bluetooth-build/bin/sdptool              ROOTFS/bin/
 
2)      复制相关的库到开发板的/lib下
#cp  Bluetooth-build/lib/libbluetooth*    ROOTFS/lib         //ROOTFS自己指定
3)      复制配置文件到开发板的/etc目录下
#cp  -arf bluetooth-build/etc/bluetooth/    ROOTFS/etc/          //ROOTFS自己指定
 
[C]     蓝牙测试
1．检查是否有蓝牙设备
在插入蓝牙到到USB口前后，用 lsusb 命令可以发现输出内容不一样。即插入蓝牙设备后 lsusb 输出多了一行。然后，运行 hciconfig 可以看到：
#hciconfig
hci0:       Type: BR/EDR  Bus: USB
       BD Address: 00:00:00:00:00:00  ACL MTU: 0:0  SCO MTU: 0:0
       DOWN
       RX bytes:0 acl:0 sco:0 events:0 errors:0
       TX bytes:0 acl:0 sco:0 commands:0 errors:0
上面的信息说明检测到了蓝牙设备hci0。
2．激活蓝牙设备
#hciconfig hci0 up
可以激活借口(这一步不做，hcitool scan无法运行) 。这时候如果再次执行hciconfg命令，可以发现蓝牙以及激活(UP RUNNING)：
hci0:       Type: BR/EDR  Bus: USB
       BD Address: 00:1F:81:00:02:DD  ACL MTU: 1021:4  SCO MTU: 180:1
       UP RUNNING
       RX bytes:342 acl:0 sco:0 events:10 errors:0
       TX bytes:33 acl:0 sco:0 commands:11 errors:1
3．扫描设备
#hcitool scan
可以得到：
Scanning ...
       00:23:7A:F3:66:8D     BlackBerry 9000                这就是搜索到的设备（提前打开哦）
4．修改配置文件：
修改/etc/bluetooth/rfcomm.conf
将里面的：device 11:22:33:44:55:66;
修改成hcitool scan的结果，也就是：
device 00:23:7A:F3:66:8D
保存退出。
rfcomm_create_dev。
5．创建蓝牙设备
运行：
#rfcomm_create_dev。
