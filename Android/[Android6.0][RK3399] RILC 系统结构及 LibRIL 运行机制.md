---
title: [Android6.0][RK3399] RILC 系统结构及 LibRIL 运行机制
tags: rockchip,ril,rild,android,telephony
grammar_cjkRuby: true
---

## RILC 代码结构
```
hardware/ril/
 |- CleanSpec.mk			// 编译文件
 |- include					// 关键头文件目录，包括 ril.h ril_cdma_sms.h
 |- libril					// LibRIL Runtime 运行环境的源文件目录
 |- mock-ril				
 |- reference-cdma-sms		// CDMA 短信相关代码
 |- reference-ril			// RIL Stub 实现源码文件目录
 |- rild					//守护进程源码文件目录
```

重点在于 libril、reference-ril 和 rild 三个目录中的 C/C++ 代码文件。
mmm 模块编译的结果分别为 libril.so、libreference-ril.so、rild
从编译 Log 中我们也可以看到
```
Instal:out/target/product/rk3399_mid/system/lib64/libril.so
Instal:out/target/product/rk3399_mid/system/lib64/libreference-rilso
Instal:out/target/product/rk3399_mid/system/bin/rild
```

## RILC 运行机制

RILC 运行在 UserLibraries 系统运行库中的 HAL 层，它使用 HAL Stub 运行结构。
最关键的为 Runtime 对外提供 Proxy 代理接口，Stub 向 Runtime 提供 Operations 操作函数，Runtime 向 Stub 提供 Callback 函数。

RILC 运行机制主要围绕 LibRIL 与 Reference-RIL 相互调用，从而完成 Solicited 和 UnSolicited 消息处理，运行结构如下。
包括两个过程：启动和运行。
启动过程即 1.2.3. 是由 rild 完成的。
运行过程的核心为 LibRIL 和 Reference-RIL 消息交互。

