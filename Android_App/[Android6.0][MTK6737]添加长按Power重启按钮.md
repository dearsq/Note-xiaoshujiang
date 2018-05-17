---
title: [Android6.0][MTK6737]添加长按Power重启按钮
tags: 
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

[TOC]

### 添加字符串资源
#### 中文资源文件
core/res/res/values-zh-rCN/strings.xml
```
base/core/res/res/values-zh-rCN/strings.xml
@@ -201,6 +201,9 @@
     <string name="shutdown_confirm_question" msgid="2906544768881136183">"您要关机吗？"</string>
     <string name="reboot_safemode_title" msgid="7054509914500140361">"重新启动并进入安全模式"</string>
     <string name="reboot_safemode_confirm" msgid="55293944502784668">"您要重新启动并进入安全模式吗
？这样会停用您已安装的所有第三方应用。再次重新启动将恢复这些应用。"</string>
+    <string name="reboot_title">"重启"</string>
+    <string name="reboot_confirm" product="tablet">"您的平板电脑将会重启。"</string>
+    <string name="reboot_confirm" product="default">"您的手机将会重启。"</string>
     <string name="recent_tasks_title" msgid="3691764623638127888">"近期任务"</string>
     <string name="no_recent_tasks" msgid="8794906658732193473">"最近没有运行任何应用"</string>
     <string name="global_actions" product="tablet" msgid="408477140088053665">"平板电脑选项"</string>

```
#### 英文资源文件
base/core/res/res/values/strings.xml
```
diff --git a/base/core/res/res/values/strings.xml b/base/core/res/res/values/strings.xml
index 370db27..a88e35d 100644
--- a/base/core/res/res/values/strings.xml
+++ b/base/core/res/res/values/strings.xml
@@ -538,6 +538,14 @@
          This will disable all third party applications you have installed.
          They will be restored when you reboot again.</string>
 
+    <!-- Title of dialog to confirm rebooting. -->
+    <string name="reboot_title">Reboot</string>
+
+    <!-- Reboot Confirmation Dialog.  When the user chooses to reboot the device, there will
+         be a confirmation dialog.  This is the message. -->
+    <string name="reboot_confirm" product="tablet">Your tablet will reboot.</string>
+    <string name="reboot_confirm" product="default">Your phone will reboot.</string>
+
     <!-- Recent Tasks dialog: title
      TODO: this should move to SystemUI.apk, but the code for the old
             recent dialog is still in the framework
@@ -562,6 +570,10 @@
     <!-- label for item that turns off power in phone options dialog -->
     <string name="global_action_power_off">Power off</string>
 
+    <!-- label for item that reboots the phone in phone options dialog -->
+    <string name="global_action_reboot">Reboot</string>
+    <!-- modified by Younix -->
+
     <!-- label for item that generates a bug report in the phone options dialog -->
     <string name="global_action_bug_report">Bug report</string>

```


### 添加 config.xml
```
base/core/res/res/values/config.xml
@@ -2030,6 +2030,7 @@
          -->
     <string-array translatable="false" name="config_globalActionsList">
         <item>power</item>
+        <item>reboot</item>
         <item>bugreport</item>
         <item>users</item>
     </string-array>
```
### 添加 public.xml
base/core/res/res/values/public.xml
```
@@ -782,6 +782,7 @@
   <public type="drawable" name="ic_lock_idle_alarm" id="0x0108002e" />
   <public type="drawable" name="ic_lock_lock" id="0x0108002f" />
   <public type="drawable" name="ic_lock_power_off" id="0x01080030" />
+  <public type="drawable" name="ic_lock_power_reboot" id="0x0108009e" />
   <public type="drawable" name="ic_lock_silent_mode" id="0x01080031" />
   <public type="drawable" name="ic_lock_silent_mode_off" id="0x01080032" />
   <public type="drawable" name="ic_menu_add" id="0x01080033" />
```

### 添加 symbols.xml
base/core/res/res/values/symbols.xml
```
@@ -818,6 +818,8 @@
   <java-symbol type="string" name="reboot_to_update_reboot" />
   <java-symbol type="string" name="reboot_to_reset_title" />
   <java-symbol type="string" name="reboot_to_reset_message" />
+  <java-symbol type="string" name="reboot_confirm" />
+  <java-symbol type="string" name="reboot_title" />
   <java-symbol type="string" name="reboot_safemode_confirm" />
   <java-symbol type="string" name="reboot_safemode_title" />
   <java-symbol type="string" name="relationTypeAssistant" />
@@ -1482,6 +1484,7 @@
   <java-symbol type="drawable" name="ic_jog_dial_vibrate_on" />
   <java-symbol type="drawable" name="ic_lock_airplane_mode" />
   <java-symbol type="drawable" name="ic_lock_airplane_mode_off" />
+  <java-symbol type="drawable" name="ic_lock_power_reboot" />
   <java-symbol type="drawable" name="ic_menu_cc" />
   <java-symbol type="drawable" name="jog_tab_bar_left_unlock" />
   <java-symbol type="drawable" name="jog_tab_bar_right_sound_off" />
@@ -1550,6 +1553,7 @@
   <java-symbol type="string" name="bugreport_status" />
   <java-symbol type="string" name="faceunlock_multiple_failures" />
   <java-symbol type="string" name="global_action_power_off" />
+  <java-symbol type="string" name="global_action_reboot" />
   <java-symbol type="string" name="global_actions_airplane_mode_off_status" />
   <java-symbol type="string" name="global_actions_airplane_mode_on_status" />
   <java-symbol type="string" name="global_actions_toggle_airplane_mode" />

```
### 添加 drawable
#### 添加 icon
frameworks\base\core\res\res\drawable
添加四种分辨率的 reboot 图标

