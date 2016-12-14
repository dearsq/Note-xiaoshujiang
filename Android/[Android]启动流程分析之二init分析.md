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
可以看到上面的传参有 –zygote, –start-system-server 

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

### AppRuntime 中的 start 方法
实际上调用的是其父类 AndroidRuntime 的方法 start()

### AndroidRuntime 类中的 start 方法
framework/base/core/jni/AndroidRuntime.cpp
```cpp
void AndroidRuntime::start(const char* className, const Vector<String8>& options, bool zygote)
```
在 start() 里面
1. 创建了 Java 虚拟机（startVm(&mJavaVM, &env, zygote)）
2. 注册了 JNI 的函数（startReg(env)）
3. 返回 ZygoteInit 的 main()

注意参数中
className 是 com.android.internal.os.ZygoteInit
options 有 start-system-server 这个选项
通过 
```cpp
    jstring optionsStr = env->NewStringUTF(options.itemAt(i).string());
    env->SetObjectArrayElement(strArray, i + 1, optionsStr);
    ...
```
```cpp
    env->CallStaticVoidMethod(startClass, startMeth, strArray);	
```
启动了 ZygoteInit 类中的 main() 与 startSystemServer()

### ZygoteInit 类中的 main 与 startSystemServer
frameworks/base/core/java/com/android/internal/os/ZygoteInit.cpp
```cpp
    public static void main(String argv[]) 
    {
    ...
        startSystemServer(abiList, socketName, zygoteServer);
    }
```
```cpp
    private static boolean startSystemServer(String abiList, String socketName, ZygoteServer zygoteServer)
    {
    ...
	Zygote.forkSystemServer(...,"com.android.server.SystemServer")
	//通过 fork 创建了 SystemServer 进程
	if (pid == 0) {
		........
		handleSystemServerProcess(parsedArgs);
		//SystemServer 进程调用 handleSystemServerProcess() 方法开始工作
		}
    }
```

至此，启动了 SystemServer 类中的 main

参考文章：Android6.0 SystemServer 类 http://blog.csdn.net/gaugamela/article/details/52261075

### SystemServer 类

framework/base/services/java/com/android/server/SystemServer.cpp
```cpp

```



## 参考文章

