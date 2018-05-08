---
title: [Android6.0][MTK6737] 系统旋转后导航栏丢失，并有黑边
tags: 
grammar_cjkRuby: true
---

Hardware:MT6737
DeviceOS:Android6.0
Kernel: Linux3.18
HostOS: Ubuntu16.04

[TOC]

这个是横屏后遇到的一个问题，当航Bar只看到黑条，在屏幕0/180度时点击无效，90/270度时点黑条的任何地方底部会有Glow的光晕效果和震动效果，但是键值全都是recentApp。

修改方法如下：
SystemUI 的 navigation_bar 布局文件中，横屏布局和竖屏布局调换，就可以正常显示了。

```
diff --git a/base/packages/SystemUI/res/layout/navigation_bar.xml b/base/packages/SystemUI/res/layout/navigation_bar.xml
index c92ba45..2e59921 100644
--- a/base/packages/SystemUI/res/layout/navigation_bar.xml
+++ b/base/packages/SystemUI/res/layout/navigation_bar.xml
@@ -26,7 +26,7 @@
     android:background="@drawable/system_bar_background"
     >
 
-    <FrameLayout android:id="@+id/rot0"
+    <FrameLayout android:id="@+id/rot90"
         android:layout_height="match_parent"
         android:layout_width="match_parent"
         >
@@ -176,10 +176,10 @@
             />
     </FrameLayout>
 
-    <FrameLayout android:id="@+id/rot90"
+    <!-- Debug for navigation_bar disappear after rotation 270 -->
+    <FrameLayout android:id="@+id/rot0"
         android:layout_height="match_parent"
         android:layout_width="match_parent"
-        android:visibility="gone"
         android:paddingTop="0dp"
         >

```

## 隐藏
如果想要隐藏，可以通过 qemu.hw.mainkeys=1 实现。