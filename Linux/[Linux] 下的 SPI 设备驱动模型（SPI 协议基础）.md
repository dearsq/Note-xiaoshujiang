---
title: [Linux] 下的 SPI 设备驱动模型（SPI 协议基础）
tags: SPI,Linux,Driver
grammar_cjkRuby: true
---

## SPI 总线概念及特点
### 概念
SPI（Serial Peripheral Interface）穿行外围设备接口，全双工三线同步串行通信接口。
在点对点的通信中，SPI 不需要进行寻址操作。
当有多个从设备时，可以增加一条设备选择线（低电平有效的 CS）。

### 特点
* 单主多从
* 时钟由 Master 控制，在时钟移位脉冲下，数据按位传输，高位在前，低位在后（MSB first）。
* 全双工（可以同时发出和接收串行数据），速率达 12Mbps
* 提供频率可编程时钟; 发送结束 中断标志 ; 写冲突保护 ; 总线竞争保护
缺点是 无法校验

### 总线结构

![](http://ww3.sinaimg.cn/large/ba061518gw1f5j171trzoj20ic06zwf7.jpg)

### GPIO 模拟
如果用 GPIO 模拟 SPI 总线，需要一个输出口（SDO）、一个输入口（SDI）。
如果实现主从设备，需要 SDO 和 SDI; 如果只实现主设备，需要实现 SDO; 如果只实现从设备，需要实现 SDI。

## 接口定义
标准 SPI 有 4 根线（片选 CS、时钟 SCLK、输出 MOSI、输入 MISO）
![](http://ww2.sinaimg.cn/large/ba061518gw1f5j1pa4vvbj20f103rt8x.jpg)
MOSI – 主器件数据输出,从器件数据输入
MISO – 主器件数据输入,从器件数据输出
SCLK – 时钟信号,由主器件 Master 产生
/CS  – 从器件使能信号,由主器件控制


 ## 内部逻辑结构
Master 和 Slave 内部分别有两个 8bit 移位寄存器。
![](http://ww4.sinaimg.cn/large/ba061518gw1f5j1us2gw4j20jb0950tm.jpg)

其实这就相当于一个 环形的总线结构。
在 SCLK 的控制下，两个 8bit shift register 进行数据交换。
example：主机 buffer = 0xAA，从机 buffer = 0x55，假设上升沿发送数据（SPI 有四种发送数据的模式，下一节再讲解）
![](http://ww4.sinaimg.cn/large/ba061518gw1f5j1ys7w2pj20680d0dik.jpg)
如上图，完成了两个8bit寄存器的数据交换。


## 工作模式
有四种工作模式。
由   时钟极性和时钟相位 （CPOL & CPHA） 决定。
CPOL = Clock Polarity  CPHA =Clock Phase

CPOL 设置时钟空闲时的电平
CPOL = 0 :串行同步时钟的空闲状态为低电平
CPOL =1  :串行同步时钟的空闲状态为高电平

CPHA 设置读取数据和发送数据的时钟沿
CPHA =0 :串行同步时钟第一个跳变沿(上升或下降)数据采样
CPHA =1 :串行同步时钟第二个跳变沿(上升或下降)数据采样

第一个跳变沿进行采样：
![](http://ww3.sinaimg.cn/large/ba061518gw1f5j2gsbgpoj20bs04bglt.jpg)
第二个跳变沿进行采样：
![](http://ww4.sinaimg.cn/large/ba061518gw1f5j2gxtbtrj20c704ggls.jpg)

最后：分析 SPI 的四种传输协议可以发现，根据一种协议，只要对串行同步时钟进行转换，就能得到其余的三种协议。
为了简化设计规定，如果要连续传输多个数据，在两个数据传输之间插入一个串行时钟的空闲等待，这样状态机只需两种状态（空闲和工作）就能正确工作。
