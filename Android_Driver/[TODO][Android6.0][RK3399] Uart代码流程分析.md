---
title: [TODO][Android6.0][RK3399] Uart代码流程分析
tags: Rockchip,Uart
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Version: v2016.08

[toc]

## 前言
RockChip 平台的串口分为两种类型，普通串口（Uart） 和 调试串口（Debug Uart）。
我们先分析 普通 Uart 的串口驱动流程。

## Uart 驱动框架

简单而言分为两层。
下层是串口驱动层（Serial_driver），它直接与硬件（Hardware）接触。我们需要填充一个 struct uart_ops 结构体。
上层（tty）包括 tty core 与 line discipline，它们俩各自有一个 ops 结构，User Space 通过 tty 注册的字符设备来访问。


```c
serial_rk_init （rk_serial.c）
——uart_register_driver（serial_core.c）  //注册 serial_rk_reg,.driver_name = "rk_serial", dev_name="ttyS"
————alloc_tty_driver （tty_io.c） //分配 tty_driver，UART_NR个，即8个
————tty_set_operations  //设置 tty_driver->ops ，normal 是 struct tty_driver ×
————tty_port_init //初始化串口
————tty_register_driver //注册uart驱动为一个标准字符设备，name = ttySx
——————alloc_chrdev_region 或者是 register_chrdev_region //注册一组字符设备编号
——————tty_cdev_add //调用 cdev_add 注册字符设备
——————proc_tty_register_driver // 用 proc_create_data 和 seq_file 创建 proc文件
————tty_port_destroy //
————put_tty_driver （tty_io.c）
—— platform_driver_register // 基于 platform 平台设备驱动模型注册 serial_rk_driver
————serial_rk_probe
————of_rk_serial_parse_dt //解析 dts 中的配置
————serial_rk_add_console_port //
————uart_add_one_port //
```
## 驱动流程分析
### 注册串口驱动
分配  struct uart_driver 并且调用 uart_register_driver 注册到 Kernel 当中。
```c
static struct uart_driver serial_rk_reg = {
	.owner			= THIS_MODULE, //拥有 uart_driver 的莫开
	.driver_name		= "rk_serial", //串口驱动名字
	.dev_name		= "ttyS", //串口设备名字
	.major			= TTY_MAJOR, //主设备号 （4）
	.minor			= 64,  //次设备号
	.cons			= SERIAL_CONSOLE, //其对应的console 前提支持serial console,否则为NULL
	.nr			= UART_NR, //该 uart_driver 支持的最大串口个数（8）
};
```
```c
	...
	uart_register_driver(&serial_rk_reg);
	...
```

## 驱动文件分析
serial_core.c 
有 uart_ops 包含了 uart 的操作指令，如 uart_open、uart_close、uart_write 等
通过 tty_set_operations 注册 uart_ops







刚才我们主要分析了 uart_driver 向上注册的过程。
我们在 userspace open 时将调用到 uart_port.ops.startup ，write 时将调用到 ops.start_tx ，这些都是 kernel 已经帮我们完成的。开发时不需要涉及到这些代码的移植。
真正需要触碰的是 uart_port 这个结构体，它真正对应于一个物理的串口。


我们知道在 uboot 启动时串口的各种信息就已经输出出来了，说明串口初始化在很早的时候。
大概函数流程如下：
start_kernel -> setup_arch -> map_io -> init_irq -> timer ->  init_machine -> ...// rk_serial_init

xxx_init 是 是类似于 module_init 等被组织进 Linux 里，放在一个特殊的 Segment，内核启动到一定时候将这个 Segment 中的每个函数取出来去调用，也是与串口相关。

