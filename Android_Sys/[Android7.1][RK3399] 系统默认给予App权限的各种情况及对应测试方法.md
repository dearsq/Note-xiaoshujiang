title: [Android7.1][RK3399] 系统默认给予App权限的各种情况及对应测试方法
date: 2020-5-12 21:00:00
tags: Android

---

Platform: RK3399
OS: Android 7.1
Kernel: v4.4.126

[TOP]


## 需求描述
有这样几种场景：
App 是 系统 App 或者是 第三方需要内置的 App;
权限 是 危险权限 或者是 特殊权限。
所以排列组合有四种场景。这里分别讨论。

1. 系统 App（比如作为用来替代原生Launcher的系统应用）需要默认给予所有的权限。
包括危险权限（身体传感器,日历,摄像头,通讯录,地理位置,麦克风,电话,短信,存储空间）和特殊权限（悬浮窗、系统修改权限、访问使用记录权限）。
危险权限可以通过修改 DefaultPermissionGrantPolicy.java 实现;
系统权限可以通过系统签名实现。

2. 系统需要内置的第三方App（比如腾讯视频，蓦然认知，喜马拉雅这种）需要默认给它 危险权限和特殊权限。


## 给系统应用权限
### framework 中的修改 DefaultPermissionGrantPolicy.java 给系统应用危险权限
```
services/core/java/com/android/server/pm/DefaultPermissionGrantPolicy.java
@@ -607,6 +607,25 @@ final class DefaultPermissionGrantPolicy {
                 grantRuntimePermissionsLPw(musicPackage, STORAGE_PERMISSIONS, userId);
             }
 
+            // QXZN
+            PackageParser.Package YounixPackage = getPackageLPr("com.younix.packagename");
+            Log.d(TAG, "YounixPackage >> ");
+            if (YounixPackage != null) {
+                Log.d(TAG, "YounixPackage >> not null");
+                grantRuntimePermissionsLPw(YounixPackage, PHONE_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, CONTACTS_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, LOCATION_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, CALENDAR_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, SMS_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, MICROPHONE_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, CAMERA_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, SENSORS_PERMISSIONS, userId);
+                grantRuntimePermissionsLPw(YounixPackage, STORAGE_PERMISSIONS, userId);
+            }else{
+                Log.d(TAG, "YounixPackage >> null");
+            }
+
             // Watches
             if (mService.hasSystemFeature(PackageManager.FEATURE_WATCH, 0)) {
                 // Home application on watches

```
如上修改便给予了 `com.younix.packagename` 这个系统 App 所有的普通权限。

### 给系统应用特殊权限
特殊权限包括 悬浮窗、修改系统 设置等。
直接**签名**即可。
根据 google 的文档：https://developer.android.google.cn/reference/android/R.attr#protectionLevel
> 被 signature 标记标记的权限类型，当 app 被系统签名的时候，这种类型的权限会直接赋予给 app
> signature ：Base permission type: a permission that the system is to grant only if the requesting application is signed with the same certificate as the application that declared the permission. If the certificates match, the system automatically grants the permission without notifying the user or asking for the user's explicit approval.

### 验证方法
1. 通过开机后在 设置-应用 中查看对应 APK 的权限是否有给到。
2. 或者通过 dumpsys package 来看：
```
$ adb shell dumpsys package [Package_Name]
```


## 给第三方应用权限
### 给第三方内置应用危险权限
网上方法有很多，但是大部分都没写自己的系统环境，很是头疼。
我搜集并逐一尝试，有的有效有的无效，最终采用的方法五，赶时间的可以直接跳过去看。

方法一：framework 中修改 PackageManagerService.java
grantPermisisons 返回 true //测试有效 ，但是对于特殊权限无效
```
services/core/java/com/android/server/pm/PackageManagerService.java
@@ -1447,8 +1447,13 @@ public class PackageManagerService extends IPackageManager.Stub {
                         InstallArgs args = data.args;
                         PackageInstalledInfo parentRes = data.res;  
 
+          /*
                         final boolean grantPermisisons = (args.installFlags
                                 & PackageManager.INSTALL_GRANT_RUNTIME_PERMISSIONS) != 0;
+          */
+          final boolean grantPermissions = true;
+          //modified by Younix @2020.05.12,第三方应用默认给予权限
+
                         final boolean killApp = (args.installFlags
                                 & PackageManager.INSTALL_DONT_KILL_APP) == 0;
                         final String[] grantedPermissions = args.installGrantPermissions;
```

