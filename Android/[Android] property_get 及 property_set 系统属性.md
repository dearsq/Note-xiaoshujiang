---
title: [Android] property_get 及 property_set 系统属性
tags: Android
grammar_cjkRuby: true
---
[TOC]

## 概念
**属性** 这个概念被大量用于 Android 当中。
**属性** 是用来**记录系统设置**或**进程之间的信息交换**。
每个属性都有名称和值，他们都是字符串的格式。
属性在整个系统中是全局可见的，每个进程都可以 get/set 属性。

## 创建过程
### 系统初始化 init
在系统初始化时，Android 将分配一个**共享内存区**来存储属性。这些是由“init” 守护进程完成的，其源代码位于：sysrtem/core/init/。“init” 守护进程将启动一个属性服务。

属性服务在“init”守护进程中运行。
每一个客户端想要**设置属性**时，必须连**接属性服务**，再**向其发送信息**。
属性服务将会在共享内存区中修改和创建属性。
任何客户端想获得属性信息，可以从共享内存直接读取。这提高了读取性能。 
属性服务调用libc中的 \__system_property_init函数来初始化属性系统的共享内存。当启动属性服务时，将从以下文件中加载默认属性：
```
/default.prop
/system/build.prop
/system/default.prop
/data/local.prop
```
属性将会以上述顺序加载。后加载的属性将覆盖原先的值。这些属性加载之后，最后加载的属性会被保持在 /data/property 中。

### build.prop
/system/build.prop 是一个属性文件
build/tools/buildinfo.sh 脚本就是专门用于生成build.prop文件
build/core/Makefile中使用build/tools/buildinfo.sh 脚本生成build.prop文件，并把系统默认的system.prop 以及定制的 system.prop 中的设定追加到build.prop文件中。
生成 build.prop 具体的加载流程分析见 http://blog.csdn.net/thl789/article/details/7014300
build.prop 代码中的详细含义见 http://blog.csdn.net/ouyang_peng/article/details/9426271


## 用法
### API
客户端应用程序可以调用libcutils中的API函数以GET/SET属性信息。libcutils的源代码位于：device/libs/cutils。API函数是：
```c
int property_get(const char *key, char *value, const char *default_value);
int property_set(const char *key, const char *value);
```

### 特别属性
如果属性名称以 **“ro.”开头**，那么这个属性被视为只读属性。一旦设置，属性值不能改变。
 
如果属性名称以 **“persist.”开头**，当设置这个属性时，其值也将写入/data/property。
 
如果属性名称以 **“net.”开头**，当设置这个属性时，“net.change”属性将会自动设置，以加入到最后修改的属性名。（这是很巧妙的。 netresolve模块的使用这个属性来追踪在 net.* 属性上的任何变化。）
 
属性 **“ ctrl.start ”和 “ ctrl.stop ”**是用来启动和停止服务。
 
 
每一项服务必须在 /init.rc 中定义。
系统启动时，与 init 守护进程将解析 init.rc 和 启动属性服务。一旦收到设置“ ctrl.start ”属性的请求，属性服务将使用该属性值作为服务名找到该服务，启动该服务。
这项服务的启动结果将会放入“ init.svc.<服务名>“属性中 。客户端应用程序可以轮询那个属性值，以确定结果。




