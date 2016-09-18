---
title: Android 启动流程
tags:
grammar_cjkRuby: true
---
[TOC]

## 概览


## 一、Android 底层启动流程
### 1. 系统上电并执行 ROM 引导代码
#### 1.1 由 PC 引出 Android 
PC 系统启动机制我们比较熟悉。
1. 系统上电
2. BIOS 被载入到硬盘的扇区 MBR
3. 运行启动程序 BIOS 并开始引导系统
Android 系统很类似
#### 1.2 Android 底层启动流程
1. CPU 上电
2. PC 指针指向 ROM 启动代码（零地址），即 Bootloader
3. 直接执行启动代码 / 将代码载入到 RAM 后执行
两种执行方式取决于是由 Nor Flash 还是 Nand Flash 存储 Bootloader。
#### 1.3 Nor Flash 与 Nand Flash 中的 Bootloader
Nor Flash 支持字节寻址，可以直接在 ROM 中执行。
Nand Flash 不支持字节寻址，需要将 Bootloader 加载到 RAM 中后才能执行。
具体 Bootloader 的定义和种类放在下一节细表。
##### Nor Flash
1. 上电后，PC 指向 ROM 的零地址，开始执行Bootloader（汇编部分）
2. 配置 EMI 寄存器（存储器地址 & 存取规则）
3. 配置电源模块，使各个模块上电
4. 为了提高执行效率，将 Nor Flash 中的代码复制到内存中
5. PC 指针指向 RAM 中映射的地址，并开始执行 Bootloader（c 部分）
##### Nand Flash
1. 上电后，DMA 将 Nand Flash 中的 Bootloader 启动代码复制到 **CPU 内部的 RAM** 中
2.  PC 指向 RAM 代码的首地址，执行 Bootloader（汇编部分）
3.  Bootloader 中设置中断向量和设置硬件配置
4.  计算 Bootloader 大小，预留空间，将执行代码搬运到 SDRAM 或者 DD-RAM 等**外部 RAM** 中。
5.  设置 Remap，映射 零地址 到 SDRAM 或者 DDRAM 中的首地址
6.  设置 PC 指针到 零地址，开始执行 Bootloader（c 部分）

### 2. Bootloader 引导程序
#### 2.1 作用
**简单地说**，BootLoader是在操作系统运行之前运行的一段程序，它可以将系统的软硬件环境带到一个合适状态，为运行操作系统做好准备。
**微观地说**，Bootloader 负责初始化硬件设备，建立内存空间映射图，为内核启动准备好软件、硬件环境。

Bootloader 阶段通常都包含有处理器厂商开发的上电引导程序 + u-boot（一个通用的 Bootloader）。
#### 2.2 处理器厂商的上电引导程序
不同厂商可能会自己定制一部分内容（对 arm core 进行封装），差异比较大，所以不同的arm处理器，对于上电引导都是由特定处理器芯片厂商自己开发的程序，这个上电引导程序通常比较简单，会初始化硬件，提供下载模式等，然后才会加载通常的 Bootloader（u-boot）。
#### 2.3 U-boot
u-boot 大致包括两个阶段，汇编代码（start.S） & C 代码。

### 3. Linux 内核
#### 3.1 内核（Kernel）的启动流程
1. Kernel 初始化
2. 设备驱动初始化
3. Kernel 启动
4. 挂载文件系统
5. 启动用户空间进程
#### 3.2 Kernel 初始化
主要对硬件进行配置。
**向量表** : 创建异常向量表 和 初始化中断处理函数;
**进程调度器** : 初始化系统核心进程调度器 和 时钟中断处理机制;
**串口** : 初始化串口控制台;
**缓存** : 创建和初始化系统, 为内存调用提供缓存;
**内存管理** : 初始化内存管理, 检测内存大小及碑内核占用的内存情况;
**进程通信** : 初始化系统进程通信机制;
#### 3.3 设备驱动初始化
设备初始化 : 加载设备驱动, 主要有 静态加载 和 动态加载两种方式;
**静态加载** : 将驱动模块加载到内核中, 设备驱动会在内核启动的时候自动加载, 这种驱动是无法卸载的;
**动态加载** : 在系统中使用 modprobe 或者 insmod 进行设备驱动模块的加载, 使用 rmmod 进行设备驱动模块卸载;
#### 3.4 挂载文件系统
**创建并挂载根设备** : kernel 初始化 和 设备初始化 之后会创建 根设备, 根设备文件系统以只读方式挂载;
**释放内存到根设备** : 根设备创建成功之后, 根设备是只读的, 这时释放未使用的内存到 根设备上;
#### 3.5 启动 init 程序
启动应用程序 : 根文件挂载成功后, 启动 /sbin/init 程序, 这是 linux 系统第一个应用程序, 启动成功后 init 进程会获得 linux 系统的控制权;
**硬件初始化** : 初始化 Android 设备硬件;
**挂载根文件** : 根据命令行参数挂载根文件系统;
**跑启动脚本** : 执行用户自定义的 init 启动脚本;

