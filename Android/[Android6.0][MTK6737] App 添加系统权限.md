---
title: [Android6.0][MTK6737] App 添加系统权限
tags: 
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

## Android 权限规则介绍
### 1. apk 的签名
这种签名不是基于权威证书的，不会决定某个应用允不允许安装，而是一种自签名证书。
重要的是，android系统有的权限是基于签名的。
比如：system等级的权限有专门对应的签名，签名不对，权限也就获取不到。
默认生成的APK文件是 debug 签名的。获取system权限时用到的签名见后面描述。

### 2. 基于UserID的进程级别的安全机制
进程有独立的地址空间，进程与进程间默认是不能互相访问的，Android通过为每一个apk分配唯一的linux userID来实现，名称为"app_"加一个数字，比如app_43不同的UserID，运行在不同的进程，所以apk之间默认便不能相互访问。

Android提供了如下的一种机制，可以使两个apk打破前面讲的这种壁垒。
在AndroidManifest.xml 中利用 sharedUserId 属性给不同的 package 分配相同的 userID，通过这样做，两个package可以被当做同一个程序，系统会分配给两个程序相同的UserID。
当然，基于安全考虑，两个apk需要相同的签名，否则没有验证也就没有意义了。

### 3. 默认apk生成的数据对外是不可见的
实现方法是：Android会为程序存储的数据分配该程序的 UserID。
借助于Linux严格的文件系统访问权限，便实现了apk之间不能相互访问似有数据的机制。
例：我的应用创建的一个文件，默认权限如下，可以看到只有UserID为app_21的程序才能读写该文件。
```
　　-rw------- app_21   app_21      87650 2000-01-01 09:48 test.txt
```
那么如何对外开放呢？

使用MODE_WORLD_READABLE and/or MODE_WORLD_WRITEABLE标记。
> When creating a new file with getSharedPreferences(String, int), openFileOutput(String, int), or openOrCreateDatabase(String, int, SQLiteDatabase.CursorFactory), you can use the MODE_WORLD_READABLE and/or MODE_WORLD_WRITEABLE flags to allow any other package to read/write the file. When setting these flags, the file is still owned by your application, but its global read and/or write permissions have been set appropriately so any other application can see it.
 

### 4. AndroidManifest.xml中的显式权限声明
Android默认应用是没有任何权限去操作其他应用或系统相关特性的，应用在进行某些操作时都需要显式地去申请相应的权限。在应用安装的时候，package installer会检测该应用请求的权限，根据该应用的签名或者提示用户来分配相应的权限。在程序运行期间是不检测权限的。如果安装时权限获取失败，那执行就会出错，不会提示用户权限不够。大多数情况下，权限不足导致的失败会引发一个 SecurityException，会在系统log（system log）中有相关记录。

### 5. 权限继承 / UserID继承
当我们遇到 apk 权限不足时，我们有时会考虑写一个linux程序，然后由apk调用它去完成某个它没有权限完成的事情，很遗憾，这种方法是行不通的。前面讲过，android权限是在进程层面的，也就是说一个apk应用启动的子进程的权限不可能超越其父进程的权限（即apk的权限），即使单独运行某个应用有权限做某事，但如果它是由一个apk调用的，那权限就会被限制。实际上，android是通过给子进程分配父进程的UserID实现这一机制的。
 

## 常见权限不足问题分析

首先要知道，普通apk程序是运行在非root、非system层级的，也就是说看要访问的文件的权限时，看的是最后三位。另外，通过system/app安装的apk的权限一般比直接安装或adb install安装的apk的权限要高一些。

言归正传，运行一个android应用程序过程中遇到权限不足，一般分为两种情况:
### 1. Log中可明显看到权限不足的提示。
此种情况一般是AndroidManifest.xml中缺少相应的权限设置，好好查找一番权限列表，应该就可解决，是最易处理的情况。有时权限都加上了，但还是报权限不足，是什么情况呢？Android系统有一些API及权限是需要apk具有一定的等级才能运行的。比如 SystemClock.setCurrentTimeMillis()修改系统时间，WRITE_SECURE_SETTINGS权限好像都是需要有system级的权限才行，也就是说UserID是system.

### 2. Log里没有报权限不足，而是一些其他Exception的提示,这也有可能是权限不足造成的。
比如：我们常会想读/写一个配置文件或其他一些不是自己创建的文件，常会报java.io.FileNotFoundException错误。系统认为比较重要的文件一般权限设置的也会比较严格，特别是一些很重要的(配置)文件或目录。如
```
　　　　-r--r----- bluetooth bluetooth      935 2010-07-09 20:21 dbus.conf
　　　　drwxrwx--x system   system            2010-07-07 02:05 data 
```
dbus.conf好像是蓝牙的配置文件，从权限上来看，根本就不可能改动，非bluetooth用户连读的权利都没有。`/data`目录下存的是所有程序的私有数据，默认情况下android是不允许普通apk访问/data目录下内容的，通过data目录的权限设置可知，其他用户没有读的权限。
所以adb普通权限下在data目录下敲ls命令，会得到opendir failed, Permission denied的错误，通过代码file.listfiles()也无法获得data目录下的内容。
上面两种情况，一般都需要提升apk的权限，目前我所知的apk能提升到的权限就是system。

## 应用获取 system 和 root 权限

### 1. 获取 system 权限

1) AndroidManifest.xml 中添加 `android:sharedUserId="android.uid.xxx> `
eg. 给apk添加system权限
```
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
... ... 
android:sharedUserId="android.uid.system">
```

2) 在对应的 Android.mk 中添加 `LOCAL_CERTIFICATE := platform`
这个动作的目的是为了使用 platform key(platform.pk8 和 platform.x509.pem) 进行签名
通过这种方式只能使 apk 的权限升级到 system 级别,  对于需要 root 权限才能访问的文件, apk 还是无法访问.

3) mm 命令编译

另外还有一种方式是独立给 apk 签名, 上面第一步不变 , 第二步是使用目标系统的 Platform 密钥文件重新给 apk 文件签名:

1) 首先找到密钥文件，在Android源码目录中的位置是"build/target/product/security"，下面的platform.pk8和platform.x509.pem两个文件

2) 然后用Android提供的Signapk工具来签名，signapk的源代码是在"build/tools/signapk"下，编译后在out/host/linux-x86/framework下，命令为
```
java -jar signapk.jar  platform.x509.pem platform.pk8 input.apk output.apk
```

### 获取 root 权限

在 apk 如果想要使用 root 权限可以在程序中通过运行 shell 脚本 / Linux 下的程序实现.

参考 https://blog.csdn.net/dearsq/article/details/78788022

## 去掉第三方应用的申请权限弹窗

比如我的 App 需要 Camera 和 Recorder 权限:
```
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

`frameworks/base/services/core/java/com/android/server/pm/DefaultPermissionGrantPolicy.java `
是用来控制 App 权限的.
在其中添加系统 APP 所带权限, 第一次开机后就会将该权限赋予 App.

```
            PackageParser.Package  AiiagePackage = getPackageLPr(
                    "com.android.Aiiage");
            if (AiiagePackage != null) {
			 	Log.d(TAG, "AiiagePackage >> not null");
                grantRuntimePermissionsLPw(AiiagePackage, CAMERA_PERMISSIONS, userId);
                grantRuntimePermissionsLPw(AiiagePackage, MICROPHONE_PERMISSIONS, userId);
            }else{
                Log.d(TAG, "AiiagePackage >> null");
            }
```