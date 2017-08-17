---
title: [Android6.0][RK3399] Mipi LCD 通用移植调试流程
tags: mipi,lcd,rockchip,android
grammar_cjkRuby: true
---

[TOC]

## 前言
其实之前有写过一篇关于 =[RK3288 平台 LCD 调试][1]流程的博客 。不过是 RK3288 Android5.1 平台的。
虽然实际上 Mipi 部分代码实在是大同小异。但是距上次那篇文章到现在也已经不知不觉整整一年了，这一年 Mipi LCD 确实也调了不少。
索性再次重新梳理一下，也许会有别样的收获吧。
没有看过那篇文章的同学也不需要再看了，这篇文章会更加全面的描述和分析调试流程。
这次文章以 RM72014 这颗 Driver IC 为例，从 RK Mipi LCD 代码分析 到 屏的公式计算 再到实践中的问题都会涉及，**调试为主，分析为辅**，比较冗长，大家可以挑选自己需要的部分来看。

## 一、扣出屏 datasheet 中的关键信息
首先我们要找屏厂索取详细版的屏的规格书，扣出其中的关键信息。
屏 Spec 的目录大概如下：

![](http://ww1.sinaimg.cn/large/ba061518gy1fimsb8phzuj20ja0ip0v3.jpg)

其中我们最需要关注的是
**General Specification**
**Power on/off sequence** 上电下电时序
**Timing** 屏参

### 1. General Specification

![](http://ww1.sinaimg.cn/large/ba061518gy1fimsg46oifj20je0mgtb4.jpg)

提炼出来关键信息是 
Hactive  = 800 ，水平分辨率
Vactive = 1280 ，垂直分辨率
Lanes = 4 ，Mipi data 信号线通道数

### 2. Power on/off sequence

![](http://ww1.sinaimg.cn/large/ba061518gy1fimsjacg20j20jk0h70u5.jpg)

这个在屏点不亮的时候需要首先确认，这个我们后面会说。
我们在调屏的时候可以先把这个截图保存到自己的笔记中，就不需要每次都去翻 datasheet 了。

### 3. Timing

![](http://ww1.sinaimg.cn/large/ba061518gy1fimskfj44mj20hp0cm799.jpg)

关键信息提炼出来：
Hactive = 800
HFP = 24
HBP = 132
Hsync = 4

Vactive = 1280
VFP = 8
VBP = 8
VSync = 4

Pixel Clock Frequency（Pclk）= 74.88MHZ

这里我们详细说一下各个参数的含义，这个对我们后续调屏会非常有帮助。
另外根据以上的信息，我们还能计算出 Mipi Dsi Clock 。
**DCLK**  = 100 + H_total×V_total × fps × 3 × 8 / lanes_nums
**total** 这里指的是 sync + front + back + active
比如 H_total = Hsync + HFP(hfront-proch)  + HBP(hback-porch) + Hactive
**fps** 指的是帧率，一般我们按照 60 帧来计算
**3 × 8** 代表一个 RGB 为 3 个字节，每个字节 8 bit
**lanes** 代表 mipi data 通道数

所以对于我这个屏 
DCLK 
= 100Mbps + H_Total × V_Total x fps x 3 x 8 / lanes_nums 
= 100 + ( 800 + 21 + 132 + 4 ) x ( 1280 + 8 + 8 + 4 ) x 60 帧 x 3 字节 x 8 bit / 4 lanes
= 100Mbps + 449Mbps = 549 Mbps

重点看下面这张图，

![](http://ww1.sinaimg.cn/large/ba061518gy1fimt123xehj20s10ggjrn.jpg)

## 二、根据屏参 和 硬件设计填写 dts

RK LCD 这部分的去耦合性已经做的很好了。
我们仅仅只需要填写 dts ，驱动会自动解析 dts ，
管脚控制部分会自动申请分配操纵 GPIO，屏初始化代码（init cmds）和屏参（timing）将被自动封装成 mipi dsi 命令进行发送。

### 2.1 创建屏的 dtsi 文件

仿造平台的其他 lcd-\*-mipi.dtsi 编写 lcd-xxx-mipi.dtsi 后 需要在 主 dts 文件中包含这个 dtsi。
```
&rk_screen {
  /* 8inch LCD Mipi */
  #include <dt-bindings/display/screen-timing/lcd-mipi-rm72014.dtsi>
};
```
根据前面我们获取到的屏参信息开始编写 dtsi

#### 2.1.1 Mipi Host
```
## MIPI Host配置
disp_mipi_init: mipi_dsi_init{
        compatible = "rockchip,mipi_dsi_init";

        /* 是否要在 dtsi 中初始化 1 是 0 否 */
        rockchip,screen_init    = <1>;

        /* 要几条数据 lane*/
        rockchip,dsi_lane       = <4>;

        /* ddr clk 一条 lane 的传输速率 Mbits/s */
		/* 前面我们已经算得为 549 */
        rockchip,dsi_hs_clk     = <549>;

        /* 单mipi 还是双 mipi*/
        rockchip,mipi_dsi_num   = <1>;
};
```
#### 2.1.2 Timing 

```
disp_timings: display-timings {
        native-mode = <&timing0>;
        compatible = "rockchip,display-timings";
        timing0: timing0 {
            screen-type = <SCREEN_MIPI>;     //单mipi SCREEN_MIPI 双mipi SCREEN_DUAL_MIPI
            lvds-format = <LVDS_8BIT_2>;     //不用配置
            out-face    = <OUT_P888>;        //屏的接线格式 
            								 //配置颜色，可为OUT_P888（24位）、OUT_P666（18位）或者OUT_P565（16位）
            clock-frequency = <74488000>;   //dclk频率，看规格书，或者 H×V×fps
            hactive = <800>;                 //水平有效像素
            vactive = <1280>;                //垂直有效像素
            hback-porch = <132>;              //水平同步信号 后肩
            hfront-porch = <24>;              //水平同步信号 前肩
            vback-porch = <8>;
            vfront-porch = <8>;            
            hsync-len = <4>;                //水平同步信号
            vsync-len = <4>;
            hsync-active = <0>;              //hync 极性控制 置 1 反转极性
            vsync-active = <0>;
            de-active = <0>;                 //DEN 极性控制
            pixelclk-active = <0>;           //dclk 极性控制
            swap-rb = <0>;                   //设 1 反转颜色 red 和 blue
            swap-rg = <0>;
            swap-gb = <0>;
	};
};
```

#### 2.1.3 init cmds

屏场给的初始化时序往往不会是 RK 平台的。我们可能需要自己转换一下。
不过一般也很好理解，我们分别分析两组平台的例子：

##### **展讯平台**：

```
GP_COMMAD_PA(02);SPI_WriteData(0x53);SPI_WriteData(0x24);
GP_COMMAD_PA(03);SPI_WriteData(0xf0);SPI_WriteData(0x5a);SPI_WriteData(0x5a); Delay_ms(30);
GP_COMMAD_PA(01);SPI_WriteData(0x11); Delay_ms(100);
GP_COMMAD_PA(01);SPI_WriteData(0x29); Delay_ms(30);
GP_COMMAD_PA(04);SPI_WriteData(0xc3);SPI_WriteData(0x40);SPI_WriteData(0x00);SPI_WriteData(0x28);
GP_COMMAD_PA(02);SPI_WriteData(0x50);SPI_WriteData(0x77);
GP_COMMAD_PA(02);SPI_WriteData(0xe1);SPI_WriteData(0x66);
GP_COMMAD_PA(02);SPI_WriteData(0xdc);SPI_WriteData(0x67);
GP_COMMAD_PA(02);SPI_WriteData(0xd3);SPI_WriteData(0xc8);
GP_COMMAD_PA(02);SPI_WriteData(0x50);SPI_WriteData(0x00);
GP_COMMAD_PA(02);SPI_WriteData(0xf0);SPI_WriteData(0x5a);
GP_COMMAD_PA(02);SPI_WriteData(0xf5);SPI_WriteData(0x80);
Delay(120);
```
GP_COMMAD_PA 表示 dsi packets 的个数
SPI_WriteData 接口用来写数据
Delay_ms 表示延时 xx 毫秒
所以
`GP_COMMAD_PA(02);SPI_WriteData(0x53);SPI_WriteData(0x24); ` 
表示给屏 0x53 指令，有**一个**指令参数，为 0x24
`GP_COMMAD_PA(03);SPI_WriteData(0xf0);SPI_WriteData(0x5a);SPI_WriteData(0x5a); Delay_ms(30);`
表示给屏 0xf0 指令，有**两个**指令参数 0x5a 和 0x5a ，并且延时 30ms
`GP_COMMAD_PA(01);SPI_WriteData(0x11); Delay_ms(100);`
表示给屏 0x11 指令，**没有**指令参数，并且延时 100ms
`GP_COMMAD_PA(01);SPI_WriteData(0x29); Delay_ms(30);`
表示给屏 0x29 指令，**没有**指令参数，并且延时 30ms

后面同理。

细心的同学发现了我这里强调了指令参数的个数。
因为这涉及到了 dsi 协议中 dsi 传输的数据类型。
根据 《MIPI-DSI-specification-v1-1.pdf》49 页我们可以看到，有如下这些数据类型。

我们只需要关注 0x05 ，0x15，0x39，他们分别对应的 dsi 参数类型是 无参指令（Short No parameters）、单参数指令（Short 1 parameter）、多参数指令（Long Command Packets）。

![](http://ww1.sinaimg.cn/large/ba061518gy1fimx9n2o10j20jh0lj40y.jpg)

##### **MTK 平台**
```
data_array[0]=0x00043902;
data_array[1]=0x8983FFB9; 
dsi_set_cmdq(&data_array, 2, 1); 
MDELAY(10);
```
分析得知 
array[0] 中 04 代表要传输的字节数，3902 代表传输的是多参指令
//MTK平台 3900 代表无参 3905 表示单参 3902 表示多参
array[1] 中的参数全部为传输的参数，而且正确的传参数据是倒着的 B9 FF 83 89 
所以移植到 RK 平台应该是 
```
rockchip,on-cmds1 {
                            compatible = "rockchip,on-cmds";
                            rockchip,cmd_type = <LPDT>;
                            rockchip,dsi_id = <0>;
                            rockchip,cmd = <0x39 0xB9 0xFF 0x83 0x89>;
                            //0x39 为 DSI 数据类型、  0xB9 为LCD 命令、后面为参数
                            rockchip,cmd_delay = <10>;
}
```

##### ** Mipi DSI 协议中 Generic 和 DCS 的区别**

另外，值得一提的是。在上面 Mipi 的 Spec 中，大家可以看到 0x29 和 0x39 都可以表示多参，0x03 和 0x05 都可以表示无参，0x13 和 0x15 都可以表示单参。但他们不是没有区别的。

**DSI 协议中 ，0x29 和 0x39 区别**：在 Mipi 协议中，它俩都表示 长包（Long Packet）数据类型。 
但是 Mipi DSI 的 Spec 中写着两者的区别 0x29 属于 Generic long write ，0x39 属于 DCS long write。 
**DCS 系**的读写命令，可带参数，常用于 LCD 初始化参数命令。 
**Generic 系**读写命令，是协议规范外的命令，通常是一些 IC 定制的，只要确保主机和外设同意这些数据格式即可，通常和 DCS 通用。


##### **RK 平台**
上述两个例子举完了。我们继续写 RK 平台 RM72014 的 inital cmds：

对应的 inital cmds
```
 disp_mipi_init_cmds: screen-on-cmds {
 	rockchip,cmd_debug = <0>;
 	compatible = "rockchip,screen-on-cmds";
 	rockchip,on-cmds1 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0x53 0x24>;
 		rockchip,cmd_delay = <0>;
 	};

 	rockchip,on-cmds2 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x39 0xf0 0x5a 0x5a>;
 		rockchip,cmd_delay = <30>;
 	};

 	rockchip,on-cmds3 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x05 0x11>;
 		rockchip,cmd_delay = <100>;
 	};

  rockchip,on-cmds4 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x05 0x29>;
 		rockchip,cmd_delay = <30>;
 	};

//... 

  rockchip,on-cmds11 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0xf0 0x5a>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds12 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0xf5 0x80>;
 		rockchip,cmd_delay = <120>;
 	};

```
**cmd_type** 表示 dsi 传输类型，分为 HSDT 高速（Video 模式） 和 LPDT 低速（command 模式）
**dsi_id** 表示通过哪一组 mipi 发送。0 表示第一组 Mipi ，2 表示两组同时发。1 表示第二组 Mipi，但是一般不会出现只用第二组的情况，所以不会是 1 。


 ### 2.2 硬件管脚 GPIO 配置
 
 有两种方式控制屏相关的 GPIO，一种是在屏 dtsi 中配置，一种是交由 vop 进行控制。
  
 前者的例子如下，比如可以在 dtsi 中完成电源控制配置
 ```c
 ## 屏电源控制配置
disp_mipi_power_ctr: mipi_power_ctr {
        compatible = "rockchip,mipi_power_ctr";
        mipi_lcd_rst:mipi_lcd_rst{
                compatible = "rockchip,lcd_rst";
                rockchip,gpios = <&gpio4 GPIO_D6 GPIO_ACTIVE_HIGH>;
                rockchip,delay = <10>;
        };
        
        // 配置 lcd_en GPIO 哪一路 ，有可能没有 LCD_EN 那么就是 VCC 常供电
        mipi_lcd_en:mipi_lcd_en {
                compatible = "rockchip,lcd_en";
                rockchip,gpios = <&gpio1 GPIO_B5 GPIO_ACTIVE_HIGH>;
                rockchip,delay = <10>;
        };
        
        //还可能有片选 cs
};
 ```
也可以交由 vop 控制，比如这样：
```c
&vopl_rk_fb {
	status = "okay";
  rockchip,prop = <PRMRY>;
  assigned-clocks = <&cru DCLK_VOP1_DIV>;
  assigned-clock-parents = <&cru PLL_CPLL>;
	power_ctr: power_ctr {
		rockchip,debug = <0>;
		lcd_en: lcd-en {
			rockchip,power_type = <GPIO>;
			gpios = <&gpio1 GPIO_B5 GPIO_ACTIVE_HIGH>;
			rockchip,delay = <10>;
		};
		lcd_rst: lcd-rst {
			rockchip,power_type = <GPIO>;
			gpios = <&gpio4 GPIO_D6 GPIO_ACTIVE_HIGH>;
			rockchip,delay = <10>;
		};
	};
};
```
GPIO_A / B C 的定义在 kernel/arch/arm64/boot/dts/include/dt-binding/pinctl/rk.h 中
delay 需要根据上面的时序图进行设置，一般 10ms 可以适配大部分的屏幕了。
这里的 rockchip,gpios 我们根据硬件进行配置：

![](http://ww1.sinaimg.cn/large/ba061518gy1fhey171zzuj20c00jbwfr.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gy1fheygh9086j20jl012weg.jpg)
```
 		rockchip,gpios = <&gpio4 30 GPIO_ACTIVE_HIGH>;  // GPIO4_D6
```
![](http://ww1.sinaimg.cn/large/ba061518gy1fheyeyrrc8j20gx00swef.jpg)
```
 		rockchip,gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>; //GPIO1_B5
 ```
 

## 三、背光 Backlight
背光常用的有三种情况：
一是 常开。
二是 背光 IC 使能后，输入 PWM 信号调光。
三是 背光 IC 使能后，通过 FB 获得反馈自动进行调光。

比如我曾用到一颗 背光 IC 是这样的：

![enter description here][2]

![enter description here][3]


我们了解到 EN 拉高时背光使能，拉低时背光禁能; FB 接受反馈信号，动态控制背光亮度。

根据相关的原理图 

![enter description here][4]
![enter description here][5]

BL_EN 是普通的 GPIO ，LCDC_BL 是支持 PWM 输出的管脚，所以得知我们硬件采用的是第二种调光方式

完成 dts 中 backlight 相关的配置
```
backlight {
        compatible = "pwm-backlight";
        pwms = <&pwm0 0 25000>;     //在这里配置采用的是 pwm0 还是 pwm1
        brightness-levels = <255 254 253 252 251 250 249 248 247 246 245 244 243 242 241 240
             239 238 237 236 235 234 233 232 231 230 229 228 227 226 225 224 223 222 221 220
             219 218 217 216 215 214 213 212 211 210 209 208 207 206 205 204 203 202 201 200
             199 198 197 196 195 194 193 192 191 190 189 188 187 186 185 184 183 182 181 180
             179 178 177 176 175 174 173 172 171 170 169 168 167 166 165 164 163 162 161 160
             159 158 157 156 155 154 153 152 151 150 149 148 147 146 145 144 143 142 141 140
             139 138 137 136 135 134 133 132 131 130 129 128 127 126 125 124 123 122 121 120
             119 118 117 116 115 114 113 112 111 110 109 108 107 106 105 104 103 102 101 100
             99 98 97 96 95 94 93 92 91 90 89 88 87 86 85 84 83 82 81 80 79 78 77 76 75 74 73 72 71 70
             69 68 67 66 65 64 63 62 61 60 59 58 57 56 55 54 53 52 51 50 49 48 47 46 45 44 43 42 41 40
             39 38 37 36 35 34 33 32 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10
             9 8 7 6 5 4 3 2 1 0>;
        default-brightness-level = <200>;
        enable-gpios = <&gpio7 GPIO_A2 GPIO_ACTIVE_HIGH>;   //BL_EN 背光使能管脚
    };
```

## 四、确认驱动代码和 vop/lcdc 通道打开

make menuconfig 确认一下三个宏打开

![enter description here][6]


dts 中确认
```
## RK3399 平台
&mipi0_rk_fb {
  status = "disabled";
};

## RK3288 平台
&dsi_host {
  status = "disabled";
};
```
## 四、调试流程






## 五、RK 平台 LCD 原理简述

### 4.1 rk 遵循标准 frame buffer driver
rk 的 fb 是遵循了 linux frame buffer 驱动拓展的 fb driver，所以 rk fb 的应用开发基本和标准的 linux frame buffer 应用开发是相同的。
RK 系列主控的 LCDC 在内部是分层的，每一层叫做 win，每一层可以在屏幕上任意位置显示任意大小的图像。并且各层可以通过 Alpha Blending（Alpha混合） 或者 Color Key 实现 overlay 合成输出。
RK3399 的 LCDC 有 3 层 win。win0、win1 支持 RGB 和 YUV 格式，win2 支持 YUV 格式。

在 rk fb 中，每一层 win 对应一个 fb 设备，他们在 linux 系统中对应的设备节点为 ` /dev/graphics/fb* `。
对应关系可以通过下面命令查询：
```
cat /sys/class/graphics/fb0/map
fb0:win0
fb1:win1
fb2:win2
```


  [1]: http://blog.csdn.net/dearsq/article/details/52354593
  [2]: http://ww4.sinaimg.cn/large/ba061518gw1f75tvya4xlj20t90bf0zo.jpg
  [3]: http://ww2.sinaimg.cn/large/ba061518gw1f75tu7eik2j20930dfwfw.jpg
  [4]: http://ww4.sinaimg.cn/large/ba061518gw1f75u6elg5wj20na0cudi8.jpg
  [5]: http://ww3.sinaimg.cn/large/ba061518gw1f75u78v1czj20c703uwfg.jpg
  [6]: http://ww2.sinaimg.cn/large/ba061518gw1f75ubbrqosj20c703275b.jpg