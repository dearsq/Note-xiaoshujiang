---
title: [Android6.0][RK3399][BUG] 插上 HDMI 时开机解锁锁屏后死机
tags: hdmi
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: Linux4.4
Version: v2017.03

## 现象

插上 HDMI 情况下开机，解锁锁屏，会死机。

Kernel 出现如下 log 信息：
```
[   18.415959] rk322x-lcdc vop0: intr post buf empty!
[   18.416010] rk322x-lcdc vop0: intr post buf empty!
[   18.432623] rk322x-lcdc vop0: intr post buf empty!
[   18.432666] rk322x-lcdc vop0: intr post buf empty!
[   18.449288] rk322x-lcdc vop0: intr post buf empty!
```
Android 出现如下异常
```
01-18 09:13:49.558 E/Zygote  (  215): Exit zygote because system server (499) has terminated
01-18 09:13:49.562 E/DisplayManager( 1465): Could not get display ids from display manager.
01-18 09:13:49.562 E/DisplayManager( 1465): android.os.DeadObjectException
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.hardware.display.IDisplayManager$Stub$Proxy.getDisplayIds(IDisplayManager.java:295)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getDisplayIds(DisplayManagerGlobal.java:154)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getDisplays(DisplayManager.java:284)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.getAllPresentationDisplays(MediaRouter.java:320)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.choosePresentationDisplay(MediaRouter.java:1868)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.updatePresentationDisplay(MediaRouter.java:1858)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:140)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.562 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.566 E/DisplayManager( 1465): Could not get display information from display manager.
01-18 09:13:49.566 E/DisplayManager( 1465): android.os.DeadObjectException
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.IDisplayManager$Stub$Proxy.getDisplayInfo(IDisplayManager.java:273)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getDisplayInfo(DisplayManagerGlobal.java:119)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getCompatibleDisplay(DisplayManagerGlobal.java:178)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getOrCreateDisplayLocked(DisplayManager.java:326)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.addPresentationDisplaysLocked(DisplayManager.java:314)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getDisplays(DisplayManager.java:291)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.getAllPresentationDisplays(MediaRouter.java:320)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.choosePresentationDisplay(MediaRouter.java:1868)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.updatePresentationDisplay(MediaRouter.java:1858)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:140)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.566 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.567 E/DisplayManager( 1465): Could not get display information from display manager.
01-18 09:13:49.567 E/DisplayManager( 1465): android.os.DeadObjectException
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.IDisplayManager$Stub$Proxy.getDisplayInfo(IDisplayManager.java:273)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getDisplayInfo(DisplayManagerGlobal.java:119)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getCompatibleDisplay(DisplayManagerGlobal.java:178)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getOrCreateDisplayLocked(DisplayManager.java:326)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.addPresentationDisplaysLocked(DisplayManager.java:314)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getDisplays(DisplayManager.java:292)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.getAllPresentationDisplays(MediaRouter.java:320)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.choosePresentationDisplay(MediaRouter.java:1868)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.updatePresentationDisplay(MediaRouter.java:1858)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:140)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.567 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.569 E/DisplayManager( 1465): Could not get display information from display manager.
01-18 09:13:49.569 E/DisplayManager( 1465): android.os.DeadObjectException
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.IDisplayManager$Stub$Proxy.getDisplayInfo(IDisplayManager.java:273)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getDisplayInfo(DisplayManagerGlobal.java:119)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getCompatibleDisplay(DisplayManagerGlobal.java:178)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getOrCreateDisplayLocked(DisplayManager.java:326)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.addPresentationDisplaysLocked(DisplayManager.java:314)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getDisplays(DisplayManager.java:293)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.getAllPresentationDisplays(MediaRouter.java:320)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.choosePresentationDisplay(MediaRouter.java:1868)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.media.MediaRouter$RouteInfo.updatePresentationDisplay(MediaRouter.java:1858)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:140)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.569 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.570 E/DisplayManager( 1465): Failed to get Wifi display status.
01-18 09:13:49.570 E/DisplayManager( 1465): android.os.DeadObjectException
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.hardware.display.IDisplayManager$Stub$Proxy.getWifiDisplayStatus(IDisplayManager.java:462)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManagerGlobal.getWifiDisplayStatus(DisplayManagerGlobal.java:355)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.hardware.display.DisplayManager.getWifiDisplayStatus(DisplayManager.java:469)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:144)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.570 E/DisplayManager( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.574 D/AndroidRuntime( 1465): Shutting down VM
--------- beginning of crash
01-18 09:13:49.575 E/AndroidRuntime( 1465): FATAL EXCEPTION: main
01-18 09:13:49.575 E/AndroidRuntime( 1465): Process: com.android.systemui, PID: 1465
01-18 09:13:49.575 E/AndroidRuntime( 1465): java.lang.RuntimeException: Unable to create service com.android.systemui.SystemUIService: java.lang.NullPointerException: Attempt to invoke interface method 'android.media.AudioRoutesInfo android.media.IAudioService.startWatchingRoutes(android.media.IAudioRoutesObserver)' on a null object reference
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2893)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ActivityThread.-wrap4(ActivityThread.java)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1430)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.os.Handler.dispatchMessage(Handler.java:102)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.os.Looper.loop(Looper.java:148)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ActivityThread.main(ActivityThread.java:5426)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at java.lang.reflect.Method.invoke(Native Method)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:772)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:662)
01-18 09:13:49.575 E/AndroidRuntime( 1465): Caused by: java.lang.NullPointerException: Attempt to invoke interface method 'android.media.AudioRoutesInfo android.media.IAudioService.startWatchingRoutes(android.media.IAudioRoutesObserver)' on a null object reference
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.media.MediaRouter$Static.startMonitoringRoutes(MediaRouter.java:155)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.media.MediaRouter.<init>(MediaRouter.java:720)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:193)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.SystemServiceRegistry$7.createService(SystemServiceRegistry.java:192)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.SystemServiceRegistry$CachedServiceFetcher.getService(SystemServiceRegistry.java:790)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.SystemServiceRegistry.getSystemService(SystemServiceRegistry.java:743)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ContextImpl.getSystemService(ContextImpl.java:1365)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.content.ContextWrapper.getSystemService(ContextWrapper.java:627)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.keyguard.KeyguardDisplayManager.<init>(KeyguardDisplayManager.java:41)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.setupLocked(KeyguardViewMediator.java:561)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.systemui.keyguard.KeyguardViewMediator.start(KeyguardViewMediator.java:616)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.systemui.SystemUIApplication.startServicesIfNeeded(SystemUIApplication.java:139)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at com.android.systemui.SystemUIService.onCreate(SystemUIService.java:31)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	at android.app.ActivityThread.handleCreateService(ActivityThread.java:2883)
01-18 09:13:49.575 E/AndroidRuntime( 1465): 	... 8 more
01-18 09:13:49.576 E/AndroidRuntime( 1465): Error reporting crash
01-18 09:13:49.576 E/AndroidRuntime( 1465): android.os.DeadObjectException
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at android.os.BinderProxy.transactNative(Native Method)
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at android.os.BinderProxy.transact(Binder.java:503)
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at android.app.ActivityManagerProxy.handleApplicationCrash(ActivityManagerNative.java:4440)
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at com.android.internal.os.RuntimeInit$UncaughtHandler.uncaughtException(RuntimeInit.java:90)
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at java.lang.ThreadGroup.uncaughtException(ThreadGroup.java:693)
01-18 09:13:49.576 E/AndroidRuntime( 1465): 	at java.lang.ThreadGroup.uncaughtException(ThreadGroup.java:690)
```


