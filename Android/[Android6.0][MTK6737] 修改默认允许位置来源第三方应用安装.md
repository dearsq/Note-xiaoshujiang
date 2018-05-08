---
title: [Android6.0][MTK6737] 修改默认允许位置来源第三方应用安装
tags: 
grammar_cjkRuby: true
---

Date:   Tue May 8 11:48:00 2018 +0800

    修改默认允许位置来源第三方应用安装
    
    Change-Id: Ic8526ec6483afcd60b9e6deed86d42acb2f014e3

diff --git a/base/packages/SettingsProvider/res/values/defaults.xml b/base/packages/SettingsProvider/res/values/defaults.xml
index 645561c..8644de1 100644
--- a/base/packages/SettingsProvider/res/values/defaults.xml
+++ b/base/packages/SettingsProvider/res/values/defaults.xml
@@ -37,7 +37,7 @@
 
     <bool name="def_bluetooth_on">false</bool>
     <bool name="def_wifi_display_on">false</bool>
-    <bool name="def_install_non_market_apps">false</bool>
+    <bool name="def_install_non_market_apps">true</bool>
     <bool name="def_package_verifier_enable">true</bool>
     <!-- Comma-separated list of location providers.
          Network location is off by default because it requires
