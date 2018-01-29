---
title: [IoT3G] MTK 开发环境搭建
tags: Bug,Android
grammar_cjkRuby: true
---
Hardware: MTK6572
Android: 4.4(API 19)
Kernel: Linux 3.4.67

#### **Check SDK Version**

```
vi build/core/version_defaults.mk

  PLATFORM_VERSION := 4.4.2    
  PLATFORM_SDK_VERSION := 19   #Android4.4
  
vi kernel/Makefile
VERSION = 3
PATCHLEVEL = 4
SUBLEVEL = 67
```

### 安装编译环境

对于Ubuntu14.04 

#### 安装 sun/oracle jdk 1.6
但是已经被从 Ubuntu14.04 源中移除了，所以手动下载：http://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase6-419409.html#jdk-6u45-oth-JPR

```
$ sudo cp -p jdk-6u45-linux-x64.bin /usr/java/
$ cd /usr/java
$ sudo chmod a+x /usr/java/jdk-6u45-linux-x64.bin
$ sudo ./jdk-6u45-linux-x64.bin
```
会自动解压并生成 `/usr/jvm/jdk1.6.0_45`

#### 配置 JAVA 环境变量
```
sudo vi /etc/profile 
```
添加
```
export JAVA_HOME=/usr/java/jdk1.6.0_45
export JRE_HOME=/usr/java/jdk1.6.0_45/jre
export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH
export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH
```
```
$ source /etc/profile
$ java -version
java version "1.6.0_45"
Java(TM) SE Runtime Environment (build 1.6.0_45-b06)
Java HotSpot(TM) 64-Bit Server VM (build 20.45-b01, mixed mode)
```
即配置成功。

存在多个版本的JAVA可以配置可选项
```
update-alternatives --install /usr/bin/javac javac /usr/java/jdk1.6.0_45/bin/javac 1
update-alternatives --install /usr/bin/java java /usr/java/jdk1.6.0_45/bin/java 1
update-alternatives --install /usr/bin/javap javap /usr/java/jdk1.6.0_45/bin/javap 1
update-alternatives --install /usr/bin/javadoc javadoc /usr/java/jdk1.6.0_45/bin/javadoc 1
update-alternatives --install /usr/bin/javaws javaws /usr/java/jdk1.6.0_45/bin/javaws 1
update-alternatives --install /usr/bin/javah javah /usr/java/jdk1.6.0_45/bin/javah 1
update-alternatives --config java （javac、javap等）可以选对应版本。
```

以后可以通过如下方式切换
```
sudo update-alternatives --config java
There are 4 choices for the alternative java (providing /usr/bin/java).

  Selection    Path                                                 Priority   Status
------------------------------------------------------------
* 0            /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java        1071      auto mode
  1            /usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java        1061      manual mode
  2            /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java        1071      manual mode
  3            /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java        1069      manual mode
  4            /xspace/Public/App/Java1.6_SDK/jdk1.6.0_31/bin/java   300       manual mode
```
选择 4 ，即为 sun jdk 1.6


需要 gcc4.4
```
## 安装 gcc4.4
$ sudo apt install gcc-4.4
## 查看系统内现有 gcc 版本并切换
$ ls /usr/bin/gcc-4*
/usr/bin/gcc-4.4  /usr/bin/gcc-4.6  /usr/bin/gcc-4.8

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.4 50

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.6 40

$ sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 20

$ sudo update-alternatives --config gcc
There are 3 choices for the alternative gcc (providing /usr/bin/gcc).

  Selection    Path              Priority   Status
------------------------------------------------------------
* 0            /usr/bin/gcc-4.4   50        auto mode
  1            /usr/bin/gcc-4.4   50        manual mode
  2            /usr/bin/gcc-4.6   40        manual mode
  3            /usr/bin/gcc-4.8   20        manual mode

Press enter to keep the current choice[*], or type selection number: 
```
这里我们要选 gcc 4.4。


#### MTK 原生编译命令

```
./mk --help
```

#### 脚本编译

```
$ cd /orangepi/scripts/
$ ./auto.sh IoT03_mt6572_emmc_b1258_32g4g_ry_smt v00 eng
```

##### cc1plus 不存在
```
gcc and g++ error: error trying to exec 'cc1plus': execvp: No such file or directory
```
```
$ ls /usr/bin/g++*
/usr/bin/g++  /usr/bin/g++-4.6  /usr/bin/g++-4.8
# 第一个 /usr/bin/g++ 为软连接，其软连接失败。
$ sudo apt install g++-4.4
```