方法二：修改 DatabaseHelper.java。//未测试，待验证。
参考的 https://blog.csdn.net/wangjicong_215/article/details/71601494
记录如下。
frameworks/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
```
--- a/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
+++ b/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java
@@ -2351,6 +2351,65 @@ class DatabaseHelper extends SQLiteOpenHelper {
         if (mUserHandle == UserHandle.USER_SYSTEM) {
             loadGlobalSettings(db);
         }
+
+       //added by Younix @2020.05.18
+       loadAppOpsPermission(); 
+    }
+
+    private void loadAppOpsPermission(){
+       AppOpsManager appOpsManager = (AppOpsManager) mContext.getSystemService(Context.APP_OPS_SERVICE);
+       PackageManager pm = mContext.getPackageManager();
+
+       //String[] apkString = {"net.imoran.main.launcher"};
+
+       final String []itemString = mContext.getResources()
+                                       .getStringArray(com.android.internal.R.array.system_alert_window_permission_disable_custom_packagename);//net.imoran.main.launcher
+       for (int i = 0; i < itemString.length; i++) {
+               try {
+                       PackageInfo packageInfo = pm.getPackageInfo(itemString[i],
+                       PackageManager.GET_DISABLED_COMPONENTS |
+                       PackageManager.GET_UNINSTALLED_PACKAGES |
+                       PackageManager.GET_SIGNATURES);
+                       
+                       appOpsManager.setMode(AppOpsManager.OP_SYSTEM_ALERT_WINDOW,
+                                       packageInfo.applicationInfo.uid, itemString[i], AppOpsManager.MODE_ERRORED);
+               } catch (Exception e) {
+                        Log.e(TAG, "Exception when retrieving package:", e);
+               }
+       }
+
+       final String []itemStringExt = mContext.getResources()
+                     .getStringArray(com.android.internal.R.array.system_alert_window_permission_custom_packagename);
+        for (int i = 0; i < itemStringExt.length; i++) {
+            try {
+                 PackageInfo packageInfo = pm.getPackageInfo(itemStringExt[i],
+                     PackageManager.GET_DISABLED_COMPONENTS |
+                     PackageManager.GET_UNINSTALLED_PACKAGES |
+                     PackageManager.GET_SIGNATURES);
+
+                    appOpsManager.setMode(AppOpsManager.OP_SYSTEM_ALERT_WINDOW,
+                            packageInfo.applicationInfo.uid, itemStringExt[i], AppOpsManager.MODE_ALLOWED);                     
+            } catch (Exception e) {
+                Log.e(TAG, "Exception when retrieving package:", e);
+            }    
+        }
+
+       final String []itemStringExt1 = mContext.getResources()
+                                       .getStringArray(com.android.internal.R.array.write_settings_permission_custom_packagename);
+
+       for (int i = 0; i < itemStringExt1.length; i++) {
+           try {
+               PackageInfo packageInfo = pm.getPackageInfo(itemStringExt1[i],
+               PackageManager.GET_DISABLED_COMPONENTS |
+               PackageManager.GET_UNINSTALLED_PACKAGES |
+               PackageManager.GET_SIGNATURES);
+
+                appOpsManager.setMode(AppOpsManager.OP_WRITE_SETTINGS,
+                        packageInfo.applicationInfo.uid, itemStringExt1[i], AppOpsManager.MODE_ALLOWED);
+            } catch (Exception e) {
+               Log.e(TAG, "Exception when retrieving package:", e);
+           }    
+       }
     }

```
write_settings_permission_custom_packagename 需要去 xml 里面定义一下。

方法三：RK 的补丁。修改的工程较大。
核心思想是，增加了一个方法
```
method public abstract boolean deleteOtherPermissions(int, java.lang.String) throws android.content.pm.PackageManager.NameNotFoundException;
```
在这个方法里针对指定的 package，删掉所有权限，再增加指定权限（grantDefaultOtherAllPermissions）。
其实本质还是`grantRuntimePermissionsLPw`。

