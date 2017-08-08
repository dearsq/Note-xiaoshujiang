---
title: [Android6.0][RK3399] 关闭双击 Power 打开 Camera 功能
tags: 
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Version: v2017.03

RK 平台默认“很贴心”的实现了一个双击 Power 键可以打开 Camera 的功能。
但是我根本就不需要啊 混蛋～
有时候手抖按了两下 Power 键就进入 Camera 了还得退出来真的很影响用户体验。
所以那就去掉这个功能吧。

## 代码实现

```
diff --git a/packages/SettingsProvider/res/values/defaults.xml b/packages/SettingsProvider/res/values/defaults.xml
index e7949b8..607818d 100755
--- a/packages/SettingsProvider/res/values/defaults.xml
+++ b/packages/SettingsProvider/res/values/defaults.xml
@@ -211,6 +211,9 @@
     <!-- Default state of tap to wake -->
     <bool name="def_double_tap_to_wake">true</bool>
 
+    <!-- Default state of gesture to open camera -->
+    <bool name="def_camera_double_tap_power_gesture_disable">true</bool>
+
     <!-- Default for Settings.Secure.NFC_PAYMENT_COMPONENT -->
     <string name="def_nfc_payment_component"></string>
 
``` 
```
diff --git a/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java b/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
index 0b122a4..5f9a2ba 100755
--- a/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
+++ b/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
@@ -2493,6 +2493,9 @@ class DatabaseHelper extends SQLiteOpenHelper {
                         R.bool.def_lockscreen_disabled);
             }
 
+            loadBooleanSetting(stmt, Settings.Secure.CAMERA_DOUBLE_TAP_POWER_GESTURE_DISABLED,
+                    R.bool.def_camera_double_tap_power_gesture_disable); 
+
             loadBooleanSetting(stmt, Settings.Secure.SCREENSAVER_ENABLED,
                     com.android.internal.R.bool.config_dreamsEnabledByDefault);
             loadBooleanSetting(stmt, Settings.Secure.SCREENSAVER_ACTIVATE_ON_DOCK,
```
