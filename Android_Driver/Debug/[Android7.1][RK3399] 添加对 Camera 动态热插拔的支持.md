---
title: [Android7.1][RK3399] 添加对 USB Camera 动态热插拔的支持.md
tags: android
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.83

[TOC]

## 思路

原生Google代码只在开机的时候加载一次Camera 的配置, 当开机之后再去插USB Camera, 虽然USB模块能枚举成功USB Camera,但是Camera HAL 和 Camera Service是无法得知此事件的．
因此解决思路就是在每次APP初始化获取Camera信息的时候重新加载初始化一次Camera.


## 解决方案
### Android6.0
CameraService.cpp:
```
int32_t CameraService::getNumberOfCameras(int type) {
    ATRACE_CALL();
    switch (type) {
        case CAMERA_TYPE_BACKWARD_COMPATIBLE:
          +  if(mNumberOfNormalCameras == 0) {
          +      ALOGE("no camera be found ! check again...");
          +      onFirstRef();
          +  }
            return mNumberOfNormalCameras;
        case CAMERA_TYPE_ALL:
            return mNumberOfCameras;
        default:
            ALOGW("%s: Unknown camera type %d, returning 0",
                    __FUNCTION__, type);
            return 0;
    }
}
```

### Android7.1
#### HAL 层 
`CameraHal/CameraHal_Module.cpp`
```
diff --git a/CameraHal/CameraHal_Module.cpp b/CameraHal/CameraHal_Module.cpp
index 01afa0d..07380f2 100755
--- a/CameraHal/CameraHal_Module.cpp
+++ b/CameraHal/CameraHal_Module.cpp
@@ -712,6 +712,7 @@ int camera_get_number_of_cameras(void)
     int cam_cnt=0,fd=-1,rk29_cam[CAMERAS_SUPPORT_MAX];
     struct v4l2_capability capability;
     rk_cam_info_t camInfoTmp[CAMERAS_SUPPORT_MAX];
+    char usbcameraPlug[PROPERTY_VALUE_MAX];
     char *ptr,**ptrr;
     char version[PROPERTY_VALUE_MAX];
     char property[PROPERTY_VALUE_MAX];
@@ -722,7 +723,10 @@ int camera_get_number_of_cameras(void)
    struct timeval t0, t1;
     ::gettimeofday(&t0, NULL);

-    if (gCamerasNumber > 0)
+    property_get("persist.sys.usbcamera.status", usbcameraPlug, "");
+    bool plugstate = (strcmp(usbcameraPlug, "add") == 0)
+        || (strcmp(usbcameraPlug, "remove") == 0);
+    if (gCamerasNumber > 0 && !plugstate)
```

