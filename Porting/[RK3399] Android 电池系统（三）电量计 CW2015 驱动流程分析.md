---
title: [RK3399] Android 电池系统（三）电量计 CW2015 驱动流程分析
tags:charger,android,rockchip
grammar_cjkRuby: true
---


## 已知问题
cw2015 的代码默认是 rk3288 平台的，3399 平台有一些接口已经升级。
所以默认编译是无法通过的。
所以当前的问题是进行代码的修改以适用于当前 3399 平台。
磨刀不误砍柴工，我们先磨好刀，下一章再开始砍柴。

## 驱动分析
我在驱动中添加了 cw_init_power_supply 和 cw_turn_on_bq_hw_init。
在前者里面完成了 power_supply 设备的注册（利用升级后的 register_power_supply 接口）
在后者中完成了电池状态的检测，并传给 bq25700_charger IC。

### 函数调用链
```
cw_bat_probe
  cw2015_parse_dt  // 解析 dts。
                   // 包括 bat_config_info、dc_det_gpio、bat_low_gpio、chg_ok_gpio
                   // chg_mode_sel_gpio、
                   // is_dc_charge 是否支持 dc 充电
                   // is_usb_charge 是否支持 usb 充电
  cw_bat_gpio_init // 申请 GPIO 并分配 dc_det_gpio、bat_low_gpio、chg_ok_gpio 为 input
                   // 分配 chg_mode_sel_gpio 为 output
  cw_init          // 初始化 cw2015 的寄存器。
                   // 设置工作模式，如果是 SLEEP MODE 就将其唤醒进入 NORMAL MODE;
                   // 设置警报寄存器 ATHD;
                   // 更新还未设置的寄存器信息
  cw_init_power_supply // 注册 power_supply 设备（三种 battery、usb、ac）
  cw_update_time_member_capacity_change  // 更新到现在开始充电系统启动的用时，以及到现在为止系统休眠了多长时间
  cw_update_time_member_charge_start // 更新到现在电量改变系统启动的用时，以及到现在为止系统休眠了多长时间
  battery_workqueue = create_singlethread_workqueue // 创建单线程工作队列 rk_battery
  INIT_DELAYED_WORK // 初始化 cw_bat_work 绑定到 battery_delay_work
    cw_bat_work     // 不断更新电池信息
       rk_ac_update_online // 更新 DC 状态
       power_supply_changed(cw_bat->rk_ac) //
       rk_usb_update_online // 更新 usb 状态
       power_supply_changed(cw_bat->rk_usb)
  INIT_DELAYED_WORK // 初始化 dc_detect_do_wakeup 绑定到 dc_wakeup_work
    dc_detect_do_wakeup // 获取 dc_det irq 号，根据现在中断状态来设置下一次中断的触发条件
  cw_turn_on_bq_hw_init // 获取 VCELL Voltage 并且传递标志位给 BQ IC 的驱动，用以决定是否配置 BQ IC
```