#### 添加 xml
 core/res/res/drawable/ic_lock_power_reboot.xml
```

<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright (c) 2014, The Linux Foundation. All rights reserved.

     Redistribution and use in source and binary forms, with or without
     modification, are permitted provided that the following conditions are
     met:
         * Redistributions of source code must retain the above copyright
           notice, this list of conditions and the following disclaimer.
         * Redistributions in binary form must reproduce the above
           copyright notice, this list of conditions and the following
           disclaimer in the documentation and/or other materials provided
           with the distribution.
         * Neither the name of The Linux Foundation nor the names of its
           contributors may be used to endorse or promote products derived
           from this software without specific prior written permission.

     THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
     WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
     ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
     BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
     CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
     SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
     BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
     WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
     OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
     IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-->

<bitmap xmlns:android="http://schemas.android.com/apk/res/android"
    android:src="@drawable/ic_lock_power_reboot_alpha"
    android:tint="?attr/colorControlNormal" />
```

### 添加代码逻辑
#### 1. GlobalActions.java
\frameworks\base\core\res\res\values\symbols.xml 
```
@@ -40,6 +40,7 @@ import android.net.ConnectivityManager;
 import android.os.Build;
 import android.os.Bundle;
 import android.os.Handler;
+import android.os.IPowerManager;
 import android.os.Message;
 import android.os.RemoteException;
 import android.os.ServiceManager;
@@ -93,6 +94,7 @@ class GlobalActions implements DialogInterface.OnDismissListener, DialogInterfac
     /* Valid settings for global actions keys.
      * see config.xml config_globalActionList */
     private static final String GLOBAL_ACTION_KEY_POWER = "power";
+    private static final String GLOBAL_ACTION_KEY_REBOOT = "reboot";
     private static final String GLOBAL_ACTION_KEY_AIRPLANE = "airplane";
     private static final String GLOBAL_ACTION_KEY_BUGREPORT = "bugreport";
     private static final String GLOBAL_ACTION_KEY_SILENT = "silent";
@@ -273,6 +275,9 @@ class GlobalActions implements DialogInterface.OnDismissListener, DialogInterfac
             }
             if (GLOBAL_ACTION_KEY_POWER.equals(actionKey)) {
                 mItems.add(new PowerAction());
+            } else if (GLOBAL_ACTION_KEY_REBOOT.equals(actionKey)) {
+                Log.d(TAG,"add reboot actions");
+                mItems.add(new RebootAction());
             } else if (GLOBAL_ACTION_KEY_AIRPLANE.equals(actionKey)) {
                 mItems.add(mAirplaneModeOn);
             } else if (GLOBAL_ACTION_KEY_BUGREPORT.equals(actionKey)) {
@@ -367,6 +372,37 @@ class GlobalActions implements DialogInterface.OnDismissListener, DialogInterfac
         }
     }

+        private final class RebootAction extends SinglePressAction {
+        private RebootAction() {
+            super(com.android.internal.R.drawable.ic_lock_power_reboot,
+                    R.string.global_action_reboot);
+        }
+
+        @Override
+        public boolean showDuringKeyguard() {
+            return true;
+        }
+
+        @Override
+        public boolean showBeforeProvisioning() {
+            return true;
+        }
+
+        @Override
+        public void onPress() {
+            try {
+                IPowerManager pm = IPowerManager.Stub.asInterface(ServiceManager
+                        .getService(Context.POWER_SERVICE));
+                pm.reboot(true, null, false);
+            } catch (RemoteException e) {
+                Log.e(TAG, "PowerManager service died!", e);
+                return;
+            }
+        }
+    }
+
+

```

#### 2. ShutdownThread.java
base/services/core/java/com/android/server/power/ShutdownThread.java
```
-217,13 +217,27 @@ public final class ShutdownThread extends Thread {
             }
         }
 
-        final int longPressBehavior = context.getResources().getInteger(
+        boolean showRebootOption = false;
+        String[] defaultActions = context.getResources().getStringArray(
+                com.android.internal.R.array.config_globalActionsList);
+        for (int i = 0; i < defaultActions.length; i++) {
+            if (defaultActions[i].equals("reboot")) {
+                showRebootOption = true;
+                break;
+            }
+        }
+
+       final int longPressBehavior = context.getResources().getInteger(
                         com.android.internal.R.integer.config_longPressOnPowerBehavior);
-        final int resourceId = mRebootSafeMode
+        //final int resourceId = mRebootSafeMode
+        int resourceId = mRebootSafeMode
                 ? com.android.internal.R.string.reboot_safemode_confirm
                 : (longPressBehavior == 2
                         ? com.android.internal.R.string.shutdown_confirm_question
                         : com.android.internal.R.string.shutdown_confirm);
+        if (showRebootOption && !mRebootSafeMode) {
+            resourceId = com.android.internal.R.string.reboot_confirm;
+        }
 
         Log.d(TAG, "Notifying thread to start shutdown longPressBehavior=" + longPressBehavior);
 
@@ -237,7 +251,9 @@ public final class ShutdownThread extends Thread {
             sConfirmDialog = new AlertDialog.Builder(context)
                 .setTitle(mRebootSafeMode
                         ? com.android.internal.R.string.reboot_safemode_title
-                        : com.android.internal.R.string.power_off)
+                        : showRebootOption
+                                ? com.android.internal.R.string.reboot_title
+                                : com.android.internal.R.string.power_off)
                 .setMessage(resourceId)
                 .setPositiveButton(com.android.internal.R.string.yes,
                         new DialogInterface.OnClickListener() {
```



