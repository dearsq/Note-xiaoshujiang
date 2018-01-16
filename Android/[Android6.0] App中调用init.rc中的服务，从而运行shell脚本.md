---
title: [Android6.0] App中调用init.rc中的服务，从而运行shell脚本
tags: Android,Shell,init.rc,rockchip
grammar_cjkRuby: true
---

OS: Android6.0
Hardware: RK3399


## 需求
希望在 Android App 中添加 SPDIF 测试功能。走 Android Audio Manager 太麻烦了。所以希望直接通过 shell 脚本，调用 tinyplay 命令来进行。 
 
 
## 实现
### init.rc
Init.rc 中添加 spdiftest 服务 
```  
service spdiftest /system/bin/spdif-test 
    class main 
    disabled 
    oneshot 
``` 
 
 
 
### device.mk
工程 Device.mk 文件（rk3399_mid.mk）中添加 
``` 
PRODUCT_COPY_FILES += \ 
   device/rockchip/rk3399/rk3399_mid/test/spdif-test:system/bin/spdif-test \ 
   device/rockchip/rk3399/rk3399_mid/test/test-music.wav:system/media/audio/test-music.wav 
``` 
 
Spdif-test 实际为测试脚本 
Test-music.wav 实际为测试音频 
 
 
 ### 测试脚本
测试脚本 spdif-test 如下 
``` 
#!/system/bin/sh 
  
#LOG_FILE=/data/spdif-test.log 
#check input 
#if [ $# -lt 1 ] ; then 
#echo "[spdif-test] not wav file to play!" >> $LOG_FILE 
#exit 1 
#fi  
# test music file : /system/media/audio/test-music.wav 
  
# wait $2 seconds 
#if [ $# -eq 2 ] ; then 
# echo "[spdif-test] sleep $2 seconds" >> $LOG_FILE 
# sleep $2 
#fi 
  
# play wav file 
# echo "[spdif-test] start play , wav file is $WAV_FILE" >> $LOG_FILE 
tinymix -D 0 "Stereo DAC MIXL DAC L1 Switch" 1 
tinymix -D 0 "Stereo DAC MIXR DAC R1 Switch" 1 
tinymix -D 0 "OUT MIXL DAC L1 Switch" 1 
tinymix -D 0 "OUT MIXR DAC R1 Switch" 1 
tinymix -D 0 "HPOVOL L Switch" 1 
tinymix -D 0 "HPOVOL R Switch" 1 
tinymix -D 0 "HPO MIX HPVOL Switch" 1 
tinymix -D 0 "HPO L Playback Switch" 1 
tinymix -D 0 "HPO R Playback Switch" 1 
  
tinyplay /system/media/audio/test-music.wav -D 1 -d 0 
``` 
 
### App 中利用 SystemProperties 调用

在 App 中通过 SystemProperties.set("ctl.start","spdiftest"); 
调用 spdiftest 服务（实际是 spdif-test 脚本) 


```
    private void setSpdifOn() throws IOException {
        SystemProperties.set("ctl.start","spdiftest");
        Log.v(TAG, "Call System Service 'spdiftest' in init.rc to test SPDIF.");
    }
```