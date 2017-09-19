---
title: [Android6.0][RK3399] 电池管理系统
tags: rockchip,powermanager
grammar_cjkRuby: true
---

本文是对 wowotech.net 上讲解电源管理系统系列相关文章的学习笔记。
原文地址 http://www.wowotech.net/pm_subsystem/pm_architecture.html

## 架构组成

电源管理（Power Management）在Linux Kernel中，是一个比较庞大的子系统，涉及到供电（Power Supply）、充电（Charger）、时钟（Clock）、频率（Frequency）、电压（Voltage）、睡眠/唤醒（Suspend/Resume）等方方面面。


## Generic PM
传统的常规电源管理 包括关机（Power off）、待机（Standby or Hibernate）、重启（Reboot）、冬眠（Hibernate）、睡眠（Sleep 或被称为 Suspend）。
wowtech 在文章中给这种常规的电源管理起名为 Generic PM，它是和 Runtime PM 相对的。

软件架构如下：

![](http://www.wowotech.net/content/uploadfile/201405/84f0e5d0dcb8b687224b39d1f400482620140514034349.gif)

根据上面的描述可知，Generic PM大致可以分为三个软件层次：
**API Layer**，用于向用户空间提供接口，其中关机和重启的接口形式是系统调用（在新的内核中，关机接口还有一种新方式，具体讲到的时候再说），Hibernate和Suspend的接口形式是sysfs。
**PM Core**，位于kernel/power/目录下，主要处理和硬件无关的核心逻辑。
**PM Driver**，分为两个部分，一是体系结构无关的Driver，提供Driver框架（Framework）。另一部分是具体的体系结构相关的Driver，这也是电源管理驱动开发需要涉及到的内容（图中红色边框的模块）。

