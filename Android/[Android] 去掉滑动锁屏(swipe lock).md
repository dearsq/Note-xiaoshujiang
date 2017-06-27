Platform: RK3399 
OS: Android 6.0 
Version: v2017.03

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
SystemProperties.getBoolean 的实现在 JNI 层，实际上是通过 property_get 获取 ro.lockscreen.disable.default 的值
获取后如果等于 true 就设置 stmt 数据库中 key 为 Settings.System.LOCKSCREEN_DISABLED 的字段为 1
如果没有获取到或者获取到为 false，则设置该字段为 R.bool.def_lockscreen_disabled，后者是在 default.xml 中定义的（所以我们也可以通过改 default.xml 的方式来完成属性的更改。见解决方法二。）

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
获取系统属性，如果获取到了就将数据库的 LockPatternUtils.DISABLE_LOCKSCREEN_KEY 字段设置为 1

完成后 
```
rm out/target/product/rk3399/system/build.prop
make -j4
./mkimage
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
rm out/target/product/rk3399/system/priv-app/SettingsProvider/SettingsProvider.apk
```
mm 后 push 并恢复出厂设置
或者 make -j4 再./mkimage
