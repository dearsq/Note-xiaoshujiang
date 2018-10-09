---
title: 组件_BroadcastReceiver
tags: android
grammar_cjkRuby: true
---


# 动态注册
## MainActivity.java
```java
    
    private IntentFilter intentFilter;
    private NetworkChangeReceiver networkChangeReceiver; // 内部类
    
    onCreate {
        intentFilter = new IntentFilter();
        // 添加 Action
        intentFilter.addAction("android.net.conn.CONNECTIVITY_CHANGE"); 

        networkChangeReceiver = new NetworkChangeReceiver(); // 内部类实例
        registerReceiver(networkChangeReceiver, intentFilter);
    }
    
    // 内部类
    class NetworkChangeReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {

            // 获得系统服务类
            ConnectivityManager connectivityManager = (ConnectivityManager)
                    getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo networkInfo = connectivityManager.getActiveNetworkInfo();

            // 具体的使用场景
            if (networkInfo != null && networkInfo.isAvailable()) {
                Toast.makeText(context, "network is available", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(context, "network is unavailable", Toast.LENGTH_SHORT).show();
            }

        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy");
        unregisterReceiver(networkChangeReceiver);
    }
}
    
```

## AndroidManifest.xml
添加权限
```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

# 静态注册
## 应用场景
接受开机广播
右击 包名 -> New -> Other -> BroadcastReceiver 
enabled = true 表示是否启用该 BoardcastReceiver
exported = ture 表示允许接受本程序以外的 Boardcast
## BootCompleteReceiver.java
```
public class BootCompleteReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        // TODO: This method is called when the BroadcastReceiver is receiving
        // an Intent broadcast.
//        throw new UnsupportedOperationException("Not yet implemented");
        Toast.makeText(context, "Boot Complete", Toast.LENGTH_SHORT).show();
    }
}
```

## AndroidManifest.xml
```
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>

    <application
        <receiver
            android:name=".BootCompleteReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>

```

# 自定义标准广播
## 应用场景
点击 Mainactivity 的 Button ,发送广播
然后 App 接收到并弹出 Toast

## Mainactivity.java
```
        // Example 3 MY_BROADCAST
        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent("com.iyounix.android.a010broadcasts.MY_BROADCAST");
                sendBroadcast(intent);
            }
        });
```

## MyBroadcastReceiver.java
public class MyBroadcastReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Toast.makeText(context, "received in Younix BoardcastReceiver",Toast.LENGTH_SHORT).show();
    }
}

## AndroidManifest.xml
```
        <receiver android:name=".MyBroadcastReceiver"
            android:enabled="true"
            android:exported="true">
            <intent-filter>
                <action android:name="com.iyounix.android.a010broadcasts.MY_BROADCAST"/>
            </intent-filter>
        </receiver>
```