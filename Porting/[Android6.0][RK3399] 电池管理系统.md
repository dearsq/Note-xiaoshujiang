---
title: [Android6.0][RK3399] 电源管理系统
tags: rockchip,powermanager
grammar_cjkRuby: true
---

本文是对 wowotech.net 上讲解电源管理系统系列相关文章的学习笔记。
原文地址 http://www.wowotech.net/pm_subsystem/pm_architecture.html

## 一、架构组成

电源管理（Power Management）在Linux Kernel中，是一个比较庞大的子系统，涉及到供电（Power Supply）、充电（Charger）、时钟（Clock）、频率（Frequency）、电压（Voltage）、睡眠/唤醒（Suspend/Resume）等方方面面。


## 二、Generic PM
传统的常规电源管理 包括关机（Power off）、待机（Standby or Hibernate）、重启（Reboot）、冬眠（Hibernate）、睡眠（Sleep 或被称为 Suspend）。
wowtech 在文章中给这种常规的电源管理起名为 Generic PM，它是和 Runtime PM 相对的。

软件架构如下：

![](http://www.wowotech.net/content/uploadfile/201405/84f0e5d0dcb8b687224b39d1f400482620140514034349.gif)

根据上面的描述可知，Generic PM大致可以分为三个软件层次：
**API Layer**，用于向用户空间提供接口，其中关机和重启的接口形式是系统调用（在新的内核中，关机接口还有一种新方式，具体讲到的时候再说），Hibernate和Suspend的接口形式是sysfs。
**PM Core**，位于kernel/power/目录下，主要处理和硬件无关的核心逻辑。
**PM Driver**，分为两个部分，一是体系结构无关的Driver，提供Driver框架（Framework）。另一部分是具体的体系结构相关的Driver，这也是电源管理驱动开发需要涉及到的内容（图中红色边框的模块）。

### 2.1 Generic PM Reboot

**RESTART**，正常的重启，也是我们平时使用的重启。执行该动作后，系统会重新启动。
**HALT**，停止操作系统，然后把控制权交给其它代码（如果有的话）。具体的表现形式，依赖于系统的具体实现。
**CAD_ON/CAD_OFF**，允许/禁止通过Ctrl-Alt-Del组合按键触发重启（RESTART）动作。 
注1：Ctrl-Alt-Del组合按键的响应是由具体的Driver（如Keypad）实现的。
**POWER_OFF**，正常的关机。执行该动作后，系统会停止操作系统，并去除所有的供电。
**RESTART2**，重启的另一种方式。可以在重启时，携带一个字符串类型的cmd，该cmd会在重启前，发送给任意一个关心重启事件的进程，同时会传递给最终执行重启动作的machine相关的代码。内核并没有规定该cmd的形式，完全由具体的machine自行定义。

### 2.2 Power Managent Interface

PM Interface 的功能，对下，定义了 Device PM 相关的回调函数。对上，实现了 PM 统一的操作函数，供 PM 核心逻辑调用。

旧版内核中，PM callbacks 分布在设备模型的大型数据结构中，
如 struct bus_type 中的 suspend、suspend_late、resume、resume_late，
如 struct device_driver/struct class/struct device_type中的suspend、resume。
随着设备复杂度的增加，这些 suspend 和 resume 已经不能满足电源管理的需求，就需要扩充 PM callbacks ，所以会影响这些数据结构。

新版本的内核中，PM callbacks 被统一封装为一个数据结构 struct dev_pm_ops，上层的数据结构只需要包含这个结构即可。
为兼容旧版本也仍然存在 suspend 和 resume ，但是不建议使用。

```
   1: /* include/linux/pm.h, line 276 in linux-3.10.29 */
   2: struct dev_pm_ops {
   3:         int (*prepare)(struct device *dev);
   4:         void (*complete)(struct device *dev);
   5:         int (*suspend)(struct device *dev);
   6:         int (*resume)(struct device *dev);
   7:         int (*freeze)(struct device *dev);
   8:         int (*thaw)(struct device *dev);
   9:         int (*poweroff)(struct device *dev);
  10:         int (*restore)(struct device *dev);
  11:         int (*suspend_late)(struct device *dev);
  12:         int (*resume_early)(struct device *dev);
  13:         int (*freeze_late)(struct device *dev);
  14:         int (*thaw_early)(struct device *dev);
  15:         int (*poweroff_late)(struct device *dev);
  16:         int (*restore_early)(struct device *dev);
  17:         int (*suspend_noirq)(struct device *dev);
  18:         int (*resume_noirq)(struct device *dev);
  19:         int (*freeze_noirq)(struct device *dev);
  20:         int (*thaw_noirq)(struct device *dev);
  21:         int (*poweroff_noirq)(struct device *dev);
  22:         int (*restore_noirq)(struct device *dev);
  23:         int (*runtime_suspend)(struct device *dev);
  24:         int (*runtime_resume)(struct device *dev);
  25:         int (*runtime_idle)(struct device *dev);
  26: };
```

PM Core 会在特定的电源管理阶段，调用相应的 callbacks，比如 suspend/resume 的过程中，函数调用链如下：
prepare—>suspend—>suspend_late—>suspend_noirq---wakeup---->resume_noirq—>resume_early—>resume—>complete。

```
   1: struct bus_type {
   2:         ...
   3:         const struct dev_pm_ops *pm;
   4:         ...
   5: };
   6:  
   7: struct device_driver {
   8:         ...
   9:         const struct dev_pm_ops *pm;
  10:         ...
  11: };
  12:  
  13: struct class {
  14:         ...
  15:         const struct dev_pm_ops *pm;
  16:         ...
  17: };
  18:  
  19: struct device_type {
  20:         ...
  21:         const struct dev_pm_ops *pm;
  22: };
  23:  
  24: struct device {
  25:         ...
  26:         struct dev_pm_info      power;
  27:         struct dev_pm_domain    *pm_domain;
  28:         ...
  29: };
```
重点关注 device 结构中的 power 和 pm_domain 变量。
**power** 变量类型是 struct dev_pm_info 
保存 PM 相关的状态：
```
struct dev_pm_info {
559     pm_message_t        power_state; //当前的 power 状态
560     unsigned int        can_wakeup:1; //是否可以被唤醒
561     unsigned int        async_suspend:1;
562     bool            is_prepared:1;  /* Owned by the PM core */ //是否 prepared 完成
563     bool            is_suspended:1; /* Ditto */ //是否 suspended 完成
564     bool            is_noirq_suspended:1;
565     bool            is_late_suspended:1;
566     bool            ignore_children:1;
567     bool            early_init:1;   /* Owned by the PM core */
568     bool            direct_complete:1;  /* Owned by the PM core */
569     spinlock_t      lock;
570 #ifdef CONFIG_PM_SLEEP
571     struct list_head    entry;
572     struct completion   completion;
573     struct wakeup_source    *wakeup;
574     bool            wakeup_path:1;
575     bool            syscore:1;
576     bool            no_pm_callbacks:1;  /* Owned by the PM core */
577 #else
578     unsigned int        should_wakeup:1;
579 #endif
580 #ifdef CONFIG_PM
581     struct timer_list   suspend_timer;
582     unsigned long       timer_expires;
583     struct work_struct  work;
584     wait_queue_head_t   wait_queue;
585     struct wake_irq     *wakeirq;
586     atomic_t        usage_count;
587     atomic_t        child_count;
588     unsigned int        disable_depth:3;
589     unsigned int        idle_notification:1;
590     unsigned int        request_pending:1;
591     unsigned int        deferred_resume:1;
592     unsigned int        run_wake:1;
593     unsigned int        runtime_auto:1;
594     unsigned int        no_callbacks:1;
595     unsigned int        irq_safe:1;
596     unsigned int        use_autosuspend:1;
597     unsigned int        timer_autosuspends:1;
598     unsigned int        memalloc_noio:1;
599     enum rpm_request    request;
600     enum rpm_status     runtime_status;
601     int         runtime_error;
602     int         autosuspend_delay;
603     unsigned long       last_busy;
604     unsigned long       active_jiffies;
605     unsigned long       suspended_jiffies;
606     unsigned long       accounting_timestamp;
607 #endif
608     struct pm_subsys_data   *subsys_data;  /* Owned by the subsystem. */
609     void (*set_latency_tolerance)(struct device *, s32);
610     struct dev_pm_qos   *qos;
611 };

```

**pm_domain**  指针
PM domain 是针对 device 而言的，通过 PM domain 实现没有 driver 的 device 的电源管理。
```
617 /*
618  * Power domains provide callbacks that are executed during system suspend,
619  * hibernation, system resume and during runtime PM transitions along with
620  * subsystem-level and driver-level callbacks.
621  *
622  * @detach: Called when removing a device from the domain.
623  * @activate: Called before executing probe routines for bus types and drivers.
624  * @sync: Called after successful driver probe.
625  * @dismiss: Called after unsuccessful driver probe and after driver removal.
626  */
627 struct dev_pm_domain {
628     struct dev_pm_ops   ops;
629     void (*detach)(struct device *dev, bool power_off);
630     int (*activate)(struct device *dev);
631     void (*sync)(struct device *dev);
632     void (*dismiss)(struct device *dev);
633 };
```

### 2.3 device PM callbacks API

为了操作 device PM callbacks 数据结构，定义了大量 API。分为两类：
通用的辅助性质类 API：
直接调用指定设备所绑定的driver的、pm指针的、相应的callback
比如 pm_generic_prepare，查看dev->driver->pm->prepare接口是否存在，如果存在，直接调用并返回结果。

整体电源管理行为相关 API：
将各个独立的电源管理行为组合起来，组成一个较为简单的功能
比如 dpm_prepare，执行所有设备的“->prepare() callback(s)”
比如 dpm_suspend，执行所有设备的“->suspend() callback(s)”
比如 dpm_suspend_start，依次执行dpm_prepare和dpm_suspend两个动作
比如 dpm_suspend_end，依次执行所有设备的“->suspend_late() callback(s)”以及所有设备的“->suspend_noirq() callback(s)”
上面是休眠相关的。
dpm_resume、dpm_complete、dpm_resume_start、dpm_resume_end，是电源管理过程的唤醒动作。和上面类似。


## 三、Hibernnate & Sleep

Hibernate和Sleep两个功能是Linux Generic PM的核心功能，它们的目的是类似的：
暂停使用——>保存上下文——>关闭系统以节电········>恢复系统——>恢复上下文——>继续使用