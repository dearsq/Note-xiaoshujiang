---
title: Cardboard Treasure Hunter 代码分析
tags: VR,Cardboard
grammar_cjkRuby: true
---

### Manifest file
```xml
<manifest ...
    <uses-permission android:name="android.permission.NFC" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

    <uses-permission android:name="android.permission.VIBRATE" />
    ...
    <uses-sdk android:minSdkVersion="19" android:targetSdkVersion="23"/>
    <uses-feature android:glEsVersion="0x00020000" android:required="true" />
    <application
            ...
        <activity
                android:name=".MainActivity"
                android:screenOrientation="landscape">
                ...

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                <category android:name="com.google.intent.category.CARDBOARD" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### Extend GvrActivity
GvrActivity 是最基本的 activity，它提供了 Google VR 设备的简单集成。它暴露时间来和 VR 进行交互，并且处理创建 VR 渲染的一些细节。
