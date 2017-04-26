[TOC]

## 概述

总得来看有这样几个阶段：
1. BootROM 上电
2. BootLoader 引导
3. Linux 内核
4. init 进程
5. Zygote 启动

![gityuan 绘制的 Android 系统架构框图](https://ws4.sinaimg.cn/large/ba061518gw1fasfsv56ofj21ay16p43l.jpg)

展开一点来看

1. 板子上电后运行固化在 ROM 中的代码，加载 Bootloader 到 RAM。
2. Bootloader 启动，引导进入 Linux 内核。
3. **Kernel 启动 swapper 进程**。即 idle 进程，pid = 0，系统初始化过程中的第一个进程，用于初始化 进程管理、内存管理、加载 Display、Camera Driver、Binder Driver 的工作。
**Kernel 启动 init 进程**（用户进程的祖宗）。pid = 1，用来孵化用户空间的守护进程、HAL、开机动画等。
**Kernel 启动 threadd 进程**（内核进程的祖宗）。pid = 2，创建内核工程线程 kworkder，软中断线程等。

4. init 进程 fork 出 Daemon 进程：孵化出ueventd、logd、healthd、installd、adbd、lmkd 等用户守护进程；
init 进程启动servicemanager(binder服务管家)、bootanim(开机动画)等重要服务;
**init 进程孵化出Zygote进程**，Zygote进程是Android系统的第一个Java进程，Zygote是所有Java进程的父进程（Android 应用程序的祖宗），Zygote进程本身是由 init 进程孵化而来的。

5. Zygote 孵化出 System Server 和 App。
它是 Android 系统的核心进程，提供了应用程序生命周期管理，地理位置信息等各种 Service（这些 Service 同样需要注册到 Context Manager）。

下面我们具体的一个个的来分析。

## 一、BootROM
按下电源后，引导芯片代码从预定义的地方（固化在 ROM）开始执行。
加载引导程序到 RAM，然后执行引导程序（bootloader）。

![](https://ws1.sinaimg.cn/large/ba061518gw1fasfuv2r3dj20oe0f3796.jpg)

## 二、Bootloader 引导程序
Bootloader 有很多，最常见的就是 uboot。

按所执行的功能分为两个阶段：
1. 检测外部的 RAM 以及加载对第二阶段有用的程序。
2. 引导程序设置网络、内存等等。这些对于运行内核是必要的，为了达到特殊的目标，引导程序可以根据配置参数或者输入数据设置内核。

按代码来看分成两个部分：
1. init.S 初始化堆栈，清零BSS段，调用main.c的_main() 函数。
2. main.c 初始化硬件（闹钟、主板、键盘、控制台），创建 linux 标签。

## 三、Linux 内核
内核启动时，设置缓存、被保护存储器、计划列表，加载驱动。当内核完成系统设置，它首先在系统文件中寻找”init”文件，然后启动 root 进程或者系统的第一个进程。

![](https://ws2.sinaimg.cn/large/ba061518gw1fasims09bzj20ja0aimyy.jpg)

> kernel 的入口点是 stext，这是一个汇编函数。
从stext开始kernel将会完成一系列通过汇编语言实现芯片级的初始化工作，并以静态定义的方式创建kernel的第一个kernel进程init_task，即 0号进程。
然后跳转到kernel的第一个c语言函数start_kernel完成后续十分繁杂的kernel初始化工作（setup_arch，mm_init，sched_init，init_IRQ以及最为关键的rest_init等几个函数）
在rest_init中创建了kernel的第二个kernel进程 kernel_init（1号进程）和第二个kernel进程kthreadd（2号进程），对于驱动工程来说，需要关注下kernel_init调用的do_basic_setup函数，其完成了系统驱动初始化工作。
最后kernel_init通过调用run_init_process("/init”)，开始执行init程序，并从kernel进程转化为第一个用户进程。

参考：[Kernel 启动流程源码总结](http://blog.csdn.net/xichangbao/article/details/52971562)


## 四、init 进程
init 进程是Linux系统中用户空间的第一个进程，进程号为1。
它是 用户进程 的祖先。
### 关键路径
init 进程  	/system/core/init
init.rc 脚本 	/system/core/rootdir/init.rc
readme.txt	/system/core/init/readme.txt

![](https://ws4.sinaimg.cn/large/ba061518gw1fashn2h1hlj20jn0cuaby.jpg)

### 作用
1. 分析和运行所有的init.rc文件; //parser.ParseConfig("/init.rc");
2. 生成设备驱动节点; （通过rc文件创建）
3. 处理子进程的终止(signal方式);
4. 提供属性服务。 //start_property_service()
5. 创建 Zygote 
5.1 解析 init.zygote.rc //parse_service()
5.2 启动 main 类型服务 //do_class_start()
5.3 启动 zygote 服务 //service_start()
5.4 创建 Zygote 进程 //fork()
5.5 创建 Zygote Socket //create_socket()

init.rc 中启动的 Action 和 Service ：
**on early-init**：设置init进程以及它创建的子进程的优先级，设置init进程的安全环境
**on init**：设置全局环境，为cpu accounting创建cgroup(资源控制)挂载点
**on fs**：挂载mtd分区
**on post-fs**：改变系统目录的访问权限
**on post-fs-data**：改变/data目录以及它的子目录的访问权限
**on boot**：基本网络的初始化，内存管理等等
**service servicemanager**：启动系统管理器管理所有的本地服务，比如位置、音频、Shared preference等等…
**service zygote**：启动zygote作为应用进程

![](https://ws2.sinaimg.cn/large/ba061518gw1fasilbde07j20h00cwmyz.jpg)

参考：[Android 的 Init 进程](http://blog.csdn.net/xichangbao/article/details/53024698)
参考：[Android系统启动-init篇](http://blog.csdn.net/omnispace/article/details/51773286)

## 五、Zygote 创建与启动应用
### Zygote 是什么
Zygote 顾名思义，是所有 Android 应用的祖先。

最开始，在 Java 中，不同的虚拟机实例可以为不同的应用分配不同的内存。但如果Android系统为每一个应用启动不同的 VM 实例，就会消耗大量的内存以及时间。因此，为了克服这个问题，Android系统创造了“Zygote”。

**Zygote 让 VM 共享代码、低内存占用以及最小的启动时间成为可能。** Zygote 是一个虚拟机进程，正如我们在前一个步骤所说的在系统引导的时候启动。Zygote 预加载以及初始化核心库类。通常，这些核心类一般是只读的，也是 Android SDK 或者核心框架的一部分。在Java虚拟机中，每一个实例都有它自己的核心库类文件和堆对象的拷贝。

### 关键代码路径
framework 层
```
App_main.main
    AndroidRuntime.start
        startVm
        startReg
        ZygoteInit.main
            registerZygoteSocket
            preload
            startSystemServer
            runSelectLoop
```

### 流程分析

Zygote是由init进程通过解析init.zygote.rc文件而创建的，zygote所对应的可执行程序app_process，所对应的源文件是App_main.cpp，进程名为zygote。

![](https://ws4.sinaimg.cn/large/ba061518gw1fasilxuuilj20ie0aqgny.jpg)

#### **创建虚拟机 //App_main.cpp**
1. 首先生成了一个 AppRuntime 对象，该类是继承自AndroidRuntime的，该类用来初始化并且运行 VM，为运行Android应用做好准备。//AndroidRuntime.start
接受main 函数传递进来的参数，-Xzygote /system/bin --zygote --start-system-server 然后初始化虚拟机
2. startVM。调用 JNI_CreateJavaVM 创建虚拟机。
3. startReg。JNI 函数注册。

#### **虚拟机初始化之后 //ZygoteInit.java** 
ZygoteInit 代码流程：
1. 绑定套接字。接受 Activity  Manager 来的应用启动请求。
2. 加载 Android Framework 中的 class、res（drawable、xml信息、strings）到内存。
Android 通过在 Zygote 创建的时候加载资源，生成信息链接，再有应用启动，fork 子进程和父进程共享信息，不需要重新加载，同时也共享 VM。
3. 启动 System Server。因为我们的应用启动需要这些 server 的参与，所以需要先启动 System Server。接下来启动 ServerThread 来执行 Android Framework 服务，并通过 JNI 向 Context Manager 注册。
4. Zygote 在轮询监听 Socket，当有请求到达，读取请求，fork 子进程，加载进程需要的类，执行所要执行程序的 Main。代码转给了 VM，App 也启动起来了。然后 Zygote 关闭套接字，删除请求描述符，防止重复启动。

参考 [Android系统启动-zygote篇](http://blog.csdn.net/omnispace/article/details/51773292)

## 六、SystemServer
Zygote启动过程中会调用startSystemServer()，可知startSystemServer()函数是system_server启动流程的起点， 启动流程图如下：
![](https://ws4.sinaimg.cn/large/ba061518gw1fashspfi0kj20vv095ab4.jpg)

![](https://ws4.sinaimg.cn/large/ba061518gw1fasig0fsj0j20qs0m4ac5.jpg)
system_server进程，从源码角度划分为引导服务、核心服务、其他服务3类。
引导服务(7个)：ActivityManagerService、PowerManagerService、LightsService、DisplayManagerService、PackageManagerService、UserManagerService、SensorService；
核心服务(3个)：BatteryService、UsageStatsService、WebViewUpdateService；
其他服务(70个+)：AlarmManagerService、VibratorService等。


参考：http://gityuan.com/2016/02/14/android-system-server/

## 七、引导结束
System Servers 在内存中跑起来后，发送开机广播 “ACTION_BOOT_COMPLETED”。