#### native 部分
```
diff --git a/media/libmedia/MediaProfiles.cpp b/media/libmedia/MediaProfiles.cpp
index fe0126a..99a5d48 100755
--- a/media/libmedia/MediaProfiles.cpp
+++ b/media/libmedia/MediaProfiles.cpp
@@ -718,7 +718,7 @@ MediaProfiles::getInstance()
         }
         CHECK(sInstance != NULL);
         sInstance->checkAndAddRequiredProfilesIfNecessary();
-        sIsInitialized = true;
+//        sIsInitialized = true;
     }

     return sInstance;
diff --git a/services/camera/libcameraservice/CameraService.cpp b/services/camera/libcameraservice/CameraService.cpp
index 28018df..737ab8f 100755
--- a/services/camera/libcameraservice/CameraService.cpp
+++ b/services/camera/libcameraservice/CameraService.cpp
@@ -41,6 +41,7 @@
 #include <media/AudioSystem.h>
 #include <media/IMediaHTTPService.h>
 #include <media/mediaplayer.h>
+#include <media/MediaProfiles.h>
 #include <mediautils/BatteryNotifier.h>
 #include <utils/Errors.h>
 #include <utils/Log.h>
@@ -428,15 +428,30 @@ void CameraService::onTorchStatusChangedLocked(const String8& cameraId,

 Status CameraService::getNumberOfCameras(int32_t type, int32_t* numCameras) {
     ATRACE_CALL();
+    char value[PROPERTY_VALUE_MAX];
     switch (type) {
         case CAMERA_TYPE_BACKWARD_COMPATIBLE:
             if(0 == mNumberOfNormalCameras) {
                 ALOGE("No camera be found ! check again...");
                 onFirstRef();
             }
+            property_get("persist.sys.usbcamera.status", value, "");
+            if((strcmp(value, "add") == 0)||(strcmp(value, "remove") == 0)){
+                mNumberOfCameras = mModule->getNumberOfCameras();
+                mNumberOfNormalCameras = mNumberOfCameras;
+                ALOGI("CameraService::getNumberOfCameras() = %d",mNumberOfCameras);
+                onFirstRef();
+                MediaProfiles::getInstance();
+            }
             *numCameras = mNumberOfNormalCameras;
             break;
         case CAMERA_TYPE_ALL:
+            property_get("persist.sys.usbcamera.status", value, "");
+            if((strcmp(value, "add") == 0)||(strcmp(value, "remove") == 0)){
+                mNumberOfCameras = mModule->getNumberOfCameras();
+                mNumberOfNormalCameras = mNumberOfCameras;
+                ALOGI("CameraService::getNumberOfCameras() = %d",mNumberOfCameras);
+                onFirstRef();
+                MediaProfiles::getInstance();
+            }
             *numCameras = mNumberOfCameras;
             break;
         default:
```
#### framework部分
```
diff --git a/core/java/android/content/Intent.java b/core/java/android/content/Intent.java
index d08a471..a25335d 100644
--- a/core/java/android/content/Intent.java
+++ b/core/java/android/content/Intent.java
@@ -4227,6 +4227,18 @@ public class Intent implements Parcelable, Cloneable {
                 | Intent.FLAG_GRANT_WRITE_URI_PERMISSION)) != 0;
     }

+         /**
+          *for Action_USB_CAMRA,remove and add action
+          */
+         /**{@hide}*/
+         public static final int FLAG_USB_CAMERA_REMOVE = 0x00008001;
+         /**{@hide}*/
+         public static final int FLAG_USB_CAMERA_ADD = 0x00008002;
+         
+         //add this action intent for usb remove /add
+         /** {@hide} */
+         public static final String ACTION_USB_CAMERA = "android.intent.action.USB_CAMERA";
+
     /**
      * If set, the recipient of this Intent will be granted permission to
      * perform read operations on the URI in the Intent's data and any URIs
diff --git a/services/usb/java/com/android/server/usb/UsbDeviceManager.java b/services/usb/java/com/android/server/usb/UsbDeviceManager.java
index 8eb0feb..5b32399 100644
--- a/services/usb/java/com/android/server/usb/UsbDeviceManager.java
+++ b/services/usb/java/com/android/server/usb/UsbDeviceManager.java
@@ -103,6 +103,10 @@ public class UsbDeviceManager {
             "/sys/class/android_usb/android0/f_audio_source/pcm";
     private static final String MIDI_ALSA_PATH =
             "/sys/class/android_usb/android0/f_midi/alsa";
+    private static final String USB_CAMERA_MATCH =
+            "DEVPATH=/devices";

     private static final int MSG_UPDATE_STATE = 0;
     private static final int MSG_ENABLE_ADB = 1;
@@ -152,6 +156,9 @@ public class UsbDeviceManager {
     private UsbDebuggingManager mDebuggingManager;
     private final UsbAlsaManager mUsbAlsaManager;
     private Intent mBroadcastedIntent;
+    
+    private long mLastUsbEvent = 0;
+    private String mLastUsbAction = "";

     private boolean mCharging=false;
     private class AdbSettingsObserver extends ContentObserver {
@@ -172,7 +179,44 @@ public class UsbDeviceManager {
     private final UEventObserver mUEventObserver = new UEventObserver() {
         @Override
         public void onUEvent(UEventObserver.UEvent event) {
-            if (DEBUG) Slog.v(TAG, "USB UEVENT: " + event.toString());
+            if (true) Slog.v(TAG, "USB UEVENT: " + event.toString());
+
+           String subSystem = event.get("SUBSYSTEM");
+           String devPath = event.get("DEVPATH");
+           Slog.d(TAG, "subSystem:" + subSystem + ",devPath:" + devPath);
+           if (devPath != null && devPath.contains("/devices")) {
+               if ("video4linux".equals(subSystem)) {
+                   Slog.i(TAG, "USB UEVENT: " + event.toString());
+                   Intent intent = new Intent(Intent.ACTION_USB_CAMERA);
+                   String action = event.get("ACTION");
+                   try {
+                       if (mLastUsbAction != null && mLastUsbAction.equals(action) 
+                           && SystemClock.uptimeMillis() - mLastUsbEvent < 1200) {
+                           Slog.i(TAG, "USB UEVENT send double, ignore this!");
+                           return;
+                       }
+                   } catch (Exception e) {
+                       e.printStackTrace();
+                   }
+                   mLastUsbAction = action;
+                   mLastUsbEvent = SystemClock.uptimeMillis();
+                   if ("remove".equals(action)){
+                       Slog.d(TAG,"usb camera remove=====");
+                       intent.setFlags(Intent.FLAG_USB_CAMERA_REMOVE);
+                       SystemProperties.set("persist.sys.usbcamera.status","remove");
+                       SystemProperties.set("sys.usbcam.status.forvideo","removed");
+                   } else if ("add".equals(action)) {
+                       Slog.d(TAG,"usb camera add=====");
+                       intent.setFlags(Intent.FLAG_USB_CAMERA_ADD);
+                       SystemProperties.set("persist.sys.usbcamera.status","add");
+                       SystemProperties.set("sys.usbcam.status.forvideo","added");
+                   }
+
+                   int num = android.hardware.Camera.getNumberOfCameras();
+                   mContext.sendBroadcastAsUser(intent,UserHandle.ALL);
+                   SystemProperties.set("persist.sys.usbcamera.status","");
+                   Slog.d(TAG,"usb camera num"+num);
+               }
+           }

             String state = event.get("USB_STATE");
             String accessory = event.get("ACCESSORY");
@@ -379,6 +423,8 @@ public class UsbDeviceManager {
                 // Watch for USB configuration changes
                 mUEventObserver.startObserving(USB_STATE_MATCH);
                 mUEventObserver.startObserving(ACCESSORY_START_MATCH);
+
+                mUEventObserver.startObserving(USB_CAMERA_MATCH);
             } catch (Exception e) {
                 Slog.e(TAG, "Error initializing UsbHandler", e);
             }
```