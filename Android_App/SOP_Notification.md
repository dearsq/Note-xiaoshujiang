---
title: SOP_Notification
tags: android
grammar_cjkRuby: true
---


1. 在 Activity 中创建
2. 在 BoardCast 中创建
3. 在 Service 中创建

## 使用
1. 管理 Notification
```
NotificationManager manager = (NotificationManager) Context.getSystemService(Context.NOTIFICATION_SERVICE);
```
2. 构造 Notification 对象
通过 `NotificationCompat.Builder`构造
```
Notification notification = new NotificationCompat.Builder(context).build();
```
或者
```
Notification notification = new NotificationCompat.Builder(context)
	.setContentTitle("This is content title")
    .setContentText("This is content Text")
    .setWhen(System.currentTimeMillis()) 		//被通知的时间
    .setLargeIcon(BitmapFactory.decodeResource(getResources(), R.drawable.large_icon)
	.build();
``` 
3. 显示通知
调用 NotificationManager 的 notifiy() 方法.
参数1 id
参数2 Notification 对象
```
manager.notify(1,notificaton)
```

## 更多通知技巧1
setSound() 设置通知音频
setVibrate() 设置振动
setLights() 设置光效
setDefaults(NotificationCompat.DEFAULT_ALL) 根据当前手机的默认参数设置一切

## setSound()
```
.setSound(Uri.fromFile(new File("/system/media/audio/ringtones/Luna.ogg")))
```

## setVibrate()
```
[0] 手机静止的时长
[1] 手机振动的时长
[2] 手机静止的时长
[3] 手机振动的时长
```
比如: 
振 1s -- 静 1s -- 振 1s 代码为:
```
.setVibrate(new long[] {0, 1000, 1000, 1000})
```
并且 AndroidManifest.xml 里面:
```
	<uses-permission android:name="android.permission.VIBRATE"/>
```

## setLights
```
.setLights(Color.GREEN,1000,1000)
```


## 更多通知技巧2
setStyle() 构建富文本通知内容
setPriority() 设置通知的重要程度

## setStyle
参数1. NotificationCompat.Style

默认通知显示内容有限 , 比如 text , 如果过长 只能显示局部.
解决方法如下
```
.setStyle(new NotificationCompat.BigTextStyle().bigText("This is a longlonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglonglong Text"))
```

## setPriority 
参数1. 
PRIORITY_MIN 最低;比如用户下拉通知栏
PRIORITY_LOW 较低;
PRIORITY_DEFAULT 默认;通知栏出现小图标
PRIORITY_HIGH 较高; 放大,排名靠前
PRIORITY_MAX 最高;立刻看到与响应, 比如微信通知弹窗


## 介绍
和 Intent 类似 , 都用于指明'意图',可以用于启动 Activity/Service/BroadCast.
和 Intent 不同 , Intent 立即执行 , PendingIntent 延迟执行.

## 使用
### 1. 静态获取 PendingIntent 实例
getActivity()
getBroadcast()
getService()
参数1 Context
参数2 0
参数3 Intent对象
参数4 PendingIntent 行为: FLAG_ONE_SHOT FLAG_NO_CREATE FLAG_CANCEL_CURRENT FLAG_UPDATE_CURRENT

### 2. 构造器连缀一个 setContentIntent
NotificationCompat.Builder.setContentIntent() 
参数 PendingIntent 对象
```
Intent intent = new Intent(this, NotificationActivity.class);
PendingIntent pi = PendingIntent.getActivity(this,  0 ,intent, 0);
...
Notification notification = new NotificationCompat.Builder(this)
	.setContentIntent(pi)
```

### 3. 取消系统状态栏上面的通知图标
3.1 NotificationCompat.Builder 连缀 .setAutoCancel(true)
3.2 利用 Manager 的 cancel()
```
NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
manager.cancel(1);
```