## 解决方法

Vop 的问题。

```

--- a/arch/arm64/boot/dts/rockchip/rk3399-sapphire-excavator-edp.dts
+++ b/arch/arm64/boot/dts/rockchip/rk3399-sapphire-excavator-edp.dts
@@ -78,7 +78,7 @@
 
 &hdmi_rk_fb {
 	status = "okay";
-	rockchip,hdmi_video_source = <DISPLAY_SOURCE_LCDC1>;
+	rockchip,hdmi_video_source = <DISPLAY_SOURCE_LCDC0>;
 };
 
 &hdmi_sound {
@@ -227,8 +227,12 @@
 	#include <dt-bindings/display/screen-timing/lcd-F402.dtsi>
 };
 
-&vopb_rk_fb {
+&vopl_rk_fb {
 	status = "okay";
+	rockchip,prop = <PRMRY>;
+	assigned-clocks = <&cru DCLK_VOP1_DIV>;
+	assigned-clock-parents = <&cru PLL_CPLL>;
+
 	power_ctr: power_ctr {
 		rockchip,debug = <0>;
 		lcd_en: lcd-en {
@@ -253,6 +257,9 @@
 	};
 };
 
-&vopl_rk_fb {
+&vopb_rk_fb {
 	status = "okay";
+	rockchip,prop = <EXTEND>;
+	assigned-clocks = <&cru DCLK_VOP0_DIV>;
+	assigned-clock-parents = <&cru PLL_NPLL>;
 };
diff --git a/include/dt-bindings/clock/rk3399-cru.h b/include/dt-bindings/clock/rk3399-cru.h
index 0fc9e7a..d32ce01 100644
--- a/include/dt-bindings/clock/rk3399-cru.h
+++ b/include/dt-bindings/clock/rk3399-cru.h
@@ -16,7 +16,7 @@
 #ifndef _DT_BINDINGS_CLK_ROCKCHIP_RK3399_H
 #define _DT_BINDINGS_CLK_ROCKCHIP_RK3399_H
 
-/* #define RK3399_TWO_PLL_FOR_VOP */
+#define RK3399_TWO_PLL_FOR_VOP
 
 /* core clocks */
 #define PLL_APLLL			1
```

```
diff --git a/include/configs/rk33plat.h b/include/configs/rk33plat.h
index 1d52381..6aab13a 100755
--- a/include/configs/rk33plat.h
+++ b/include/configs/rk33plat.h
@@ -319,7 +319,6 @@
 #define CONFIG_ROCKCHIP_DW_MIPI_DSI
 #define CONFIG_ROCKCHIP_ANALOGIX_DP
 #define CONFIG_ROCKCHIP_DW_HDMI
-#define CONFIG_RK_HDMI
 #endif
 
 #if defined(CONFIG_RKCHIP_RK3368)
@@ -351,7 +350,7 @@
 
 #endif /* CONFIG_LCD */
 
-
+#define CONFIG_RK_VOP_DUAL_ANY_FREQ_PLL
 /* more config for charge */
 #ifdef CONFIG_UBOOT_CHARGE
 
```