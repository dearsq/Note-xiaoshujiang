---
title: [Android] AS 导入源码中的 App “Setting”
tags: AndroidStduio,Android
grammar_cjkRuby: true
---
Platform: RockChip
OS: Android 6.0 
Kernel: 4.4

[TOC]


## 问题
希望在 AndroidStudio 中看 Android 中 Setting App 的源码。
解决步骤在后面。

仍然存在的问题：
1. 因为 Setting App 是系统级 App ，所以调用了很多系统资源，所以无法在 AS 中编译（意思是 只能用 AS 看源码），暂时还不知道怎么修改。
可以关注这个问题 ：
http://stackoverflow.com/questions/25517643/how-can-i-work-with-the-settings-app-of-aosp

2. 另外如果想用 Android Studio 查看整个 Android SDK 的源码，方法如下：
http://blog.csdn.net/u014304560/article/details/52357513
http://blog.csdn.net/yanbober/article/details/48846331
前者比较精简，后者比较详细。可以对照着看。


## 步骤
**步骤如下图**

![](https://ws2.sinaimg.cn/large/ba061518gw1f9zhmkygunj20ll0dkdim.jpg)

![](https://ws1.sinaimg.cn/large/ba061518gw1f9zhndcs3nj20zk0sqtd1.jpg)

![](https://ws4.sinaimg.cn/large/ba061518gw1f9zhnqxs6dj20ek0diab7.jpg)

![](https://ws2.sinaimg.cn/large/ba061518gw1f9zhnvs7v6j20ek0ditb9.jpg)

![](https://ws4.sinaimg.cn/large/ba061518gw1f9zho2v1w9j20fe02uaa9.jpg)

至此可以利用 AndroidStudio **查看** 这个 App 的源码了。
![](https://ws4.sinaimg.cn/large/ba061518gw1f9zhuxuf16j20xw0tc4gr.jpg)

但是暂时有如下问题问题是无法编译的。
![](https://ws4.sinaimg.cn/large/ba061518gw1f9zhvx68xsj20xw0tce0n.jpg)

寻求大牛解决得到的反馈是，
” 系统级 APP 里面引用了很多系统的资源，直接导入 IDE 是不行的，需要进行很多配置。 建议用 IDE 阅读，还是在 源码下 去编辑。“

如果有哪位小伙伴了解如何解决这个问题的，希望能告知～先谢谢啦～
