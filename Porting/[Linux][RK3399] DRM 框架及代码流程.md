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
由 渲染 及 模式设置 方式的差别有两种不同的 API (/dev/dri/renderX 和 /dev/dri/controlDX)
KMS 提供了一种配置显卡的方式

### 对比
Linux 中显示方式还有其他方式，比如 FBDEV 和 V4L2
DRM 的优势在于：
更新很活跃
被广泛用于用户空间图形栈
有一些高级的特性（overlays、hw cursor ...）

### 架构

![](http://ww1.sinaimg.cn/large/ba061518gy1fhr9dpubjqj20jq06vmxj.jpg)

#### 1）DRM 组件：Framebuffer

显示信息存储在如下地方：
1. 指向被用来存储显示内容的内存区域
2. 一部分内存用于存储帧的格式
3. 活跃的内存区域中的内容将被显示呈现

DRM 帧缓存是一个虚拟的对象（依赖于某一个具体的实现）
帧缓存具体的实现取决于：
  正在使用的内存管理器（GEM或TTM）
  显示控制器功能：支持 DMA、IOMMU
GEM对象的默认实现可以使用CMA（连续内存分配器）：drivers/gpu/drm/drm_fb_cma_helper.c 
其他的实现常常取决于显示控制器
  Scatter Gather 的例子：drivers/gpu/drm/tegra
  IOMMU 的例子：drivers/gpu/drm/exynos

![](http://ww1.sinaimg.cn/large/ba061518gy1fibds6hkixj20lp0b03z9.jpg)
![](http://ww1.sinaimg.cn/large/ba061518gy1fibduaddhej20lo04m3yn.jpg)

`pixel_format` 描述内存缓存组织
FOURCC 格式的编码
支持的格式在如下头文件定义：
include/drm/drm_fourcc.h 
这些 FOURCC 格式 不是标准化的，因此它们仅在 DRM/KMS 子系统中有效。

DRM/KMS 子系统中用到了三种类型的格式：
RGB：每个像素以 RGB 元编码。
YUV：每个像素以 YUV 元编码
C8 ：使用转换表将值映射到RGB元

其中 YUV 支持不同的模式：
封装：一部分内存区域存储所有组件（Y，U和V）
semi-planar：一部分内存区域用来存储 Y 一部分用来存储 UV
plane：用来存所有组件的内存区域

每一个用来存放帧元的内存区域被称作 plane

#### 2）Planes

#### 3）CRTC
#### 4）Encoder
#### 5）Connector

// TODO
14/49
http://events.linuxfoundation.org/sites/events/files/slides/brezillon-drm-kms.pdf
