---
title: [Android6.0][RK3399] IR(红外线)移植步骤
tags: android,ir,rockchip
grammar_cjkRuby: true
---
<h1 style="text-align:center">OrangePi RK3399 IR Porting Guide </h1>

Platform: RK3399 
OS: Android 6.0 
SDK Version: v2016.08

<h4 style="text-align:right">by Xunlong® Younix.Zhang</h1>

[TOC]

## 一、 红外介绍
**IR(Infrared Radiation)**
现有的红外遥控有两种方式，PWM（脉冲宽度调制）和PPM（脉冲位置调制）。
对应的两种编码形式的代表分别为NEC和PHILIPS的RC-5、RC-6、RC-7
**Linux 内核中，IR 驱动仅支持 NEC 编码格式。**

## 二、 驱动移植与验证
### 1. 修改 dts 打开 pwm
kernel/arch/arm64/boot/dts/rockchip/rk3399-sapphire-excavator-edp.dts
根据原理图 

![](http://ww1.sinaimg.cn/large/ba061518gy1febxt5701kj20ie00sjre.jpg)

可以看到红外部分采用的是 pwm3。
所以在 dts 中我们进行如下配置：
```dts
&pwm3 {
	status = "okay";
	interrupts = <GIC_SPI 61 IRQ_TYPE_LEVEL_HIGH 0>;
	compatible = "rockchip,remotectl-pwm";
	remote_pwm_id = <3>;
	handle_cpu_id = <0>;
  
  ir_key1 {
    rockchip,usercode = <0xfb04>;
    rockchip,key_table =
      <0xa3	KEY_ENTER>,
	  <0xe4 388>,
      <0xf5	KEY_BACK>,
      <0xbb	KEY_UP>,
      <0xe2	KEY_DOWN>,
      <0xe3	KEY_LEFT>,
      <0xb7	KEY_RIGHT>,
      <0xe0	KEY_HOME>,
      <0xba	KEY_VOLUMEUP>,
      <0xda	KEY_VOLUMEUP>,
      <0xe6	KEY_VOLUMEDOWN>,
      <0xdb	KEY_VOLUMEDOWN>,
      <0xbc	KEY_SEARCH>, 
      <0xb2	KEY_POWER>,
      <0xe5 KEY_POWER>,
      <0xde KEY_POWER>,
      <0xdc	KEY_MUTE>,
      <0xa2	KEY_MENU>,
      <0xec	KEY_1>,
      <0xef	KEY_2>,
      <0xee	KEY_3>,
      <0xf0	KEY_4>,
      <0xf3	KEY_5>,
      <0xf2	KEY_6>,
      <0xf4	KEY_7>,
      <0xf7	KEY_8>,
      <0xf6	KEY_9>,
      <0xb8	KEY_0>;
  };
};
```
`status = "okay";` 表示打开 pwm3
`interrupts` 是中断号
`compatible = "rockchip,remotectl-pwm";` linux 平台上默认的 IR 驱动为 drivers/input/remotectl/rockchip_pwm_remotectl.c ，这里会对应去匹配 driver。
`remote_pwm_id = <3>;` pwm我们采用的是第三组。
`handle_cpu_id = <0>;`

ir_key1 为键值表，第一列是键值，第二列是响应的按码键。其中的值在最初可以不用填。后面第 3 小节后我们根据遥控器确定按键后再来修改。

### 2. 检查是否加载 IR 驱动
驱动代码在 drivers/input/remotectl/rockchip_pwm_remotectl.c 
出现如下 log 表示 IR 驱动正常加载。
```
[    0.656437] .. rk pwm remotectl v1.1 init
[    0.656672] input: ff420030.pwm as /devices/platform/ff420030.pwm/input/input0
```
根据 log 中 ff420030，我们后面（第三节）也可以找到 system/usr/keylayout/ff420030_pwm.kl 文件，这个文件用于将 Linux 层获取的键值映射到 Android 上对应的键值。

### 3. 获取 USERCODE 和 KEY 值
先通过以下命令使能 DBG_CODE 打印：
```
echo 1 > /sys/module/rockchip_pwm_remotectl/parameters/code_print
```
按遥控上的任意按键，可以看到类似如下信息：

![](http://ww1.sinaimg.cn/large/ba061518gy1febwrfy63bj208v04baap.jpg)

USERCODE 这个遥控的 usercode，用以标识遥控种类。
RMC_GETDATA 表示键值。
我的遥控是这样子的，左边是我依次按键后根据 log 画出来遥控对应的键值。

![](http://ww1.sinaimg.cn/large/ba061518gy1febww3azalj20qo0zkdhq.jpg)

### 4. 修改 dts 的 ir_key map
添加如下信息
```
  ir_key1 {
    rockchip,usercode = <0xfb04>;
    rockchip,key_table =
      <0xa3	KEY_ENTER>,
	  <0xe4 388>,
      <0xf5	KEY_BACK>,
      <0xbb	KEY_UP>,
      <0xe2	KEY_DOWN>,
      <0xe3	KEY_LEFT>,
      <0xb7	KEY_RIGHT>,
      <0xe0	KEY_HOME>,
      <0xba	KEY_VOLUMEUP>,
      <0xda	KEY_VOLUMEUP>,
      <0xe6	KEY_VOLUMEDOWN>,
      <0xdb	KEY_VOLUMEDOWN>,
      <0xbc	KEY_SEARCH>, 
      <0xb2	KEY_POWER>,
      <0xe5 KEY_POWER>,
      <0xde KEY_POWER>,
      <0xdc	KEY_MUTE>,
      <0xa2	KEY_MENU>,
      <0xec	KEY_1>,
      <0xef	KEY_2>,
      <0xee	KEY_3>,
      <0xf0	KEY_4>,
      <0xf3	KEY_5>,
      <0xf2	KEY_6>,
      <0xf4	KEY_7>,
      <0xf7	KEY_8>,
      <0xf6	KEY_9>,
      <0xb8	KEY_0>;
  };
};
```
### 5. 配置编译驱动选项
RK3399 平台默认配置有 IR 部分。
其他 Android 平台没有的需要添加。
1. 配置文件 drivers/input/remotectl/Kconfig 添加

```
config ROCKCHIP_REMOTECTL_PWM
	bool "rockchip remoctrl pwm capture"
	default n
```

![](http://ww1.sinaimg.cn/large/ba061518gy1febx3iryoqj20d503t0sx.jpg)

2. 修改 drivers/input/remotectl 路径下的 Makefile，增加如下编译选项
```
obj-$(CONFIG_ROCKCHIP_REMOTECTL_PWM)	+= rockchip_pwm_remotectl.o
```

3.  在 kernel 路径中 make menuconfig，添加 IR 驱动
```menuconfig
Device Drivers
    -> Input device support
        ->[*]rockchip remotectl
		        [*]rockchip remoctrl pwm capture
```

![](http://ww1.sinaimg.cn/large/ba061518gy1febx88xrflj20k60akdh3.jpg)

### 6. 编译并烧录固件
在 kernel 下
```
make -j4 rk3399-sapphire-excavator-edp.img
```
烧录 kernel.img 和 resource.img

### 7. 验证结果
按照 3 中的方式打开 DBG Log
依次按键，看是否能实现相应功能。
如果有问题，查看打印中 RMC_GETDATA   的值是否和 dts 中对应。

## 三、 Android 键值映射
生成的 out/target/product/rk3399/system/usr/keylayout/ff420030_pwm.kl 文件用于将 Linux 层获取的键值映射到 Android 上对应的键值。
我们可以添加或者修改该文件的内容以实现不同的键值映射。
adb pull 后修改再 adb push 进去可以实现修改键值映射。

比如我在 Android 部分实现了 键盘鼠标切换功能。
那么我可以在 ff420030_pwm.kl 中添加
```
 key 388   TV_KEYMOUSE_MODE_SWITCH
```
我要将 e4 按键设置为这个功能键，那么我就可以在 dts 中添加
```
	  <0xe4 388>,
```

