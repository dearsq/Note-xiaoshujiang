---
title: [Android6.0][MTK6737] 修改默认输入法为 Sogou
tags: 
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

[TOC]

## 预置 APP
```
commit f99f8c8092e65cbadf138c9e6b55fb9f22160425
Author: dearsq <zhang.yang@aiiage.com>
Date:   Fri May 11 12:33:01 2018 +0800

    将 Sogou 作为内置输入法 APK
    
    Change-Id: If5ec1311a0cc36a3300effbe5a3ea50c157d7793

diff --git a/apps/Sogou/Android.mk b/apps/Sogou/Android.mk
new file mode 100644
index 0000000..7513cf4
--- /dev/null
+++ b/apps/Sogou/Android.mk
@@ -0,0 +1,28 @@
+LOCAL_PATH := $(call my-dir)
+
+include $(CLEAR_VARS)
+
+LOCAL_MODULE := Sogou
+
+LOCAL_MODULE_TAGS := optional
+
+LOCAL_SRC_FILES := $(LOCAL_MODULE).apk
+
+LOCAL_MODULE_CLASS := APPS
+
+LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
+
+LOCAL_PREBUILT_JNI_LIBS := \
+  @lib/armeabi-v7a/libmono.so \
+  @lib/armeabi-v7a/libyuvutil.so \
+  @lib/armeabi-v7a/libbutterfly.so \
+  @lib/armeabi-v7a/libluajava.so \
+  @lib/armeabi-v7a/libNinepatch.so \
+  @lib/armeabi-v7a/libweibosdkcore.so \
+  @lib/armeabi-v7a/libmain.so \
+  @lib/armeabi-v7a/libsogouupdcore.so \
+  @lib/armeabi-v7a/liblegalkey.so 
+
+LOCAL_CERTIFICATE := PRESIGNED
+include $(BUILD_PREBUILT)
+
diff --git a/apps/Sogou/Sogou.apk b/apps/Sogou/Sogou.apk
new file mode 100644
index 0000000..b72d600
Binary files /dev/null and b/apps/Sogou/Sogou.apk differ
```
参考 https://blog.csdn.net/long375577908/article/details/78270702

## 查看所有的输入法的包名
代码内进行如下修改
```
--- a/base/services/core/java/com/android/server/InputMethodManagerService.java
+++ b/base/services/core/java/com/android/server/InputMethodManagerService.java
@@ -3037,6 +3037,7 @@ public class InputMethodManagerService extends IInputMethodManager.Stub
             }
 
             if (DEBUG) Slog.d(TAG, "Checking " + compName);
+            Slog.d(TAG, "Checking packageName:" + si.packageName + "  name:" + si.name);
 
             try {
                 InputMethodInfo p = new InputMethodInfo(mContext, ri, additionalSubtypes);
```
开机阶段 
```
adb logcat | grep "Checking "
```
可以看到内置的所有输入法的名字

## 查看 Setting 中我们需要写入的值

在设置的 语言和输入法 界面点击切换输入法. 
会出现如下 Log
```
adb logcat | grep SettingsProvider

05-10 11:52:58.431   891   909 V SettingsProvider: packageValueForCallResult, name = default_input_method, value : com.cootek.smartinputv5/com.cootek.smartinput5.TouchPalIME
05-10 11:52:58.445   891   891 V SettingsProvider: packageValueForCallResult, name = enabled_input_methods, value : com.android.inputmethod.latin/.LatinIME:com.cootek.smartinputv5/com.cootek.smartinput5.TouchPalIME

```
所以我们知道了我们需要去操作的值是
`default_input_method` 和 `enabled_input_methods`

