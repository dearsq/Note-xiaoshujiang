---
title: Mipi LCD 的基础知识
tags: LCD
grammar_cjkRuby: true
---

## 基础知识
LCD（Liquid Crystal Display）即液晶显示器。
根据驱动方式 分为 静态驱动、简单矩阵驱动、主动矩阵驱动。
简单矩阵驱动 分为 扭转向阵列（TN） 和 超扭转时向列型（STN）。
主动矩阵驱动 以 薄膜式晶体管（TFT） 为主。

我们作为驱动工程师，关注的点在于 屏 的时序。
时序图中 
VCLK 为 像素时钟信号（用于锁存图像数据的像素时钟）
HSYNC 为 行同步信号
VSYNC 为 帧同步信号
VDEN 为 数据有效标志信号
VD 为 图像的数据信号
PCLK/DCLK 为 点时钟 dot CLK


![行场控制的 LCD 时序图](http://ww3.sinaimg.cn/large/ba061518gw1f6wulbs1dfj20n10fodhj.jpg)
VSYNC 是 帧同步信号，每发出一个脉冲，意味着新的一屏图像数据开始发送。
HSYNC 是 行同步信号，每发出一个脉冲，意味着新的一行图像资料开始发送。
在 帧同步 和 行同步 头尾 都必须留有回扫时间。

LCD 控制器中我们需要设置一些参数。
VBP（vertical back porch） 上边界 帧切换回扫时间
VFP（vertical front porch） 下边界 帧切换回扫时间
HBP（horizontal back porch）左边界 行切换回扫时间
HFP（horizontal front porch）右边界 行切换回扫时间
HS（hsync，horizontal pulse width）水平同步信号，行同步本身需要的时间
VS（vsync，vertical pulse width）垂直同步信号，帧同步本身需要的时间
H_VALUE/V_VALUE 表示横向分辨率 和 纵向分辨率。

且这些参数遵循如下公式：
HBP + Hsync + HFP + Xres  = HP(horizontal period)
VBP + Vsync + VFP + Yres = VP(vertical period)

了解了这些知识就可以开始 LCD 的移植了。
## 调试流程

## 常见问题和解决方法
