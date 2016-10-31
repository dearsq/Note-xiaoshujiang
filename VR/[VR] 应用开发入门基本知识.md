---
title: [VR] 应用开发入门基本知识(Oculus/Cardboard/Daydream)
tags: VR
grammar_cjkRuby: true
---

近两天搜集 VR 开发的相关资料。整理如下，也算是对希望进入 VR 应用开发的初学者有个指引与规划的作用。

[TOC]

## 技术概览
VR 核心技术体现在以下几个方面：
**全立体显示**（3D 显示）：包括反畸变算法、多图像处理
**运动追踪**：利用陀螺仪 GyroscopeSensor 加速度计 G-Sensor 等来感应我们身体移动和头部转动
**输入设备**：触摸板、手柄、无线体感设备、手势识别
利用手柄的典型方案比如 HTC 的 Vive、Sony 的 PS VR
无线体感设备比如 雷射的 Hydra、Sixense 的 STEM
手势识别感应设备比如 Leap Motion 和 Nimble VR
具体哪种方式会成为未来 **VR 的 “鼠标**” 暂时还不明朗。
**开发工具**：OpenGL 提供的 API、Unity3D 引擎 等 

## 三种解决方案
VR 设备代表性的目前有 Oculus Rift、GearVR、谷歌盒子
他们分别采用了三种解决方案：
1. 分体机（Oculus Rift ）
2. 一体机（Gear VR）
3. VR 盒子（Cardboard）
### Oculus Rift
Oculus Rift 是 Oculus 开发的一款头显。要使用它，我们还需要拥有一款强大的主机。
### GearVR
有的人会说 GearVR 是插入手机的 VR 盒子呢～ 但是实际上 GearVR 是属于一体机的。
从技术上来说，因为 GearVR 的产生实际是 Oculus 提供的一种便携式解决方案。它结合了 Oculus 的光学技术、头部追踪技术以及三星的 OLED 高分辨率屏等。运用了头盔中内置陀螺仪传感器而不是采用的手机中的传感器，这实际上是所有一体机的设计模式。
从市场上来说，我们一般也是将 GearVR 与一体机来进行比较的，而且 GearVR + 三星手机 比市场上大多数 3000元以下的一体机的体验都要好。
### Cardboard
谷歌纸盒 实际上是 Google 开放的一种**规格**。
我们只需要下载安装 Google 纸盒支持的应用程序，然后将手机放在纸盒中运行就可以了。
现在市面上很多的 VR 盒子都是参考 Cardboard 的规格来设计的。


实际上还有 Google 的 **Daydream**。
>“Cardboard上的应用主要是有趣的短视频体验， 几乎没有任何交互。
> 但是 Daydream 则相反， 主要是提供沉浸式高度交互性的内容。”

但是 Daydream 暂时还未正式发布，暂时不表。

## VR 应用的分类
在不同类型的应用中我们所用到的开发技术也有所区别。
### 浏览器
现在浏览器已经开始慢慢支持 VR。我们可以运用 HTML5、WebGL、JavaScript 这些技术快速开发 VR 应用。并且这些应用的跨平台性还很不错。
### 视频
视频和游戏完全不同。我们知道 游戏中的图像大都是合成的，但是 VR 视频的内容是拍摄的现实世界的内容。
这方面涉及的知识属于 “3D 录像”（facebook 有开源一个 利用17个摄像头实现全景录像的项目，surround360，大家可以去 Github 上面自己瞅～）。
### 游戏、VR OS、普通应用
本文主要讨论的，同时也是行业内一般所称的 VR 应用指的是 VR 中的普通应用（比如设置菜单、图库、播放器），主题，以及 VR 游戏等。
采用的开发工具多为 **Unity3D**。
但是根据不同的平台（一体机、分体机、VR 盒子），也会有一些差异，在后面将会具体的描述。

## 三种方案中对应的开发工具
前文有说现在 VR 产品的表现形式大致有三种：
1. 分体机（Oculus Rift ）
2. 一体机（Gear VR）
3. VR 盒子（Cardboard）

