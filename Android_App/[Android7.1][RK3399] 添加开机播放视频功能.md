---
title: [Android7.1][RK3399] 添加开机播放视频功能
tags: android
grammar_cjkRuby: true
---

Author: Kris_Fei
Platform: RK3399  
OS: Android 7.1  
Kernel: v4.4.83

rk3399上默认已经添加了开机播放视频的功能，只要按照如下改动就可成功播放。
```
kris@eco:~/rk3399/device/rockchip/rk3399$ g df
diff --git a/device.mk b/device.mk
index 2a730bc..6645072 100755
--- a/device.mk
+++ b/device.mk
@@ -282,3 +282,8 @@ PRODUCT_COPY_FILES += \
 #Kris,170814.
 PRODUCT_COPY_FILES += \
     device/rockchip/rk3399/kmsg.sh:system/bin/kmsg.sh
+
+#Kris,170904, copy boot video.
+PRODUCT_COPY_FILES += \
+    device/rockchip/rk3399/bootvideo.mp4:system/media/bootanimation.ts
+
diff --git a/rk3399_mid/system.prop b/rk3399_mid/system.prop
index a9d895e..b0e1807 100755
--- a/rk3399_mid/system.prop
+++ b/rk3399_mid/system.prop
@@ -45,3 +45,7 @@ ro.sf.lcd_density=280

 #Kris,180712,remove lockscreen.
 ro.lockscreen.disable.default=true
+
+#Kris,180724, enable boot video.
+persist.sys.bootvideo.enable=true
+persist.sys.bootvideo.showtime=10  //测试验证最大15秒，见后面分析
```

代码流程：
```
status_t BootAnimation::readyToRun() {
   //判断DATA_BOOTVIDEO_FILE或者SYSTEM_BOOTVIDEO_FILE是否存在。
   //static const char DATA_BOOTVIDEO_FILE[] = "/data/local/bootanimation.ts";
   //static const char SYSTEM_BOOTVIDEO_FILE[] = "/system/media/bootanimation.ts";
   if (access(SYSTEM_BOOTVIDEO_FILE, R_OK) == 0){
      mVideoFile = (char*)SYSTEM_BOOTVIDEO_FILE;
   } else if (access(DATA_BOOTVIDEO_FILE, R_OK) == 0){
      mVideoFile = (char*)DATA_BOOTVIDEO_FILE;
   }
   //persist.sys.bootvideo.enable需要设置成true
   property_get("persist.sys.bootvideo.enable",decrypt, "false");
   char value[PROPERTY_VALUE_MAX];
   property_get("persist.sys.bootvideo.showtime", value, "-1");
   if(mVideoFile != NULL && !strcmp(decrypt, "true") &&(atoi(value)!=0)) {
        mVideoAnimation = true;
   }else{
        ALOGD("bootvideo: No boot video animation,EXIT_VIDEO_NAME:%s,bootvideo.showtime:%s\n",decrypt,value);
   }
}
```

threadLoop():
```
bool BootAnimation::threadLoop()
{
    //mVideoAnimation为true就播放视频
    if (mVideoAnimation){
        r = video();
    }
}
```

video():
```
bool BootAnimation::video()
{
......
    //视频播放的时间
    property_get("persist.sys.bootvideo.showtime", value, "-1");
    int bootvideo_time = atoi(value);//s
    //最大不能超过两分钟
    if(bootvideo_time > 120)
          bootvideo_time = 120;
......
    while(true) {
        const nsecs_t realVideoTime = systemTime()-mStartbootanimaTime;
        //这里检查要不要退出
        //退出的条件是service.bootanim.exit被置1
        checkExit();
        property_set("sys.bootvideo.closed", "0");
        usleep(CHECK_DELAY);
        //播放完或者播放时间超过了就暂停
        if(!mp->isPlaying()||(((ns2ms(realVideoTime)/1000) > bootvideo_time) && (bootvideo_time > -1))){
          mp->pause();
        }
        if(exitPending()){
           ALOGD("bootvideo:-----------------stop bootanimationvedio");
           break;
          }
    }
    ......
}
```
小结：
实际验证下来，发现视屏的播放并不能按照预设的时间来执行。 
大概播放15秒之后MediaPlayer使用的RockFFPlayer会被reset。 
具体最大播放时间可以打印realVideoTime的值。
```
07-24 17:46:11.023   733   733 D PhoneStatusBar: disable: < expand* icons alerts system_info back* home* recent* clock search* quick_settings >
07-24 17:46:11.024   308  1212 D RockFFPlayer: reset()***********
07-24 17:46:11.024   308  1212 D RockFFPlayerBase: dumpStatus(): Started
```