---
title: [Android6.0][RK3399] 休眠唤醒调试步骤
tags: rockchip,suspend,resume
grammar_cjkRuby: true
---

对于 ARMv8 的休眠唤醒操作是在 ATF（Arm Trusted Firmware）中实现的，也就是 trust.img 。这部分的代码是未开放的，不同的需求可以通过 DTS 配置系统 SLEEP 时进入不同的低功耗模式。

DTS 也可以配置对应的唤醒源使能。

RK3399 有 4 路 PWM，不同的硬件上可能有用到若干路作为调压使用，为保证稳定性需要在休眠前必须设置 PWM 控制的几路电压为默认电压，唤醒恢复。