后面逐一列一下他们分别用到的具体开发工具。
### 分体机
以 Oculus Rift 为例，我们需要
1. [VR 硬件设备（DK2）](https://www3.oculus.com/en-us/dk2/)
2. 下载 [运行库](https://developer.oculus.com/)
3. 下载 Oculus 的 SDK。这个需要你去 Oculus 官网上注册帐号，然后填写你使用的平台的相关信息。

我们要开发 Oculus Rift 的桌面端 VR 应用可以参考这两篇文章
[Oculus 开发环境配置（基于 Unity）](http://www.jianshu.com/p/fbe643385fb1)
[Oculus Unity 开发指南](http://forum.exceedu.com/forum/forum.php?mod=viewthread&tid=34175)

### 一体机
以 GearVR 为例。
硬件上我们需要一部 S6 或者 Note4 以上的三星手机，
软件上我们需要
1. 下载 [Oculus 的移动端 SDK](http://developer.oculus.com)（后面简称 移动端SDK）

  注册一个账户，然后
  1）在顶部导航栏选择Downloads页面。
  2）在SDK下拉选项中选择SDK:MOBILE。
  3）点击最新移动端SDK链接。
  4）同意使用许可协议。
  5）下载SDK的压缩包。

2. 下载 Android 的 SDK
我是在 Android Studio 中下载的 SDK，你也可以在 [Android 官网 SDK 下载界面](http://developer.android.com/sdk/installing/index.html) 下载。

3. 生成 Oculus 签名文件
我们需要签名文件才可以让应用在你的手机上运行，因为通过移动端 SDK 构建的 VR 应用需要一个唯一的签名才可以调用更底层的API。
在 [Oculus开发者官网](http://developer.oculus.com/osig/) 上可以进行签名文件的生成。
有 Android 设备调试经验的应该了解 adb，我们将 adb devices 获取到的 id 复制到上面的网站相应区域，然后可以获取签名文件。

4. 采用 Unity 开发 GearVR 应用。
可以参考这一篇[文章](http://blog.csdn.net/liulong1567/article/details/51164581)。

### VR 盒子
以 Google Cardboard 为例，
Google 为 Cardboard 提供了[两套 SDK](https:developers.google.com/cardboard/overview/)，一套用作 Android 原生开发，一套用作 Unity3D 引擎开发。

这里是一个[基于 Cardboard SDK 利用 Unity3D 开发的小例子](http://blog.csdn.net/cartzhang/article/details/52959035)
这里是一个[开发 Google VR 的简要教程](http://www.jianshu.com/p/09c0822b9d1e) ，这个博客后面两篇文章还介绍了两个 Google 开源的项目（VR 全景图播放器、VR 视频播放器）


## 其他知识点
因为我并非专业 VR 应用开发者，在搜集资料的时候也碰到一些概念不大了解。所以归纳总结如下，如果有误还请指出，谢谢～
### OpenGL 与 Unity3D
**OpenGL** 是一个相对底层的框架。会提供一系列函数框架作为 API 提供给开发者使用。
**Unity3D** 是一个跨平台的游戏引擎。解决的是游戏制作人通过什么东西来做游戏的问题。本身包含很多游戏相关的功能，比如绘图，播动画，放音乐，联网等等。

Unity会用到OpenGL来绘制它要绘制的2D、3D图形。这两者的关系，好比汽车与它的引擎，汽车一定需要引擎，但是引擎可不知道它被用在哪个汽车上([via 周华](https://www.zhihu.com/question/27069587/answer/35317198))。

### Unity3D
Unity3D 是一个很强大的游戏引擎，并且它是我们制作 VR 应用的首选方案(via [MichaelLiew](http://blog.csdn.net/liulong1567/article/details/50698834))。
Unity结合Oculus的SDK提供了一整套的VR开发解决方案，其中还包括示例场景和入门教程。

Unity3D 的学习资料 [这里](http://www.51zxw.net/list.aspx?cid=454) 的一套比较好。

