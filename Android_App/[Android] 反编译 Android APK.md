---
title: [Android] 反编译 Android APK 
tags: android
grammar_cjkRuby: true
---
https://blog.csdn.net/m0_37433067/article/details/79717253

工具（Ubuntu平台下）： 
a. apktool: 主要将apk中，资源文件及XML文件进行反编译。 
https://download.csdn.net/download/m0_37433067/10311837 
b.dex2jar：将dex文件转为jar包及.class文件 
https://download.csdn.net/download/m0_37433067/10311848 
c.jd-gui-0.3.3.linux.i686: jar\dex.samil源码查看工具 
https://download.csdn.net/download/m0_37433067/10311855 
工具准备完成。解压好几个文件。使用到解压软件，安装unzip与zip我不过多说明 


## 步骤
### 1. dex2jar
.apk 解压, 获取 classes.dex  文件
./dex2jar.sh classes.dex 

### 2. jd-gui

$ sudo apt-get install libgtk2.0-0:i386
$ ./jd-gui
open file 可以看到源码

### 3. apktool
./apktool d -f  xxx.apk
获取资源文件res
