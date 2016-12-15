[TOC]

## 概述

总得来看有这样几个阶段：
1. BootROM 上电
2. BootLoader 引导
3. Linux 内核
4. init 进程
5. Zygote 启动

展开一点来看

1. 板子上电后运行固化在 ROM 中的代码，引导进入 Bootloader。
2. Bootloader 启动，引导进入 Linux 内核。
3. 内核通过 start_kernel() 启动 init 进程。
4. init 进程先 fork() 来创建子进程：
**首先 fork 出 Daemon 进程（守护进程）。** 包括 USB 守护进程、Debug 进程、无线通信连接守护进程;
**然后 fork 出 Context Manager。** Android System 提供的所有 Service 都需要 Context Manager 注册，然后其他的进程才能够调用这个服务。
**然后 fork 出 Media Server。** 这是 Native 服务，不是 Java 服务，所以不需要 VM。包括 Audio Flinger、Camera Service。
**然后 fork 出 Zygote。** 和它的中文（受精卵）一样，它是所有 Android 应用程序的祖先。用它来孵化 Java 系统服务，同时孵化应用程序。
5. Zygote 孵化出 System Server 和 App。
它是 Android System 的核心进程，提供了应用程序声明周期管理，地理位置信息等各种 Service（这些 Service 同样需要注册到 Context Manager）。

下面我们具体的一个个的来分析。

