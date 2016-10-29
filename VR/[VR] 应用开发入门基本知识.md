---
title: [VR] 应用开发入门基本知识(Oculus/Cardboard/Daydream)
tags: VR
grammar_cjkRuby: true
---

近两天搜集 VR 开发的相关资料。整理如下，也算是对希望进入 VR 应用开发的初学者有个指引与规划的作用。

[TOC]

## 三种解决方案
**Oculus、Cardboard、Daydream**
Oculus VR公司被 Facebook 收购了。算是 FB 阵营。
后面两个实际上都是 Google 提供的。算是 Google 阵营。[Google VR 链接](https://developers.google.com/vr/)
Oculus 自家有出一体机 Rift，也有和三星合作出 GearVR（盒子）。
Cardboard 成本低，更趋向于演示 demo。
Daydream 是一个更高的终端虚拟现实体验。
>“Cardboard上的应用主要是有趣的短视频体验， 几乎没有任何交互。
> 但是 Daydream 则相反， 主要是提供沉浸式高度交互性的内容。”

### Oculus
OculusVR 公司不仅提供软件  SDK，自己也有做硬件，他们的 [Oculus Rift](https://zh.wikipedia.org/wiki/Oculus_VR) （一体机）是一个虚拟现实的头戴式显示器。
同时，三星的 Gear VR（手机盒子）也是基于 Oculus 的硬件模具和软件来进行开发的。

[Oculus 开发环境配置（基于 Unity）](http://www.jianshu.com/p/fbe643385fb1)
[Oculus Unity 开发指南](http://forum.exceedu.com/forum/forum.php?mod=viewthread&tid=34175)

### Google VR
Google VR SDK & NDK 不仅可以适用于 Cardboard，也适用于 Daydream。
**Cardboard**：现在市场上很多手机盒子是基于 Cardboard 的模具来进行设计的。他们的特点是价格低廉，体验方便，沉浸感欠妥。
**Daydream**：是基于 Android 的解决方案，内置于 Android N 中。

Google VR 提供了一些基本的 API，如果我们的盒子符合 Cardboard 的设计标准，调用这些 API 就可以去适配 Cardboard。
同时，它还提供了一些更加高级的 API，调用那些 API 就可以去适配支持 Daydream 的设备。

[Cardboard 开发环境介绍](https://developers.google.com/vr/cardboard/overview)
软件开发 SDK 有四个平台的 Android、U3D、UE4、iOS
[Daydream 开发环境介绍](https://developers.google.com/vr/daydream/dev-kit-setup)
软件 SDK 有三个平台的，Android、U3D、UE4
硬件 需要一部 API > 19 的 Android 手机 和 一个 VR 盒子（可以插入手机）

[这里](http://www.jianshu.com/p/09c0822b9d1e) 有一个开发 Google VR 的简要教程。


## 区分两个概念 OpenGL 与 Unity3D
**OpenGL** 是一个相对底层的框架。会提供一系列函数框架作为 API 提供给开发者使用。
**Unity3D** 是一个跨平台的游戏引擎。解决的是游戏制作人通过什么东西来做游戏的问题。本身包含很多游戏相关的功能，比如绘图，播动画，放音乐，联网等等。

Unity会用到OpenGL来绘制它要绘制的2D、3D图形。这两者的关系，好比汽车与它的引擎，汽车一定需要引擎，但是引擎可不知道它被用在哪个汽车上([via 周华](https://www.zhihu.com/question/27069587/answer/35317198))。


## Oculus + Unity3D
了解上面两个概念的区别后，我们知道 Unity3D 可以用来开发游戏，同时可以用其来开发 VR 应用。
所以如果想要成为 VR 开发者的话，我们可以选择使用“**集成了 Oculus PC/移动 SDK 的 U3D 工具**”来为 VR 设备开发应用。
[Oculus Unity Development Guide开发指南](http://forum.exceedu.com/forum/forum.php?mod=viewthread&tid=34175)

## Cardboard + Unity3D
同样，我们也可以选择使用 “**集成了 Cardboard SDK 的 U3D 工具**”来为 VR 设备开发应用。

[Cardboard for U3D](https://developers.google.com/cardboard/unity/)
[基于Unity3D的google cardboard开发](http://blog.csdn.net/wuyt2008/article/details/50236211)

## Cardboard + OpenGL
如果你熟悉 OpenGL 框架的话，你甚至可以直接采用 [Cardboard SDK for  Android](https://developers.google.com/vr/android/) 来进行开发。


## 比方
这三种开发方式，我们可以打个比方。
如果说 Unity3D 是一个引擎，那么 OpenGL 就是这个引擎发动的原理（内燃机）。Oculus 或者 Cardboard 是不同的燃料。

如果我们要完成一个飞机（Android VR应用）的制造。
可以选择现成的引擎（Unity3D）来完成制造。
也可以不用引擎（U3D），自己直接去操作内燃机（OpenGL）。

所以完成VR应用开发就好像
**飞机（Android VR 应用） <==  燃料 （Cardboad)）+ 内燃机（OpenGL）**
或者
**飞机（Android VR 应用）<== 引擎（集成了 Cardboard SDK 的 U3D）**
**飞机（Android VR 应用）<== 引擎（集成了 Oculus SDK 的 U3D）**

其实其他端（iOS、PC）的应用我们也能直接用引擎来做
**汽车（PC 端 VR 应用）<== 引擎（集成了 Oculus SDK 的 U3D）**

