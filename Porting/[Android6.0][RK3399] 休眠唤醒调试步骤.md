---
title: [Android6.0][RK3399] 休眠唤醒调试步骤
tags: rockchip,suspend,resume
grammar_cjkRuby: true
---


## 一、基础知识
先介绍一些基本的概念。休眠唤醒是 电源管理系统中的一个部分。
电源管理系统是一个比较庞大的子系统，涉及到供电（Power Supply）、充电（Charger）、时钟（Clock）、频率（Frequency）、电压（Voltage）、睡眠/唤醒（Suspend/Resume）。
本文仅仅只涉及到 休眠唤醒部分的调试。后面将会深入到源码去讲解休眠唤醒。

### Runtime PM 和 wakelock
运行时的Power Management，不再需要用户程序的干涉，由Kernel统一调度，实时的关闭或打开设备，以便在使用性能和省电性能之间找到最佳的平衡 。
Runtime PM是Linux Kernel亲生的运行时电源管理机制，Wakelock是由Android提出的机制。这两种机制的目的是一样的，因此只需要支持一种即可。另外，由于Wakelock机制路子太野了，饱受Linux社区的鄙视，但是没办法 Android 用的就是这套机制，所以我们下一篇文章着重分析的也是 wakelock。

### SLEEP mode
休眠模式，RK3399 支持 Core 断电、Logic 断电、DDR 进入 Retention 状态，OSC Disable。

### 唤醒源
系统处在休眠时，可以接受唤醒源的中断。

### DTS 中的配置方法
于 ARMv8 的休眠唤醒操作是在 ATF（Arm Trusted Firmware）中实现的，也就是 trust.img 。这部分的代码是未开放的，不同的需求可以通过 DTS 配置系统 SLEEP 时进入不同的低功耗模式。

同样，DTS 也可以配置对应的唤醒源使能。

参见 ./Documentation/devicetree/bindings/soc/rockchip/rockchip-pm-config.txt
配置方法如下：
```
rockchip_suspend: rockchip-suspend {
        compatible = "rockchip,pm-rk3399";
        status = "disabled";
        rockchip,sleep-debug-en = <0>; 
        rockchip,virtual-poweroff = <0>; 
        rockchip,sleep-mode-config = <
            (0
            | RKPM_SLP_ARMPD
            | RKPM_SLP_PERILPPD
            | RKPM_SLP_DDR_RET
            | RKPM_SLP_PLLPD
            | RKPM_SLP_OSC_DIS
            | RKPM_SLP_CENTER_PD
            | RKPM_SLP_AP_PWROFF
            )
        >;
        rockchip,wakeup-config = <
            (0
            | RKPM_GPIO_WKUP_EN
            )
        >;
    };   
```
` rockchip,sleep-mode-config ` 配置休眠时系统支持哪些低功耗操作，配置对应的功能，休眠时代码就会执行对应的流程;比如 ARMOFF，OSC disabled。
` rockchip,wakeup-config ` 配置休眠时能唤醒系统的唤醒源，休眠时对应的唤醒源能够唤醒系统;比如 GPIO、USB、SD卡 等。
可填充的比如 RKPM_GPIO_WKUP_EN 或者 RKPM_PWM_WKUP_EN。
` rockchip,pwm-regulator-config ` 硬件中有哪一个 PWM 作调压功能，休眠之前就会将这路电压恢复到默认电压。
```
&rockchip_suspend {
    status = "okay";
    rockchip,sleep-debug-en = <1>;
    rockchip,sleep-mode-config = <
        (0
        | RKPM_SLP_ARMPD
        | RKPM_SLP_PERILPPD
        | RKPM_SLP_DDR_RET
        | RKPM_SLP_PLLPD
        | RKPM_SLP_CENTER_PD
        | RKPM_SLP_AP_PWROFF
        )
        >;
    rockchip,wakeup-config = <
        (0
        | RKPM_GPIO_WKUP_EN
        | RKPM_PWM_WKUP_EN
        )
        >;
        rockchip,pwm-regulator-config = <
        (0
        | PWM2_REGULATOR_EN
        )
        >;
        rockchip,power-ctrl =
        <&gpio1 17 GPIO_ACTIVE_HIGH>,
        <&gpio1 14 GPIO_ACTIVE_HIGH>;
};

```


### PWM 的要求
RK3399 有 4 路 PWM，不同的硬件上可能有用到若干路作为调压使用，为保证稳定性需要在休眠前必须设置 PWM 控制的几路电压为默认电压，唤醒恢复。


## 二、Linux 电源管理系统