## 在代码中写入 Setting 的值
```
--- a/base/packages/SettingsProvider/res/values/defaults.xml
+++ b/base/packages/SettingsProvider/res/values/defaults.xml
@@ -22,6 +22,9 @@
     <integer name="def_sleep_timeout">-1</integer>
     <bool name="def_airplane_mode_on">false</bool>
     <bool name="def_theater_mode_on">false</bool>
+
+    <string name="enabled_input_methods" translatable="false">com.sohu.inputmethod.sogou/.SogouIME</string>
+    <string name="def_input_method" translatable="false">com.sohu.inputmethod.sogou/.SogouIME</string>
     <!-- Comma-separated list of bluetooth, wifi, and cell. -->
     <string name="def_airplane_mode_radios" translatable="false">cell,bluetooth,wifi,nfc,wimax</string>
     <string name="airplane_mode_toggleable_radios" translatable="false">bluetooth,wifi,nfc</string>
diff --git a/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java b/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
index be664ae..0bb063c 100644
--- a/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
+++ b/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
@@ -2463,6 +2463,13 @@ class DatabaseHelper extends SQLiteOpenHelper {
             loadSetting(stmt, Settings.Secure.LOCATION_PROVIDERS_ALLOWED,
                     mUtils.getStringValue(Settings.Secure.LOCATION_PROVIDERS_ALLOWED,
                     R.string.def_location_providers_allowed));
+           
+           // Added by Younix
+           loadStringSetting(stmt, Settings.Secure.ENABLED_INPUT_METHODS,
+                R.string.enabled_input_methods);
+           loadStringSetting(stmt, Settings.Secure.DEFAULT_INPUT_METHOD,
+                               R.string.def_input_method);
+           // End Added
 
             String wifiWatchList = SystemProperties.get("ro.com.android.wifi-watchlist");

```
这里不同版本的 Android 可能 loadStringSetting 的实现不一样.
可以自己看下 loadStringSetting 的实现然后传参.
 
 
 ## 补充:MTK平台FAQ汇总
 
如果按照如上的步骤没有修改成功，请参考如下步骤进行检查修改：
（1）检查是否成功预置输入法：FAQ13232 
（2）检查下setting-- language&input 界面，该输入法前面的勾是否选上，没有选上说明此输入法没有被enable，请参考FAQ08909来enable；
（3）检查是否发生语言切换，如果有切换则会恢复默认输入法，若不想因语言变化导致恢复，请参考FAQ12213，FAQ06663
（4）修改默认输入法FAQ04327



### 06663
【描述】切换系统语言后默认输入法会自动切换到latin输入法，或者系统预置的默认输入法不能生效【解法】
KK、L、M 的解决方案：
 可以在文件inputmethodmanagerservice.java中
在构造函数InputMethodManagerService中的最后面，将接收语言改变广播的事件注释掉：
```
final IntentFilter filter = new IntentFilter();        
filter.addAction(Intent.ACTION_LOCALE_CHANGED);        
mContext.registerReceiver(	new BroadcastReceiver() {
	@Override                    
	public void onReceive(Context context, Intent intent) {                        
			synchronized(mMethodMap) {                            
			//resetStateIfCurrentLocaleChangedLocked();//将此行注释掉                        
			}                    
	}                
}, filter);
```
这样就可以了。


### 12213
[DESCRIPTION]
一些版本设置默认输入法不成功，是因为KK比较晚的版本和之后的版本把默认输入法的代码搬到了InputMethodManagerService.java中。 
[SOLUTION]
首先查看InputMethodManagerService.java中的systemRunning函数中是否有下面红色的代码，如果有则把红色后面蓝色的语句注释掉即可。
如果没有红色代码可以参考FAQ06663。                  
```
if (!mImeSelectedOnBoot) {                    
		Slog.w(TAG, "Reset the default IME as \"Resource\" is ready here.");                    
		/// M: Loading preinstalled ime from feature option. @{                    
				String preInstalledImeName = IMEFeatureOption.DEFAULT_INPUT_METHOD;                    
				Slog.i(TAG, "IMEFeatureOption defaultIME : " + preInstalledImeName);                    
				if (preInstalledImeName != null) {                        
						InputMethodInfo preInstalledImi = null;                        
						for (InputMethodInfo imi : mMethodList) {                            
								Slog.i(TAG, "mMethodList service info : " + imi.getServiceName());                            
								if (preInstalledImeName.equals(imi.getServiceName())) {                                
										preInstalledImi = imi;                                
										break;                            
								}                        
						}                        
						if (preInstalledImi != null) {                            
								setInputMethodLocked(preInstalledImi.getId(), NOT_A_SUBTYPE_ID);                        
						} else {                            
								Slog.w(TAG, "Set preinstall ime as default fail.");                            
								resetDefaultImeLocked(mContext);                        
						}                    
				}                    
		/// @}                    
		resetStateIfCurrentLocaleChangedLocked();                    
		InputMethodUtils.setNonSelectedSystemImesDisabledUntilUsed(                            
		mContext.getPackageManager(),                            
		mSettings.getEnabledInputMethodListLocked());                
}
```