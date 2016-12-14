---
title: [Android]启动流程分析之二init分析
tags: Android
grammar_cjkRuby: true
---
### init 进程解析 init.rc 并启动 Zygote 进程
system/core/rootdir/init.rc
```rc
import /init.${ro.zygote}.rc
```
system/core/rootdir/init.zygote32.rc
```
service zygote /system/bin/app_process -Xzygote /system/bin --zygote --start-system-server
    class main
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    onrestart write /sys/power/state on
    onrestart restart media
    onrestart restart netd
    writepid /dev/cpuset/foreground/tasks
```
可以看到 zygote 实际上对应的是 **app_process** 进程

### 启动 app_process 进程（Zygote）
frameworks/base/cmds/app_process/app_main.cpp
可以看到上面的传参有 --zygote, --start-system-server 

**根据 zygote 参数：**
1. 将 app_process 更名为 zygote
2. 执行 AppRuntime 的 start() 方法（实际上为其父类 AndroidRuntime 的 start() 的方法）
3. 利用 start() 方法启动 ZygoteInit 类的 main()
```cpp
    if(zygote){
        runtime.start("com.android.internal.os.ZygoteInit", args, zygote);
    }else{...}
```
**根据 start-system-server 参数：**
```
if (startSystemServer) {
            args.add(String8("start-system-server"));
}
```
将此参数传入 args，并作为参数传入 ZygoteInit 类的 main()
那么start() 具体是如何启动 ZygoteInit 类的呢？我们研究一下它的 start() 方法

### AppRuntime 中的 start 方法
实际上调用的是其父类 AndroidRuntime 的方法 start()

### AndroidRuntime 类中的 start 方法
framework/base/core/jni/AndroidRuntime.cpp

在 start() 里面
1. 创建了 Java 虚拟机（startVm(&mJavaVM, &env, zygote)）
2. 注册了 JNI 的函数（startReg(env)）
3. 返回 ZygoteInit 的 main() （  env->CallStaticVoidMethod(startClass, startMeth, strArray);）

```cpp
void AndroidRuntime::start(const char* className, const Vector<String8>& options, bool zygote)
```
注意参数中
**className** 是 com.android.internal.os.ZygoteInit
**options** 中有 start-system-server 这个选项
设置 strArray：
```cpp
    jstring optionsStr = env->NewStringUTF(options.itemAt(i).string());
    env->SetObjectArrayElement(strArray, i + 1, optionsStr);
    ...
```
查找 startClass，获得 startMeth。
//找到类 ZygoteInit，获得 类中“main”方法的 ID startMeth
并执行 main。
```cpp
    jclass startClass = env->FindClass(slashClassName);
	jmethodID startMeth = env->GetStaticMethodID(startClass, "main","([Ljava/lang/String;)V");
    env->CallStaticVoidMethod(startClass, startMeth, strArray);	
```
启动了 ZygoteInit 类中的 main()
至此，进入了 Java 的世界。

### ZygoteInit 类中的 main 与 startSystemServer
frameworks/base/core/java/com/android/internal/os/ZygoteInit.java
```cpp
public static void main(String argv[]) {
    try {
        ...
        String socketName = "zygote";
        ...
        //注册server socket
        zygoteServer.registerZygoteSocket(socketName);
        ...
        //预加载 1. 常用系统资源 2. 图形相关的（OpenGL） 3. 必要的库（SharedLibraries）4...
		//Zygote 进程预先加载这些类和资源，在以后 fork 子进程的时候，仅需做复制就可以（根据 fork 的 copy-on-write 机制，有些类不做改变的话，甚至不用复制，子进程和父进程共享数据，可以达到省内存的目的）
        preload();
        ...
        if (startSystemServer) {
            //启动system server
             startSystemServer(abiList, socketName, zygoteServer);
        }
        //zygote进程进入无限循环，处理请求
        zygoteServer.runSelectLoop(abiList);
        zygoteServer.closeServerSocket();
    } catch (Zygote.MethodAndArgsCaller caller) {
        //通过反射调用新进程函数的地方
        //后续介绍新进程启动时，再介绍
        caller.run();
    } catch (RuntimeException ex) {
        closeServerSocket();
        throw ex;
    }
}
```
```cpp
    private static boolean startSystemServer(String abiList, String socketName) {
    //准备capabilities参数
    ........
    String args[] = {
        "--setuid=1000",
        "--setgid=1000",
        "--setgroups=.........",
        "--capabilities=" + capabilities + "," + capabilities,
        "--nice-name=system_server",
        "--runtime-args",
        "com.android.server.SystemServer",
    };
    ZygoteConnection.Arguments parsedArgs = null;

    int pid;

    try {
        //将上面准备的参数，按照 ZygoteConnection 的风格进行封装
        parsedArgs = new ZygoteConnection.Arguments(args);
        ...........

        //通过fork"分裂"出system server，具体的过程在介绍system server时再分析
        /* Request to fork the system server process */
        pid = Zygote.forkSystemServer(
            parsedArgs.uid, parsedArgs.gid,
            parsedArgs.gids,
            parsedArgs.debugFlags,
            null,
            parsedArgs.permittedCapabilities,
            parsedArgs.effectiveCapabilities);
    } catch (IllegalArgumentException ex) {
        throw new RuntimeException(ex);
    }

    if (pid == 0) {
        ............
        //pid = 0, 在进程 system server中
        //system server 进程处理自己的工作
        handleSystemServerProcess(parsedArgs);
    }

    return true;
}
```
至此，启动了 SystemServer 类中的 main

参考文章：Android6.0 SystemServer 类 http://blog.csdn.net/gaugamela/article/details/52261075

### SystemServer 类

framework/base/services/java/com/android/server/SystemServer.cpp
```cpp
```



## 参考文章

