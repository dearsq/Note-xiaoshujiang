---
title: [Linux][RK3399] DRM 框架及代码流程
tags: linux,rockchip,drm
grammar_cjkRuby: true
---

 RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 

## DRM 简介
### 定义
DRM: Direct Rendering Manager 它用于处理显卡（graphic cards embedding GPUs）
KMS: Kernel Mode Setting 它是 DRM API 的一个子集
由 渲染 及 模式设置 方式的差别有两种不同的 API (/dev/dri/renderX 额 /dev/dri/controlDX)
KMS 提供了一种配置显卡的方式

### 对比
Linux 中显示方式还有其他方式，比如 FBDEV 和 V4L2
DRM 的优势在于：
更新很活跃
被广泛用于用户空间图形栈
有一些高级的特性（overlays、hw cursor ...）

### 架构

![](http://ww1.sinaimg.cn/large/ba061518gy1fhr9dpubjqj20jq06vmxj.jpg)

#### 1）DRM Framebuffer

显示信息存储在如下地方：
1. 引用的内存区域被用来存储显示内容
2. 一部分内存用于存储帧的格式
3. 活跃的内存区域中的内容将被显示呈现

#### 2）Planes
#### 3）CRTC
#### 4）Encoder
#### 5）Connector

// TODO
10/49
http://events.linuxfoundation.org/sites/events/files/slides/brezillon-drm-kms.pdf
