---
title: [Android7.1] 打开设置中的返回键
tags: android
grammar_cjkRuby: true
---

OS: Android7.1

## 应用场景
Setting App 在没有物理按键和虚拟返回键的时候无法返回.
不过 app 中是自带这个功能的, 不过默认是关闭的.

## 解决方案
```
--- a/src/com/android/settings/SettingsActivity.java
+++ b/src/com/android/settings/SettingsActivity.java
@@ -629,7 +629,8 @@ public class SettingsActivity extends SettingsDrawerActivity
                         mInitialTitleResId, mInitialTitle, false);
             } else {
                 // No UP affordance if we are displaying the main Dashboard
-                mDisplayHomeAsUpEnabled = false;
+                mDisplayHomeAsUpEnabled = true;
                 // Show Search affordance
                 mDisplaySearch = true;
                 mInitialTitleResId = R.string.dashboard_title;
```