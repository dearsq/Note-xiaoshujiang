---
title: [Android6.0][RK3399]去掉鼠标移动唤醒功能
tags: android,resume
grammar_cjkRuby: true
---

[TOC]


## 需求
去掉移动时唤醒系统功能


## 解决方法
```
a/frameworks/native/services/inputflinger/InputReader.cpp b/frameworks/native/services/inputflinger/InputReader.cpp
index 10d35eb..730b733 100644
--- a/frameworks/native/services/inputflinger/InputReader.cpp
+++ b/frameworks/native/services/inputflinger/InputReader.cpp
@@ -2579,7 +2579,7 @@ void CursorInputMapper::sync(nsecs_t when) {
     // TODO: Use the input device configuration to control this behavior more finely.
     uint32_t policyFlags = 0;
     if ((buttonsPressed || moved || scrolled) && getDevice()->isExternal()) {
-        policyFlags |= POLICY_FLAG_WAKE;
+        //policyFlags |= POLICY_FLAG_WAKE;
     } 
```