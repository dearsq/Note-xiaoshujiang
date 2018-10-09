---
title: 组件_Service.md
tags: android
grammar_cjkRuby: true
---

## 基本概念

Service 是 Android 中实现程序后台运行的解决方案, 
适合执行那些不需要和用户交互而且还要求长期运行的任务.


![](https://ws1.sinaimg.cn/large/ba061518gy1fui895t2mjj20mq0bpwg4.jpg)

### 4个手动调用的方法
startService()	启动服务, 手动调用 startService() 后，自动调用内部方法：onCreate()、onStartCommand().
stopService()	关闭服务, 手动调用 stopService() 后，自动调用内部方法：onDestory(). 但是如果没有解绑, 是无法停止服务的
bindService()	绑定服务, 手动调用 bindService()后，自动调用内部方法：onCreate()、onBind().
unbindService()	解绑服务, 手动调用 unbindService()后，自动调用内部方法：onCreate()、onBind()、onDestory()


### 内部自动调用的方法
onCreat()	创建服务
onStartCommand()	开始服务
onDestroy()	销毁服务
onBind()	绑定服务
onUnbind()	解绑服务

### 重要知识点
startService()和 stopService()只能开启和关闭Service，无法操作Service； 
bindService()和 unbindService()可以操作 Service

startService() 开启的Service，调用者退出后Service仍然存在； 
BindService() 开启的Service，调用者退出后，Service随着调用者销毁。

## 只使用 startService 启动服务的生命周期
手动 startService()
onCreate()
onStartCommand()
手动 stopService()
onDestory()

## 只使用 bindService 绑定服务的生命周期
手动 bindService()
onCreate()
onBind()
手动 unBindService()
onUnbind()
onDestory()

## 同时使用 startService BindService 服务的生命周期
手动 startService()
onCreate()
onStartCommand()
手动 BindService()
onBind()
手动 unBindService()
onUnbind()
手动 StopService()
onDestory()