方法四：修改 framework 中各个权限的 protectionLevel。**不推荐。** 测试有效，但会引起很多Bug，比如点击 设置 里面的某些内容的时候会闪退。
参考：
https://developer.android.google.cn/guide/topics/manifest/permission-element
https://developer.android.google.cn/reference/android/R.attr#protectionLevel
因为保护级别包含基本权限类型以及零个或者多个标记。
“dangerous”保护级别没有标记。

我们以 PACKAGE_USAGE_STATS 为例。比如在`core/res/AndroidManifest.xml` 中看到如下信息：
```
2667     <!-- @SystemApi Allows an application to collect component usage
2668         ¦statistics
2669         ¦<p>Declaring the permission implies intention to use the API and the user of the
2670         ¦device can grant permission through the Settings application. -->
2671     <permission android:name="android.permission.PACKAGE_USAGE_STATS"
2672         android:protectionLevel="signature|privileged|development|appop" />
2673     <uses-permission android:name="android.permission.PACKAGE_USAGE_STATS" />
```
关注 protectionLevel：
> signature ：Base permission type: a permission that the system is to grant only if the requesting application is signed with the same certificate as the application that declared the permission. If the certificates match, the system automatically grants the permission without notifying the user or asking for the user's explicit approval.
> privileged：Additional flag from base permission type: this permission can also be granted to any applications installed as privileged apps on the system image. Please avoid using this option, as the signature protection level should be sufficient for most needs and works regardless of exactly where applications are installed. This permission flag is used for certain special situations where multiple vendors have applications built in to a system image which need to share specific features explicitly because they are being built together.
> development：Additional flag from base permission type: this permission can also (optionally) be granted to development applications.

所以将特殊权限修改为危险权限后，配合方法一使用即可。

方法五：使用 grantRuntimePermissionsLPw 授予特殊权限。
根据方法三中 RK 的补丁。grantRuntimePermissionsLPw 是可以给予特殊权限的。
所以进行如下操作
```
--- a/services/core/java/com/android/server/pm/DefaultPermissionGrantPolicy.java
+++ b/services/core/java/com/android/server/pm/DefaultPermissionGrantPolicy.java
@@ -87,6 +87,13 @@ final class DefaultPermissionGrantPolicy {
     private static final String ATTR_NAME = "name";
     private static final String ATTR_FIXED = "fixed";
 
+    private static final Set<String> YOUNIX_PERMISSIONS = new ArraySet<>();
+    static {
+        YOUNIX_PERMISSIONS.add(Manifest.permission.PACKAGE_USAGE_STATS);
+        YOUNIX_PERMISSIONS.add(Manifest.permission.SYSTEM_ALERT_WINDOW);
+        YOUNIX_PERMISSIONS.add(Manifest.permission.WRITE_SETTINGS);
+    }
+
     private static final Set<String> PHONE_PERMISSIONS = new ArraySet<>();
     static {
         PHONE_PERMISSIONS.add(Manifest.permission.READ_PHONE_STATE);
@@ -663,6 +670,7 @@ final class DefaultPermissionGrantPolicy {
                 grantRuntimePermissionsLPw(YounixPackage, CAMERA_PERMISSIONS, userId);
                 grantRuntimePermissionsLPw(YounixPackage, SENSORS_PERMISSIONS, userId);
                 grantRuntimePermissionsLPw(YounixPackage, STORAGE_PERMISSIONS, userId);
+       grantRuntimePermissionsLPw(YounixPackage, YOUNIX_PERMISSIONS, userId);
             }else{
                 Log.d(TAG, "YounixPackage >> null");
             }

```


### 第三方应用危险权限申请 PERMISSIONS_STORAGE
#### 原理
```
 674     <permission android:name="android.permission.READ_EXTERNAL_STORAGE"
 675         android:permissionGroup="android.permission-group.STORAGE"
 676         android:label="@string/permlab_sdcardRead"
 677         android:description="@string/permdesc_sdcardRead"
 678         android:protectionLevel="dangerous" />
```
关注 protectionLevel：dangerous
> Base permission type: a higher-risk permission that would give a requesting application access to private user data or control over the device that can negatively impact the user. Because this type of permission introduces potential risk, the system may not automatically grant it to the requesting application. For example, any dangerous permissions requested by an application may be displayed to the user and require confirmation before proceeding, or some other approach may be taken to avoid the user automatically allowing the use of such facilities.

