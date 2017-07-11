---
title: [TODO][Android6.0][RK3399] RK 平台 Sensor-dev 框架脉络梳理
tags: sensor,rockchip
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 
IC: MPU6500

## sensor dev probe 
1. i2c_check_functionality 校验是否是 I2C 设备
2. 需要有其 device tree
3. 分配 pdata 内存空间
4. 解析 DTS。设备类型、GPIO、中断使能、数据范围、layout 贴片方式。
5. 初始化等待队列 data_ready_wq
6. 初始化互斥锁
7. 初始化等待队列　flags.open_wq
8. 初始化 sensor  sensor_chip_init。
8.1 sensor_get_id 获取 chip id
8.2 sensor_initial 调用 sensor 设备自己的 ops->init
9. 分配 input 设备空间
10. 根据不同的设备类型进行不同的　input_set_abs_params
11. 注册 input 设备，input_register_device
12. 初始化 sensor irq
13. 注册 misc device
14. 如果 dts 设置了为 factory 模式，且是 GSensor 就为其初始化 Class 子系统

## sensor_type.c
在 sensor_dev.c 中我们看到会操作 ops-> 下的一些回调函数
在 sensor 各自的 .c 中这些回调函数被实现并被挂到 ops 上
其中实现的 ops 包括：
1. sensor_init 完成 config 寄存器的写操作 最后执行 sensor_active
2. sensor_active 完成特定寄存器的写操作
3. sensor_report_value 完成寄存器的读操作，最后上报 input_report
4. 配置一些其他的寄存器信息。比如 id、precision、status reg 等。
