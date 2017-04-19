
Platform: RK3399 
OS: Android 6.0 
Version: v2017.0３


## 解决方法（一）

在 ~/rk_Project_3399/device/rockchip/rk3399/rk3399_YOUR_DEVICE
下的　system.prop 中添加　
```
ro.lockscreen.disable.default=true
```
重新编译后，成功去掉锁屏，锁屏失效。

## 代码流程

该属性　调用到一下两个地方：
rk_Project_3399/frameworks/base/packages/SettingsProvider/src/com/android/providers/settings/DatabaseHelper.java

```
if (SystemProperties.getBoolean("ro.lockscreen.disable.default", false) == true) {
                loadSetting(stmt, Settings.System.LOCKSCREEN_DISABLED, "1");
            } else {
                loadBooleanSetting(stmt, Settings.System.LOCKSCREEN_DISABLED,
                        R.bool.def_lockscreen_disabled);
            }
```
rk_Project_3399/frameworks/base/services/core/java/com/android/server/LockSettingsService.java:
```
public void initialize(SQLiteDatabase db) {
    // Get the lockscreen default from a system property, if available
    boolean lockScreenDisable = SystemProperties.getBoolean(
            "ro.lockscreen.disable.default", false);
    if (lockScreenDisable) {
        mStorage.writeKeyValue(db, LockPatternUtils.DISABLE_LOCKSCREEN_KEY, "1", 0);
    }
}
```

## 解决方法（二）

frameworks/base/packages/SettingsProvider/res/values/defaults.xml
```
<bool name="def_lockscreen_disabled">false</bool> 
```
改为 true  即默认禁止锁屏

改完后
```
rm out/target/product/rk3399/system/framework/framework.jar
cd framework/base
mm
adb push framework.jar /system/framework
```
机器再恢复出厂设置。即可。
