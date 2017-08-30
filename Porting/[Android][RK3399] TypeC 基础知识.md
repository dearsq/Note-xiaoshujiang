---
title: [Android][RK3399] TypeC 基础知识
tags: typec
grammar_cjkRuby: true
---

[TOC]

## TypeC 基本特性
* 正反插
* 速度快 10Gbps

## 引脚定义

![](http://ww1.sinaimg.cn/large/ba061518gy1fj1ve6r1jfj20dw034754.jpg)

TX/RX 两组差分信号用来进行数据传输。

CC1 和 CC2 作用：
1. 区分正反面
2. 区分 DFP （Host）和 UFP（Device）
3. 配置 VBUS，有 USB TypeC 和 USB Power Delivery 两种模式
4. 配置 Vconn，当线缆中有芯片时，一个 CC 传输信号，一个 CC 变成供电 Vconn
5. 配置其他模式，比如接音频时、dp时、pcie时 等等。


Vbus 电源 和 GND 都有 4 个，这也是为何可以达到 100W 的原因。
最高可以支持 20V/5A，但是需要 USB PD 芯片的支持。

SUB1 和 SUB2 （Side band use），在一些特殊的传输模式下才会使用。

D+ D- 用来兼容 USB 之前的标准。


## TypeC 如何确定充电方向

TypeC 设备有三种形式：
**DFP**（Downstream Facing Port）：只能作 Source（Host），比如充电器。
**UFP**（Upstream Facing Port）：只能作 Sink（Device），比如 U盘、鼠标、键盘、老款的手机（UFP TypeC 头的手机）。
**DRP**：两者都可以作。比如新款的手机（DRP TypeC头的手机），平板，笔记本。

所以，如果我们手上有一个 TypeC 的手机，有可能有两种情况：
1. 手机上是 UFP 的 C 母头。无论是接到充电器还是电脑，都会被充电。
2. 手机上是 DRP 的 C 母头。
2.1 插到充电器，因为充电器只能作 DFP，所以手机会切换为 UFP，进而被充电
2.2 插到笔记本、另一台手机 或是 充电宝：
2.2.1 手机、电脑、充电宝 会随机当 host 和 sink，每次插拔后角色互换（前提是支持 PD 协议）
2.2.2 手机、电脑、充电宝 有一方有作为 host 端的偏好设定。此时有偏好设定的一方会称为 host 端。

注：偏好设定是最新的 TypeC 规范中对 DRP 部分的描述，新增了两种类型：
1. DRP try source：和DRP或者DRP try sink相连时，会连成Source。
2. DRP try sink：和DRP或者DRP try source相连时，会连成sink。

## TypeC 确定设备类型的原理

### usb 模式

![](http://ww1.sinaimg.cn/large/ba061518gy1fj1vq6xpsxj20dw05y0ti.jpg)

根据 CC 引脚区分 DFP （Host） 和 UFP （Device）。

在 DFP 的 CC pin 有上拉电阻 Rp（阻值不确定，后面会说） ，在 UFP 的 CC pin 有下拉电阻 Rd 5.1k。
没有连接的时候，DFP VBUS 没有输出。
连接时，CC pin 相连，DFP 的 CC 会检测到 UFP 的下拉电阻 Rd，此时表示连接上了，DFP 就会打开 VBUS 电源，输出电源给 UFP。希望能提供原始文档。

具体哪个 CC pin 检测到下拉电阻，就决定了插入方向，顺便切换 RX/TX。

![](http://ww1.sinaimg.cn/large/ba061518gy1fj1warqqhkj20dw06bmyy.jpg)

UFP 的下拉电阻 Rd = 5.1 k
DFP 的上拉电阻 Rp 阻值不确定，因为需要这个电阻来确定 USB TypeC 的几种供电模式。
当 Rp 值不同，CC pin 检测到的电压就不同，进而控制 DFP 使用哪种供电模式。

虽然有两个 CC，
但是实际在不含芯片的线缆中只有一根 CC 线，
含芯片的线缆也不是两根 CC 线，是一根 CC 线，一根 Vconn 用来给芯片供电（3.3V或者5V），此时 CC 端下拉电阻 Ra = 800-1.2k 欧

### 音频配件模式
两个 CC pin 都接了下拉电阻 <= Ra 时，DFP 进入音频配件模式，左右声道、mic 都具备

### DP 模式 和 PCIe 模式
USB PD 是在 CC pin 上传输，PD 有个 VDB（Vendor defined message ）功能，定义了 Device 端 ID，读到了支持 DP 或者 PCIe 的装置，就进入 alternate 模式。

如果 DFP 认到 device 为 DP，便切换 MUX/Configuration Switch，让 Type-C USB3.1 信号脚改为传输 DP 信号。AUX 辅助由 Type-C 的 SBU1,SUB2 来传。HPD 是检测脚，和 CC 差不多，所以共用。

而 DP 有 lane0-3 四组差分信号， Type-C 有 RX/TX1-2 也是四组差分信号，所以完全替代没问题。而且在 DP 协议里的替代模式，可以 USB 信号和 DP 信号同时传输，RX/TX1 传输 USB 数据，RX/TX2 替换为 lane0,1 两组数据传输，此时可支持到 4k。

如果 DFP 认到 device 为 DP，便切换 MUX/Configuration Switch，让 Type-C USB3.1 信号脚改为传输 PCIe 信号。同样的，PCIe 使用 RX/TX2 和 SBU1,SUB2 来传输数据，RX/TX1 传输 USB 数据。

这样的好处就是一个接口同时使用两种设备，当然了，转换线就可以做到，不用任何芯片。