### 4. init 初始化系统服务
（1）**init 初始化系统服务**
**Linux 中 init 进程简介 :**
-- 系统父进程 : init 进程是 Linux 系统所有进程的 父进程, id 为 1;
-- init 进程作用 : 
1. 初始化 和 启动 系统, 创建其它进程 如 shell login 等进程;
2. 子进程的终止处理;
3. 提供属性服务，保存系统运行所需要的环境变量。
**Android 中 init 进程简介 :** 
-- 系统父进程 : init 在 Android 中也是第一个进程, id 为 1;
-- 创建其它进程 : 创建 zygote 进程, 该进程可以提供 属性服务 用于管理系统属性;
（2）**init 完成操作**
init 操作 : 系统初始化操作, 解析 init.rc 配置文件等操作;
-- 初始化 : 初始化 log 系统;
-- 解析配置 : 解析 init.rc 配置文件 和 /init.硬件平台名称.rc 配置文件, 执行 early-init, 解析 init 动作, eartly-boot 动作, boot 动作, Execute property 动作;
-- 初始化2 : 设备初始化, 属性服务初始化, 开启属性服务; 
-- 无限循环 : 进入无限循环状态, 等待属性设置 或 子进程退出事件;

注册消息处理器
创建并且挂载所需要的文件目录（socket 文件，虚拟内存文件）
创建设备节点文件、输出 log 文件，将错误信息重定向到这里
解析 init.rc 脚本（init.rc 用于通用环境变量和进程相关的定义）
iparse_config_file 来读取脚本，然后生成服务列表和动作列表
服务列表（service）和动作列表（on）会注册到 service_list 和 action_list 中，其为 init 进程中声明的全局结构体
device_init 来生成静态设备节点


（3） init.rc 配置文件解析
http://blog.csdn.net/dearsq/article/details/52100130


## 二、Android 上层启动流程
### 1. 上层系统启动简介
1. init 进程启动
2. Native Service（Android系统本地服务）
3. Zygote 进程
4. System Service（Android系统服务）
5. HomeActivity
### 2. 启动 Native Service 本地服务
由 init 启动，C/C++ 实现。启动项定义在 init.rc 中
#### 作用
Native Service 是 Android 内核 与 Android 通信 的通道，利用 socket 进行通信。
**Console** : shell console 服务;
**Service Manager** : Binder 服务管理器, 管理所有的 Android 系统服务;
**Vold** : 支持外设热插拔服务;
**Mountd** : 设备安装 状态通知服务;
**Debuggerd** : 处理调试进程请求服务;
**Rild** : 无线接口层服务;
**Zygote** : 启动 Dalvik 并创建其它进程服务;
**MediaServer** : 多媒体相关服务;

### 3. Zygote 进程启动
Zygote 由 init 进程创建，init.rc 中配置了 Zygote 的创建参数。
init.rc 中配置：Zygote 原始名称是“app_process”，启动中改名为 Zygote
#### 作用
本质 : Zygote 进程是一个虚拟的进程, 是虚拟实例(Dalvik虚拟机)的孵化器;
操作 : Zygote 负责 Dalvik 虚拟机初始化, 预置类库加载等操作;
应用启动处理 : 每个 Android 应用启动时, Zygote 会创建一个子进程(Dalvik虚拟机)执行它;
节省内存策略 : Android 中有些系统库是只读的, 所有的 Dalvik 虚拟机都可以共享这些只读系统库;
### 4. Android SystemService 启动
-- 启动 : Android System Service 是 Zygote 进程的第一个子进程, 由 Zygote 进程孵化而来;
-- 作用 : System Service 是 Android 框架核心, 负责 Android 系统初始化 并 启动其它服务;
-- 其它服务 : System Service 孵化的其它服务运行在对应 Dalvik 虚拟机进程的空间里;
-- init.rc 配置 : 在 Zygote 配置中 "--start-system-server" 参数用来实现 System Service 的启动;
### 5. 启动 HomeActivity 主界面
Launcher 应用程序 : 该应用程序就是 HomeActivity 所在的程序;
-- 启动 : Launcher 由 Activity Manager Service 启动, 启动流程 System Service -> Activity Manager Service -> Launcher;
-- 展示图标 : Launcher 启动后就会将已经安装的 app 程序的快捷图标展示到桌面;

## 三、代码实现



## 参考文献
[1][Android系统启动流程 -- bootloader](http://blog.csdn.net/lizhiguo0532/article/details/7017503)
[2][ 【Android 系统开发】 Android 系统启动流程简介](http://blog.csdn.net/shulianghan/article/details/39125439)