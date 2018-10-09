---
title: [Android7.1][RK3399] 添加对三路以上 Camera 同时预览的支持
tags: android
grammar_cjkRuby: true
---

## 思路
系统默认只支持两路Camera,只要将CameraHal中的数量限制改掉就可以了。 
另外，有些地方直接用0和1表示Camera通道，也要做相应修改。

## 代码
```
diff --git a/CameraHal/CameraHal_Module.cpp b/CameraHal/CameraHal_Module.cpp
index 01afa0d..07380f2 100755
--- a/CameraHal/CameraHal_Module.cpp
+++ b/CameraHal/CameraHal_Module.cpp

@@ -835,7 +839,7 @@ int camera_get_number_of_cameras(void)
             fd = open(cam_path, O_RDONLY);
             if (fd < 0) {
                 LOGE("Open %s failed! strr: %s",cam_path,strerror(errno));
-                break;
+                continue;
             } 
             LOGD("Open %s success!",cam_path);

@@ -849,13 +853,13 @@ int camera_get_number_of_cameras(void)
                LOGD("Video device(%s): video capture not supported.\n",cam_path);
             } else {
                rk_cam_total_info* pNewCamInfo = new rk_cam_total_info();
-                memset(camInfoTmp[cam_cnt&0x01].device_path,0x00, sizeof(camInfoTmp[cam_cnt&0x01].device_path));
-                strcat(camInfoTmp[cam_cnt&0x01].device_path,cam_path);
-                memset(camInfoTmp[cam_cnt&0x01].fival_list,0x00, sizeof(camInfoTmp[cam_cnt&0x01].fival_list));
-                memcpy(camInfoTmp[cam_cnt&0x01].driver,capability.driver, sizeof(camInfoTmp[cam_cnt&0x01].driver));
-                camInfoTmp[cam_cnt&0x01].version = capability.version;
+                memset(camInfoTmp[cam_cnt].device_path,0x00, sizeof(camInfoTmp[cam_cnt].device_path));
+                strcat(camInfoTmp[cam_cnt].device_path,cam_path);
+                memset(camInfoTmp[cam_cnt].fival_list,0x00, sizeof(camInfoTmp[cam_cnt].fival_list));
+                memcpy(camInfoTmp[cam_cnt].driver,capability.driver, sizeof(camInfoTmp[cam_cnt].driver));
+                camInfoTmp[cam_cnt].version = capability.version;
                 if (strstr((char*)&capability.card[0], "front") != NULL) {
-                    camInfoTmp[cam_cnt&0x01].facing_info.facing = CAMERA_FACING_FRONT;
+                    camInfoTmp[cam_cnt].facing_info.facing = CAMERA_FACING_FRONT;
 #ifdef LAPTOP
                 } else if (strstr((char*)&capability.card[0], "HP HD") != NULL
                     || strstr((char*)&capability.card[0], "HP IR")) {
@@ -866,14 +870,14 @@ int camera_get_number_of_cameras(void)
                     LOGD("Camera %d name: %s", (cam_cnt&0x01), gUsbCameraNames[cam_cnt&0x01].string());
 #endif
                 } else {
-                    camInfoTmp[cam_cnt&0x01].facing_info.facing = CAMERA_FACING_BACK;
+                    camInfoTmp[cam_cnt].facing_info.facing = CAMERA_FACING_BACK;
                 }  
                 ptr = strstr((char*)&capability.card[0],"-");
                 if (ptr != NULL) {
                     ptr++;
-                    camInfoTmp[cam_cnt&0x01].facing_info.orientation = atoi(ptr);
+                    camInfoTmp[cam_cnt].facing_info.orientation = atoi(ptr);
                 } else {
-                    camInfoTmp[cam_cnt&0x01].facing_info.orientation = 0;
+                    camInfoTmp[cam_cnt].facing_info.orientation = 0;
                 }

                 memset(version,0x00,sizeof(version));
@@ -1207,8 +1211,11 @@ int camera_get_number_of_cameras(void)
     }
     #endif

-    memcpy(&gCamInfos[0], &camInfoTmp[0], sizeof(rk_cam_info_t));
-    memcpy(&gCamInfos[1], &camInfoTmp[1], sizeof(rk_cam_info_t));
+    for (int i = 0; i < gCamerasNumber; i++) {
+        memcpy(&gCamInfos[i], &camInfoTmp[i], sizeof(rk_cam_info_t));
+    }

     property_get("ro.sf.hwrotation", property, "0");
	 
diff --git a/CameraHal/CameraHal_Module.h b/CameraHal/CameraHal_Module.h
index 45c81ec..69be491 100755
--- a/CameraHal/CameraHal_Module.h
+++ b/CameraHal/CameraHal_Module.h
@@ -11,11 +11,11 @@ using namespace android;
 #define CAMERA_DEFAULT_PREVIEW_FPS_MIN    8000        //8 fps
 #define CAMERA_DEFAULT_PREVIEW_FPS_MAX    15000
 #endif
-#define CAMERAS_SUPPORT_MAX             2
+#define CAMERAS_SUPPORT_MAX             10
 #if defined(TARGET_RK3399)
-    #define CAMERAS_SUPPORTED_SIMUL_MAX     2
+    #define CAMERAS_SUPPORTED_SIMUL_MAX     10
 #else
-    #define CAMERAS_SUPPORTED_SIMUL_MAX     1
+    #define CAMERAS_SUPPORTED_SIMUL_MAX     10
 #endif
 #define CAMERA_DEVICE_NAME              "/dev/video"
 #define CAMERA_MODULE_NAME              "RK29_ICS_CameraHal_Module"

```

## 注意
因为Android只定义了Front和Back两种Camera属性，所以不能使用默认的APK测试。