#### 测试APKdemo
```
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```
```
    private static String[] PERMISSIONS_STORAGE = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE};
			
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        requestDangerousPermission();
        //requestOverlayPermission();
        //requestWriteSettings();
    }
	
	    private void requestDangerousPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, PERMISSIONS_STORAGE, REQUEST_PERMISSION_CODE);
            }
        }
    }
	
	    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_PERMISSION_CODE) {
            for (int i = 0; i < permissions.length; i++) {
                Log.i("MainActivity", "申请的权限为：" + permissions[i] + ",申请结果：" + grantResults[i]);
            }
        }

    }

```

### 第三方应用特殊权限（悬浮窗）申请 SYSTEM_ALERT_WINDOW
#### 原理
```
1726     <!-- Allows an app to create windows using the type
1727         ¦{@link android.view.WindowManager.LayoutParams#TYPE_SYSTEM_ALERT},
1728         ¦shown on top of all other apps.  Very few apps
1729         ¦should use this permission; these windows are intended for
1730         ¦system-level interaction with the user.
1731 
1732         ¦<p class="note"><strong>Note:</strong> If the app
1733         ¦targets API level 23 or higher, the app user must explicitly grant
1734         ¦this permission to the app through a permission management screen. The app requests
1735         ¦the user's approval by sending an intent with action
1736         ¦{@link android.provider.Settings#ACTION_MANAGE_OVERLAY_PERMISSION}.
1737         ¦The app can check whether it has this authorization by calling
1738         ¦{@link android.provider.Settings#canDrawOverlays
1739         ¦Settings.canDrawOverlays()}.
1740         ¦<p>Protection level: signature -->
1741     <permission android:name="android.permission.SYSTEM_ALERT_WINDOW"
1742         android:label="@string/permlab_systemAlertWindow"
1743         android:description="@string/permdesc_systemAlertWindow"
1744         android:protectionLevel="signature|preinstalled|appop|pre23|development" />
```
关注 protectionLevel：signature|preinstalled|appop|pre23|development
signature：签名后可以自动给于此权限
preinstalled：这个权限可以给系统中预安装的应用程序
appop：此权限与用于控制访问权限的应用操作紧密相关
pre23：如果是  Build.VERSION_CODES.M  以下的 SDK，可以自动授予
development：这个权限可以给予开发中的应用程序

#### 测试APKdemo
参考https://blog.csdn.net/zhangyong7112/article/details/55097257
```
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
```
```
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //myRequetPermission();
        requestOverlayPermission();
        //requestWriteSettings();
    }
	
	    private void requestOverlayPermission() {
        //Settings.canDrawOverlays(this) 检查是否有悬浮窗权限
        if(!Settings.canDrawOverlays(this)){
            //没有悬浮窗权限,跳转申请
            Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION);
            startActivity(intent);
        }
    }
```
可以看到，不会弹出悬浮窗了。权限被直接给予。

### 第三方应用特殊权限（修改系统设置）申请 WRITE_SETTINGS
#### 原理
略，各种标志前面都写了
#### 测试 APK demo
这个权限比较特殊，App 默认是会跳转到设置的系统界面中去，需要用户手动打开开关进行设置。
代码参考 https://www.jianshu.com/p/c3908cb3554d
```
    /**
     * 申请权限
     */
    private void requestWriteSettings()
    {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
        {
            //大于等于23 请求权限
            if ( !Settings.System.canWrite(getApplicationContext()))
            {//没有权限，进行申请
                Intent intent = new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS);
                intent.setData(Uri.parse("package:" + getPackageName()));
                startActivityForResult(intent, REQUEST_CODE_WRITE_SETTINGS );
            } else {//有了权限，具体的动作（比如调整系统亮度）
                        Settings.System.putInt(getContentResolver(),Settings.System.SCREEN_BRIGHTNESS, progress);
			}
        }else{
            //小于23直接设置
        }
    }
	
	    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_WRITE_SETTINGS)
        {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M)
            {
                  //Settings.System.canWrite方法检测授权结果
                if (Settings.System.canWrite(getApplicationContext()))
                {
                    T.show("获取了权限");
                }else{
                    T.show("您拒绝了权限");
                }
            }
        }

    }
```