![](http://ww1.sinaimg.cn/large/ba061518gy1fh94b2pjf7j20ku0egjto.jpg)

LibRIL 和 Reference-RIL 交互过程，符合 HAL层中基于 Stub 方式的运行机制。
LibRIL 为 Runtime ，Reference-RIL 实现了 RIL 请求转换成 AT 命令，并执行 AT 命令逻辑。
LibRIL 提供了 Reference-RIL 的 Proxy 代理接口。RILJ 基于 Socket 网络连接完成 Solicited 和 UnSolicited 消息 和 LibRIL 进行交互。最终交给 Reference-RIL 进行处理。
Reference-RIL 和 Modem 之间通过串口通信，主要用于 AT 命令的执行。

### 1. RILC 启动过程

#### 1.1 RILC 加载入口

device/rockchip/rk3399/init.rc
```
565 service ril-daemon /system/bin/rild -l /system/lib/libreference-ril.so
566     class main
567     socket rild stream 660 root radio
568     socket rild-debug stream 666 radio system
569     user root
570     group radio cache inet misc audio log
```
Linux 在启动过程中，会加载此配置文件中配置的系统服务。
所以 Android 在开机过程中，Linux Kernel 会运行 rild 可执行文件加载和启动 LibRIL。

1. 从上面可以看出建立了两个 Socket 连接，端口号分别是 rild 和 rild-debug。
2. 基于安全考虑，启动 ril-daemon 系统 service 服务的用户为 radio，进入控制台可以查看其进程信息
```
root@rk3399_mid:/ # ps | grep rild                                             
root      226   1     8416   2480  hrtimer_na 7fac161344 S /system/bin/rild
```
#### 1.2 解析 RILC 加载方法
hardware/ril/rild/rild.c 
关键函数是 RIL_startEventLoop、RIL_Init、RIL_register 
```c
main(){
// 调用 ril.cpp 中的 RIL_startEventLoop，LibRIL 开始循环监听 Socket 事件
// 即 可开始接受 RILJ 发起的 Socket 连接请求和 RIL Solicited 消息请求
   RIL_startEventLoop();

// 通过 referece-ril.so 动态链接库，获取指向 RIL_Init 函数的指针 rilInit
    rilInit = (const RIL_RadioFunctions *(*)(const struct RIL_Env *, int, char **))
        dlsym(dlHandle, "RIL_Init");
// 异常处理
    if (rilInit == NULL) {
        RLOGE("RIL_Init not defined or exported in %s\n", rilLibPath);
        exit(EXIT_FAILURE);
    }
// 调用 reference-ril.so 动态链接库的 RIL_Init 函数，传递 s_rilEnv 给 reference-ril.so
// 首先，前面 dlsym 方法获取了指向 RIL_init 的指针
// 其次，调用 RIL_init 完成 RIL Stub 的初始化，即 reference-ril.so 动态链接库
// 其参数 s_rilEnv 即 Runtime,它的获取是在 rild.c 代码中的静态代码块中完成的
// 其返回值 funcs 即 Functions
    funcs = rilInit(&s_rilEnv, argc, rilArgv);
    RLOGD("RIL_Init rilInit completed");
// 调用 libril.so 的 RIL_register 函数，将 funcs 传递给 libril.so
// 即提供其 Functions 给 LibRIL 调用。
    RIL_register(funcs);
    RLOGD("RIL_Init RIL_register completed");
}
```
上面的 main 函数整体负责启动 RILC。
关键职责便是建立 LibRIL 和 Reference-RIL 的一种相互协调的能力。
LibRIL 中有指向 Reference-RIL 中 funcs 结构体的指针。
Reference-RIL 中有指向 LibRIL 中 s_rilEnv 结构体（Runtime） 的指针。
建立关系后，两者就可以开始 RIL 消息的交互。


### 2. RILC 运行过程
LibRIL 现在可以和 Reference-RIL 开始 RIL 消息的交互。
根据消息流向分为两种类型：
下行消息：LibRIL 接收到 RILJ 发起的 Solicited 消息后，LibRIL 适用 funcs 调用 Reference-RIL 的 onRequest、onStateRequest 等方法。
上行消息：Modem 中相关通信的状态发生变化或者执行完 Solicited 请求消息后，
Reference-RIL 可以通过 s_rilEnv 结构体指针调用 LibRIL 中的方法，完成上行消息的发送。

### 3. RILC Runtime LibRIL

#### 3.1 代码架构
hardware/ril/libril
├── Android.mk
├── ril_commands.h		// 定义了 LibRIL 接收到 RILJ发出的 Solicited 请求消息所对应的调用函数和返回调用函数
├── ril.cpp		// 建立 Runtime 框架
├── ril_event.cpp	// 实现基于 ril_event 双向链表操作函数 ，在 5 节中讲解
├── ril_event.h		// ril_event 事件的结构定义
├── ril_ex.h
├── RilSapSocket.cpp
├── RilSapSocket.h
├── RilSocket.cpp
├── RilSocket.h
├── rilSocketQueue.h
└── ril_unsol_commands.h  // 定义了 UnSolicited 消息返回调用的函数

LibRIL 以 ril.cpp 代码为核心，其他代码协助它完成 LibRIL Runtime 的启动和运行，LibRIL Runtime 的两个作用：
1. 与 RILJ 基于 Socket 交互
2. 与 Reference-RIL 基于函数调用的交互

#### 3.2 结构体 RIL_Env
hardware/ril/include/telephony/ril.h
hardware/ril/reference-ril/ril.h
这两个 ril.h 完全相同。
RIL_Env 在 ril.h 中的定义如下
```c
struct RIL_Env {
    /**
     * "t" is parameter passed in on previous call to RIL_Notification
     * routine.
     * If "e" != SUCCESS, then response can be null/is ignored
     * "response" is owned by caller, and should not be modified or
     * freed by callee
     * RIL_onRequestComplete will return as soon as possible
     */
    //动态库完成一个请求后，通过 OnRequestComplete 通知处理结果，其中第一个参数标明是哪个请求的处理结果
    void (*OnRequestComplete)(RIL_Token t, RIL_Errno e,
                           void *response, size_t responselen);

#if defined(ANDROID_MULTI_SIM)
    /**
     * "unsolResponse" is one of RIL_UNSOL_RESPONSE_*
     * "data" is pointer to data defined for that RIL_UNSOL_RESPONSE_*
     * "data" is owned by caller, and should not be modified or freed by callee
     */
    void (*OnUnsolicitedResponse)(int unsolResponse, const void *data, size_t datalen, RIL_SOCKET_ID socket_id);
#else
    /**
     * "unsolResponse" is one of RIL_UNSOL_RESPONSE_*
     * "data" is pointer to data defined for that RIL_UNSOL_RESPONSE_*
     * "data" is owned by caller, and should not be modified or freed by callee
     */
	// 动态库用于进行unsolicited Response通知的函数
    void (*OnUnsolicitedResponse)(int unsolResponse, const void *data, size_t datalen);
#endif
    /**
     * Call user-specifed "callback" function on on the same thread that
     * RIL_RequestFunc is called. If "relativeTime" is specified, then it specifies
     * a relative time value at which the callback is invoked. If relativeTime is
     * NULL or points to a 0-filled structure, the callback will be invoked as
     * soon as possible
     */
	 // 给Rild提交一个超时任务
    void (*RequestTimedCallback) (RIL_TimedCallback callback,
                                   void *param, const struct timeval *relativeTime);
};
```
定义了三个指向函数的指针。其功能在上面注释中有说明。

#### 3.3 结构体 RIL_RadioFunctions 
```
typedef struct {
    int version;        /* set to RIL_VERSION */ //版本号
    RIL_RequestFunc onRequest;	
    RIL_RadioStateRequest onStateRequest;
    RIL_Supports supports;
    RIL_Cancel onCancel;
    RIL_GetVersion getVersion;
} RIL_RadioFunctions;
```
当 LibRIL 接收到 RILJ 发起的 Solicited 请求消息后，其他 5 个指向函数的指针会调用 Reference-RIL 提供的 funcs 中对应请求函数。

### 4. LibRIL Runtime 加载
LibRIL Runtime 的加载体现在 RIL_startEventLoop 和 RIL_register 两个函数。

#### 4.1 RIL_startEventLoop
RILC 启动过程中，先调用 LibRIL 中的 RIL_startEventLoop 函数完成 LibRIL 运行环境的准备，然后开始循环监听 Socket 相关 RIL 事件。
```c
extern "C" void			// 标识后此方法可以让 rild.c 调用
RIL_startEventLoop(void) {
    /* spin up eventLoop thread and wait for it to get started */
    s_started = 0;		// 启动标志
    pthread_mutex_lock(&s_startupMutex);	// 增加 pthread 的同步锁

    pthread_attr_t attr;
    pthread_attr_init(&attr);		// 初始化 pthread 参数
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);	

    // 创建基于 eventLoop 函数调用的子线程
    int result = pthread_create(&s_tid_dispatch, &attr, eventLoop, NULL);
    if (result != 0) {
        RLOGE("Failed to create dispatch thread: %s", strerror(result));
        goto done;
    }

    while (s_started == 0) { // pthread 启动标志，会在 eventLoop 方法中设置为 1
	    // 等待 s_startupCond 通知
        pthread_cond_wait(&s_startupCond, &s_startupMutex);
    }

done:
    pthread_mutex_unlock(&s_startupMutex); //释放锁
}
```

**eventLoop 函数**

进入 ril.cpp 代码中的 eventLoop 函数，其处理逻辑如下：
```c
static void *
eventLoop(void *param) {
    int ret;
    int filedes[2];

    ril_event_init(); // 初始化 ril_event 双向链表

    pthread_mutex_lock(&s_startupMutex); // 增加 pthread 同步锁

    s_started = 1; // 修改启动状态为 1
    pthread_cond_broadcast(&s_startupCond);

    pthread_mutex_unlock(&s_startupMutex); // 释放 thread 同步锁

    ret = pipe(filedes); //  创建管道通信

    if (ret < 0) { // 管道创建异常处理
        RLOGE("Error in pipe() errno:%d", errno);
        return NULL; // 直接返回 NULL
    }

    s_fdWakeupRead = filedes[0];  // 输入文件描述符
    s_fdWakeupWrite = filedes[1];  // 输出文件描述符

    fcntl(s_fdWakeupRead, F_SETFL, O_NONBLOCK);
    // 设置新创建 RIL 事件的 ril_event 参数，关注 s_fdWakeupRead 文件描述符 以及 RIL 事件回调方法 processWakeupCallback
    ril_event_set (&s_wakeupfd_event, s_fdWakeupRead, true,
                processWakeupCallback, NULL);
	// 增加 ril_event 节点，并激活
    rilEventAddWakeup (&s_wakeupfd_event);

    // Only returns on error 只在异常情况下才返回
	// 调用 ril_event.cpp 中 ril_event_init 函数，开始循环监听和处理 ril_event 时间
    ril_event_loop();
    RLOGE ("error in event_loop_base errno:%d", errno);
    // kill self to restart on error 异常时自杀重启
    kill(0, SIGKILL); 

    return NULL;
}
```

**s_wakeupfd_event 的事件处理**
s_wakeupfd_event 事件处理主要分为三大块，如下：
1. 创建管道获取其输入输出文件描述符 s_fdWakeupRead、s_fdWakeupWrite
2. 使用 s_fdWakeupRead 和 processWakeupCallback 创建 s_wakeupfd_event 事件
3. 增加并激活 s_wakeupfd_event 事件

ril_event 双向链表中此时仅有一个节点，那就是 s_wakeupfd_event。此节点的 fd 文件描述符为 s_fdWakeupRead，RIL 事件回调函数为 processWakeupCallback。

**ril_event_loop 函数**
ril_event.cpp 
在 ril_event_loop 函数中，核心是 for(;;) 循环，只要循环中处理逻辑不变化，ril_event_loop 函数调用是不会返回的。

#### 4.2 RIL_register 函数引入三方 RIL_RadioFunctions
**RIL_register 函数**
其作用在于引入第三方 Reference-RIL（以封装后 so 动态链接库提供 libreference-ril.so）。
关键代码在于对第三方 Reference-RIL 提供的 callbacks 参数（funcs）作 判空、版本号 等验证，验证过后，拷贝保存此指向 RIL_RadioFunctions 结构体指针。
这样 LibRIL 中就可以调用第三方 Reference-RIL 提供的 RIL 请求相关函数。

### 5. ril_event 事件处理机制
RIL 事件相关的数据均封装在 ril_event 结构体中，一个 RIL 事件会对应一个 ril_event 结构体。
LibRIL 在启动完成后进入运行状态，将围绕 ril_event 结构体处理 RIL 相关事件。

hardware/ril/libril/ril_event.h
```
// 定义指向 RIL 事件 Callback 回调函数的指针 ril_event_cb
typedef void (*ril_event_cb)(int fd, short events, void *userdata);

struct ril_event {
    struct ril_event *next;
    struct ril_event *prev;

    int fd;
    int index;	// 当前 RIL 事件的索引
    bool persist; // 保留当前 RIL 事件标志
    struct timeval timeout; // RIL 事件超时设置
    ril_event_cb func; // RIL 事件回调函数指针
    void *param;
};
```
