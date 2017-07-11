---
title: [Android5.1] 添加自定义开机动画（视频）并去黑屏
tags: Android,Rockchip,开机动画,黑屏
grammar_cjkRuby: true
---
[TOC]

平台 ：RK3288
OS：Android5.1
参考文章：[Android系统的开机画面显示过程分析（罗升阳）](http://blog.csdn.net/luoshengyang/article/details/7691321)
## 补丁如下

## 源码分析及修改方式
关于开机动画的流程主要代码在 
framebuffer/base/cmds/bootanimation/bootAnimation.cpp 
从 BootAnimation::threadLoop() 中的我们可以看到
```c
if(mZip == NULL) {    
        r = android();
    } else {
        r = movie();
}
```
根据 mZip（这是一个叫做 bootanimation.zip 的文件）是否存在，决定调用 android() 接口还是 movie() 接口。
### android() 
如果没有 zip 文件进入的就是这种方式。
会加载"images/android-logo-mask.png"和"images/android-logo-shine.png" 这两张图片，前者是镂空的 ANDROID 字样，后者是一副很长的银白黑渐进的背景图，通过固定前者，移动后者，实现 ANDROID 字样的反光效果。
想修改android闪动的那两张图片的话，最简单的方法是直接替换图片（图片在 /frameworks/base/core/res/assets/images），如果懂 openGL 的话也可以自己做酷炫的动画。

### movie()
如果有 bootanimation.zip 文件进入的就是这种方式。
```c
 #define SYSTEM_BOOTANIMATION_FILE "/system/media/bootanimation.zip"
 ```
会加载 bootanimation.zip 中的内容。zip 文件中实际是很多帧图片的组合，通过多帧图片的逐步播放实现动画的效果。
所以把做好的动画拷贝到编译好对应的目录下即可，然后执行**make snod**整合进 img 包就可以看到效果了。
具体制作 bootanimation.zip 的文章参考这两篇：
http://blog.csdn.net/mlbcday/article/details/7410509
http://luq1985428.blog.163.com/blog/static/12243116220131198011812/
**但这样默认是没有音乐的**，还需要实现一个 playMusic() 的接口，来同步的播放音乐。
具体实现 playMusic() 接口的方式参考这一篇的 "1.播放音乐"：
http://www.voidcn.com/blog/longtian635241/article/p-2095371.html
从 mp4 中提取音频为 ogg 或者 wav 格式的网站有
http://media.io/
**缺点**是
1. 多帧图片由于画面色彩丰富、动画较长，这样做出来的 zip 会比较大，播放效果会出现明显、严重卡顿
2. 播放时music时可能出现动画和声音不同步

所以我们可以调用 mediaPlayer 的接口来实现播放视频（mp4）
### 自行添加 video 接口
修改 ThreadLoop 中的判断
```c
 // We have no bootanimation file, so we use the stock android logo
     // animation.
-    if (mZip == NULL) {
  +    if (mVideo) {//这里的 mVideo 是一个标志位，表示是否有开机视频
+        r = video();
+    }else if (mZip == NULL) {
         r = android();
     } else {
         r = movie();
```
我们在 ReadyToRun 中实现 mVideo 的判断。
```c
@@ -359,6 +362,7 @@ status_t BootAnimation::readyToRun() {
     mFlingerSurfaceControl = control;
     mFlingerSurface = s;
 
+	mVideo = false;
     // If the device has encryption turned on or is in process
     // of being encrypted we show the encrypted boot animation.
     char decrypt[PROPERTY_VALUE_MAX];
@@ -366,6 +370,9 @@ status_t BootAnimation::readyToRun() {
 
     bool encryptedAnimation = atoi(decrypt) != 0 || !strcmp("trigger_restart_min_framework", decrypt);
 
+   if (access(BOOTANIMATION_VIDEO, R_OK) == 0) 
+      mVideo = true;
+
     ZipFileRO* zipFile = NULL;
     if ((encryptedAnimation 
             && (access(SYSTEM_ENCRYPTED_BOOTANIMATION_FILE, R_OK) == 0) 
```
下面可以开始添加 video 接口了
```c
+bool BootAnimation::video()
+{
+    const float MAX_FPS = 60.0f;
+    const bool LOOP = true;
+    const float CHECK_DELAY = ns2us(s2ns(1) / MAX_FPS);
+    sp<IMediaHTTPService> httpService;
+    eglMakeCurrent(mDisplay, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
+    eglDestroySurface(mDisplay, mSurface);
+    /*
+    float asp = 1.0f * mWidth / mHeight;
+    SurfaceComposerClient::openGlobalTransaction();
+    mFlingerSurfaceControl->setPosition(mWidth, 0);
+    mFlingerSurfaceControl->setMatrix(0, 1 / asp, -asp, 0);
+    SurfaceComposerClient::closeGlobalTransaction();
+     */
+
+    sp<MediaPlayer> mp = new MediaPlayer();
+    mp->setDataSource(httpService, BOOTANIMATION_VIDEO, NULL);//设置播放资源
+    mp->setLooping(true);//确定是否播放循环
+    mp->setVideoSurfaceTexture(mFlingerSurface->getIGraphicBufferProducer());
+    mp->prepare();
+    mp->start();
+    while(true) {
+        if(exitPending())
+            break;
+        usleep(CHECK_DELAY);
+        checkExit();
+    }
+    mp->stop();
+    return false;
+}
```
如果要实现开关机动画不同也可以增加一个判断。
这里的  BOOTANIMATION_VIDEO 为 mp4 的路径，setDataSource 接口有多种重载方式，这里采用 url 的方式。
```c
+#define  BOOTANIMATION_VIDEO                 "/system/media/bootanimation.mp4"
+#include <media/IMediaHTTPService.h>
```
最后修改头文件，添加增加的两个成员变量
/cmds/bootanimation/BootAnimation.h
```c
@@ -106,6 +106,8 @@ private:
     EGLDisplay  mSurface;
     sp<SurfaceControl> mFlingerSurfaceControl;
     sp<Surface> mFlingerSurface;
+    bool        mVideo;
+    bool        video();
     ZipFileRO   *mZip;
     int         mHardwareRotation;
     GLfloat     mTexCoords[8];
```
至此已经完成 video() 接口的编写了。
（具体 MediaPlayer 的用法参考的 http://blog.csdn.net/ddna/article/details/5176233 ）
后面可以在 /system/media/ 中添加 bootanimation.mp4 尝试能否播放 mp4。

## 开机视频前黑屏 5s
是由于等待电池的后台服务启动导致的，屏蔽如下代码。
 frameworks/av/media/libmediaplayerservice/MediaPlayerService.cpp
 ![](https://ws3.sinaimg.cn/large/ba061518gw1f7kstpdro9j20mx0btjuz.jpg)
屏蔽后黑屏时间减为 1s 左右。

