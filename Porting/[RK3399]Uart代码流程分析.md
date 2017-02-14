---
title: [RK3399]普通Uart代码流程分析
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

## 驱动流程分析
```
static struct uart_driver serial_rk_reg = {
	.owner			= THIS_MODULE,
	.driver_name		= "rk_serial",
	.dev_name		= "ttyS",
	.major			= TTY_MAJOR,
	.minor			= 64,
	.cons			= SERIAL_CONSOLE,
	.nr			= UART_NR,
};
```

```
static struct platform_driver serial_rk_driver = {
	.probe		= serial_rk_probe,
	.remove		= serial_rk_remove,
	.suspend	= serial_rk_suspend,
	.resume		= serial_rk_resume,
	.driver		= {
		.name	= "serial",
#ifdef CONFIG_OF
		.of_match_table	= of_rk_serial_match,
#endif
		.owner	= THIS_MODULE,
	},
};
```

serial_rk_init （rk_serial.c）
——uart_register_driver(&serial_rk_reg)    //注册 serial_rk_reg,.driver_name = "rk_serial", dev_name="ttyS"
————
————
——platform_driver_register(&serial_rk_driver)  //注册 driver