## 一、BootROM
按下电源后，引导芯片代码从预定义的地方（固化在 ROM）开始执行。
加载引导程序到 RAM，然后执行引导程序（bootloader）。

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
![](https://ws4.sinaimg.cn/large/ba061518gw1farh6dq9odj20iv09zq4w.jpg)

> kernel 的入口点是 stext，这是一个汇编函数。
从stext开始kernel将会完成一系列通过汇编语言实现芯片级的初始化工作，并以静态定义的方式创建kernel的第一个kernel进程init_task，即 0号进程。
然后跳转到kernel的第一个c语言函数start_kernel完成后续十分繁杂的kernel初始化工作（setup_arch，mm_init，sched_init，init_IRQ以及最为关键的rest_init等几个函数）
在rest_init中创建了kernel的第二个kernel进程 kernel_init（1号进程）和第二个kernel进程kthreadd（2号进程），对于驱动工程来说，需要关注下kernel_init调用的do_basic_setup函数，其完成了系统驱动初始化工作。
最后kernel_init通过调用run_init_process("/init”)，开始执行init程序，并从kernel进程转化为第一个用户进程。

参考：[Kernel 启动流程源码总结](http://blog.csdn.net/xichangbao/article/details/52971562)


## 四、init 进程
init 进程是Linux系统中用户空间的第一个进程，进程号为1。
它是用户态所有进程的祖先。
### 关键路径
init 进程  	/system/core/init
init.rc 脚本 	/system/core/rootdir/init.rc
readme.txt	/system/core/init/readme.txt

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

![](https://ws4.sinaimg.cn/large/ba061518gw1fari9an4vmj20fq0cgabl.jpg)

### 细节（可跳过）
1. init 进程会先注册一些消息处理器；
2. 然后是创建并挂载启动所需要的文件目录（socket文件，虚拟内存文件）；
3. 在dev目录下创建设备节点文件，创建输出log的文件，同时将错误信息重定向到这里。

> 何为设备节点文件：
> Linux对于系统中的设备都会抽象成一个文件，内核为了高效的管理已经被打开的文件，通过一个文件描述符来表示，在Linux中Everything is file，通过这种方式，对于启动的时候，对于文件描述符，0代表标注输入，1表示标准输出，2是错误处理，然后设备文件，socket文件都会获得一个文件描述符来表述它。但是Linux会对其做相应的限制，同时可能会对一些进程进行限制，限制给进程分配多少个文件描述符。
> 创建设备节点文件：
> 应用程序通过驱动程序访问硬件设备，设备节点文件是设备驱动的逻辑文件，应用程序通过设备节点文件来访问设备驱动程序。
> 设备节点的两种创建方式，一种，根据预先定义的设备信息，创建设备节点文件，第二种，在系统运行中，当设备插入时，init进程会接收这一事件，为插入设备动态创建设备节点文件。
>当设备插入的时候内核会加载相应的驱动程序，而后驱动程序会调用启动函数probe，将主，次设备号类型保存到/sys文件系统中。然后发出 uevent，并传递给守护进程，uevent，是内核向用户空间进程传递信息的信号系统，内核通过 uevent 将信息传递到用户空间，守护进程会根据 uevent 读取设备信息，创建设备节点文件。对于一些设备，采用冷插拔的方式，监听设备的uevent，然后调用其函数，创建设备节点文件。

4. init进程生成输出设备之后，开始解析init.rc脚本文件，记录init进程执行的功能, init.rc用于通用的环境变量和进程相关的定义，通过函数 iparse_config_file 来读取其脚本。读取分析之后，生成服务列表和动作列表。

> init.rc 的语言是 AIL（Android Init Language）。
> init.rc文件大致上分为两个部分，一部分是以“on”关键字开头的动作列表，另一部分是以“service”关键字开头的服务服务列表。
> 动作列表：主要设置环境变量，生成系统运行所需的文件或目录，修改相应的权限，并挂载和系统运行相关的目录。在挂载文件的时候，主要挂载/system和/data两个目录，两个目录挂载完毕，android根文件系统准备好了。根文件系统大致可分为shell使用程序，system目录（提供库和基础应用），data目录（保存用户应用和数据）,Android采用闪存设备，其采用了yaffs2文件系统，启动的时候要挂载到/system和/data目录下，然后是on boot段落，该部分设置应用程序终止条件，应用程序驱动目录和文件权限。为各应用制定 OOM，OOM用来监视内核分配给应用程序的内存，当内存不足的时候，应用程序会被终止执行。init.rc文件分析函数，它通过read_file函数，parse_config 函数，用来分析读入的字符串。
> 服务列表：用来记录 init 进程启动的进程，由 init 进程启动的子进程或者是一次性程序，系统相关的 Daemon 进程。

5. 服务列表和动作列表会注册到service_list和action_list中，其为在init进程中声明的全局结构体，调用device_init函数，生成静态设备结点文件，之后，全局属性值的生成在init进程中propertyinit函数中进行初始化，在共享内存区域，创建并初始化属性值，对于全局属性的修改，只有init进程可以修改，当要修改的时候，需要预先向其提交申请，然后init进程通过之后，才会去修改属性值，提交申请的过程会创建一个socket用来接收提交的申请。（执行到这系统将Android系统的Logo显示在LCD上）

6. 这个时候设置事件处理循环的监视事件，注册在POLL中的文件描述符会在poll函数中等待事件，事件发生，则从poll函数中跳出并处理事件。各种文件描述符都会前来注册。

参考： [Android 的 Init 进程](http://blog.csdn.net/xichangbao/article/details/53024698)
参考：[Android系统启动-init篇](http://blog.csdn.net/omnispace/article/details/51773286)

## 五、Zygote 创建与启动应用
### Zygote 是什么
Zygote 顾名思义，是所有应用的祖先。因为 Zygote 是 Java 代码，所以需要装载到 AndroidRuntime VM （ART）上执行。

在 Java 中，不同的虚拟机实例可以为不同的应用分配不同的内存。但如果Android系统为每一个应用启动不同的 VM 实例，就会消耗大量的内存以及时间。因此，为了克服这个问题，Android系统创造了”Zygote”。

Zygote 让 VM 共享代码、低内存占用以及最小的启动时间成为可能。Zygote 是一个虚拟机进程，正如我们在前一个步骤所说的在系统引导的时候启动。Zygote 预加载以及初始化核心库类。通常，这些核心类一般是只读的，也是Android SDK或者核心框架的一部分。在Java虚拟机 中，每一个实例都有它自己的核心库类文件和堆对象的拷贝。

### 关键代码
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

1. 创建虚拟机 //App_main.cpp
1）首先生成了一个 AppRuntime 对象，该类是继承自AndroidRuntime的，该类用来初始化并且运行 VM，为运行Android应用做好准备。//AndroidRuntime.start
接受main 函数传递进来的参数，-Xzygote /system/bin --zygote --start-system-server 然后初始化虚拟机
2）startVM。调用 JNI_CreateJavaVM 创建虚拟机。
3）startReg。JNI 函数注册。

2. 虚拟机初始化之后 //ZygoteInit.java 
1）运行 ZygoteInit 类 main **注意代码已经变成 java 代码了**
2）registerZygoteSocket()为zygote命令连接注册一个服务器套接字。
3）preloadClassed “preloaded-classes”是一个简单的包含一系列需要预加载类的文本文件，你可以在< Android Source>/frameworks/base找到“preloaded-classes”文件。
4）preloadResources() preloadResources也意味着本地主题、布局以及android.R文件中包含的所有东西都会用这个方法加载。
//这个阶段可以看到开机动画

3. Zygote 作用过程 
现在程序的执行转向了虚拟机 Java 代码的执行，首先执行 main 函数，接下来就是 Zygote 的作用过程了。

参考 [Android系统启动-zygote篇](http://blog.csdn.net/omnispace/article/details/51773292)

### 启动应用


ZygoteInit 代码流程：
1. 绑定套接字。接受 Activity  Manager 来的应用启动请求。
2. 加载 Android Framework 中的 class、res（drawable、xml信息、strings）到内存。
Android 通过在 Zygote 创建的时候加载资源，生成信息链接，再有应用启动，fork 子进程和父进程共享信息，不需要重新加载，同时也共享虚拟机。
3. 启动 System Server。因为我们的应用启动需要这些 server 的参与，所以需要先启动 System Server。接下来启动 ServerThread 来执行 Android Framework 服务，并通过 JNI 向 Context Manager 注册。
4. Zygote 在轮询监听 Socket，当有请求到达，读取请求，fork 子进程，加载进程需要的类，执行所要执行程序的 Main。代码转给了 Dalvik VM，App 也启动起来了。然后 Zygote 关闭套接字，删除请求描述
符，防止重复启动。

## 六、引导结束
System Servers 在内存中跑起来后，发送开机广播 “ACTION_BOOT_COMPLETED”。





