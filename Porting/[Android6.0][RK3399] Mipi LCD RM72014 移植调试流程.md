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

本文地址：http://blog.csdn.net/dearsq/article/details/77341120
作者 Younix，欢迎转载，转载请著名出处，谢谢。

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
//MIPI Host配置
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
//	 RK3399 平台
	&mipi0_rk_fb {
	  status = "disabled";
	};

// RK3288 平台
	&dsi_host {
	  status = "disabled";
	};
```

## 五、调试流程
一般按照上面的顺序，编译，烧录后。
幸运的话，屏就可以点亮（有东西显示）了。

但是这个世界对长的帅的人就是如此不公平。
至少我从来没有一次就直接点亮过。

下面我们开始进入调试阶段。

### 5.1 检查电压
检查原理图上各个供电管脚的电压
VCC 、VCC IO 是否正常。
VCC IO 是给 GPIO 供电用，比如 RST。有的屏会兼容 3.3V 和 1.8 V 的 IO 电平，但是大部分不会。
VCC_LCDA 、VCC_LCDK 电压是否满足要求。

确认电压正常后，关机，上屏，结合 开机 Log 看屏部分是否正常初始化。

### 5.2 背光是否正常
背光没亮的话确认一下接上屏的时候，量一量 VDD_LCDA 的电压为多少（串联电路大概能到 20V+） 
没有就去检查背光电路供电电压和 backlight 相关的配置（比如背光功能使能的 GPIO 有没有控制到、PWM通道是否配置正确）。

### 5.3 framebuffer 是否有数据产生
3368/3399 的命令为
```
echo bmp > sys/class/graphics/fb0/dump_buf 
或者
echo bin > sys/class/graphics/fb0/dump_buf
```

312x 的命令为 
```
cat /dev/graphics/fb0 > /data/fb0.yuv
```
将生成的文件 adb pull 出来后可以通过图片查看软件,譬如 7YUV 读取输出的 bmp 文件或者 bin 文件。
如果有软件能正常显示画面，说明是 mipi 的问题。
如果软件不能正常显示画面,说明 fb 刷下来的数据有问题

### 5.4 打印 Mipi LCD 相关 Log 信息
打开 Mipi DBG 的接口
```
driver/video/rockchip/transmitter/rk32_mipi_dsi.c 中的:
	#define MIPI_DBG(x...) printk(KERN_INFO x)

driver/video/rockchip/screen/lcd_mipi.c 中的:
	#define MIPI_SCREEN_DBG(x...) printk(KERN_ERR x)
```
看看 log 中是否有异常。
譬如 probe 函数是否正常;
是否有调用到 rk32_dsi_enable() 函数,该函数为 lcdc 调用 mipi 的入口函数;
初始化 mipi 的过程中是否有报错等等

电源控制部分对应的操作函数:driver/video/rockchip/screen/lcd_mipi.c 的
rk_mipi_screen_pwr_enable(),rk_mipi_screen_pwr_disable()。

### 5.5 上电时序是否正常
根据前面我们从 datasheet 中扣出来的上电时序图，确认上电时序是否正常，VCC、RST、MIPI 顺序是否正常。
1. VCC 使能有没有起作用。
2. RST 是否有一个 低-高 的变化，没有则是 rst 设置的触发方式可能反了 
3. 在 RST 变高后会开始传输数据，量 lanes 是否有数据输出。抓取数据需要一定规格的示波器和差分探头，我们用普通的示波器大致看看有没有数据输出就够了。

如果到这篇文章中的所有办法都用完了还没有点亮，只能来这里重新测 data 和 clk 波形是否正常。
如果也正常,那就需要确认 mipi phy 是否把初始化命令正确发送出来。用差分探头在单端模式下抓 mipi phy 的 lane0N 和 lane0P。
命令也是正常的，屏依旧还没有点亮，只能进一步分析 mipi 协议了。

### 5.6 clock 是否正常
用示波器量波形看 DCLK 的频率为多少，是否为 dsi_hs_clk 中设置的（可能实际的会略低一点）。
实际的 DCLK 是否满足屏的要求。

### 5.7 可以显示了但是 花屏/闪屏/抖动 等
见后面的问题集锦

## 六、问题集锦

RK 的官方文档中描述了不少问题，我这边就不再赘述了。
以下是我碰到的一些问题的解决办法，还有一些从网上搜到的发挥了作用的解决办法，一并都附在这里了。

### 6.1 RST 复位不正常
我们 RST 是低电平有效，所以我想当然的将 RST 设置为
ACTIVE_LOW。

我在调试的时候发现 lane 一直为低电平，没有数据传输，然后采取量 RST 发现唤醒屏后待到屏幕快灭了 RST 才会被拉高。跟代码发现 RK 平台的实现是

```
！你设置的触发电平
你设置的触发电平
```
我设置的触发电平是 低电平有效 ACTIVE_LOW 
即
```
！ACTIVE_LOW
ACTIVE_LOW
```
即先高再低。
所以是错的，改为 ACTIVE_HIGH 后正常。 

但是虽然填的是 ACTIVE_HIGH ，但是根据驱动应该还是属于低电平有效的，这里是 RK 平台 driver 的实现有问题。 
修改后 lane 有数据传递了。

### 6.2 有数据传输，但是 cmds 有问题
cmds 有的参数超过了 32个字节（有个有36个字节，有个有39个字节），完成 dtsi 中 cmds 编写后 
烧录，板子跑飞，空指针异常。 
发现传递 这个超长 参数的时候有内存溢出情况。 
于是跟代码发现 dcs_cmd.cmds 的数据类型为 int cmds[32]，所以擅自想当然的将包拆成了 39 = 28+11，还将其中的延时设置为 0 。 
这样当然是不行的。但是一切都是基于这个拆了包的 cmds 来调，走了不少弯路。 

于是去联系原厂的工程师，说平台参数大小有限制，咨询拆包是否可行。
他们说可以直接修改 cmds 数组大小，将 cmds[32] 改成了 cmds[400] 。 

这个问题在 RK 后来的 kernel 中被更新了。

所以有时候碰到问题需要确认一下 kernel 是不是最新的，也许会有意想不到的效果。

### 6.3 开机 Logo 闪烁，且水平方向向右偏移压缩了半个屏幕
在点亮屏后刚开始有开机 logo 闪烁，向右偏移了近半个屏幕的长度。
重新确认 clock-frequence 后发现少打了一个 0 。 
修改后解决了 闪烁，大偏移 的问题。

### 6.4 偏移巨大
如下面这张图，偏移的特别多，可能是 dclk 有问题，修改 dsi_hs_clk 由 504 降到 496 解决。

![enter description here][7]

比如下面这张图，也是偏移的很多，将 dclk 增加解决。

![](http://ww1.sinaimg.cn/large/ba061518gy1fimzp6hrxmj20qo0zkjt1.jpg)

### 6.5 偏移一点点
如下图，一般修改 HBP、HFP、VBP、VFP 即可。

![enter description here][8]


### 6.6 水平方向似乎被裁剪（偏移）
如下图，实际是 HBP 的问题。
增大 HBP 后解决，将 HBP 由 10 增加到 30。

![enter description here][9]

### 6.7 正常开机可以点亮，休眠唤醒无法点亮。
dclk 有问题。
用示波器去测究竟 dclk 出来的是多少。
比如我设置的 470 开机启动可以点亮，休眠唤醒无法点亮。
用示波器一测，竟然才 200 Mbps，修改到 584 后（实际出来为 450） 休眠唤醒才也可以点亮。

### 6.8 白屏（偶尔）
白屏有可能是静电问题，把 LCD 拿到头发上擦几下，如果很容易出现白屏那肯定就是静电问题了。
另外一个在有Backend IC的情况下，也有可能bypass没处理好。 

### 6.9 白屏（开机 Logo 到 Android 动画之间）
結束開機logo至Android動畫出現之間出現閃屏或者閃白光的情況。
原因：在這個時間點kernel會會對屏再次初始化，我們可以軟件上屏蔽第一次初始化動作從而解决。

### 6.10 白屏（进入睡眠 suspend / 开始显示 resume 时）
喚醒屏幕閃白光問題，說白了是背光早亮了，很有可能是下序列mdelay太久，改小點就沒有這個問題了。根本原因屏幕初始化序列下慢了。 
sleep out（0x11）和 display on（0x29）之间需要 mdelay（120ms）左右。

### 6.11 花屏
LCD 初始化成功，但是 RGB 没有刷过来。
优先确认 timing 中的 pclk，另外还有可能是总线速度有问题。

开机花屏最简单的解决方式是，在 Init 结束的地方加一个刷黑屏的功能。也可以在睡眠函数里加延时函数。

### 6.12 闪烁（快速，大量）
1. pclk 有问题 
在最开始的时候，我的 pclk 漏了一个 0 ，为之前的 1/10 此时就有图像闪烁问题。
2. proch 有问题 
在调试完后，我尝试将 proch 增加到极限，发现会出现图像闪烁的问题。

### 6.13 闪烁（偶尔）
通过调节电压来稳定，一般调节的电压为VRL、VRH、VDV和VCM

### 6.14 闪烁（唤醒 resume 时）
RST 后下载初始化时序时间过长，适当减少 delay 时间可以解决。

### 6.15 抖动
测时序，延时不足

### 6.16 灰屏（唤醒时）
寄存器没有使能外部升压电路

### 6.17 水波纹
通常都是rgb interface polarity導致，需要調整pclk hsync vsync de極性使之符合平台極性。
这是网上的一个建议。
我自己碰到的一次出现水波纹的原因是 VCOM 不对。在屏厂帮助下，在 init cmds 里面添加关于 VCOM 的调试参数解决。
水波纹一般是 VCOM 的问题。出现水波纹首先可以确保电源和背光部分VDD/AVDD/VGL/VGH纹波足够小,确保VCOM波形正确,VCOM电路端的电源稳定;确保 LCD 周边外围电路的电容、电阻电压是否干净。


### 6.18 调节对比度

VRL、VRH、VDV和VCM，这些电压也可以用来调节亮暗（对比度） 
也可以通过调节Gamma值来实现，要调节的对象为 PRP、PRN、VRP、VRN 等

### 6.19 图像颜色不正常

可能时钟型号极性反了 
可能 VCOM 调节不正常 
进行 GAMMA 校正

### 6.20 明暗色过渡部分，出现不停闪动的亮点
pixel clock 极性，由上升沿采样改为下降沿采样即可。


最后，我上面说的都是废话。
最好的资料就是 RK 官方的TRM 、屏的 Spec 和  Mipi DSI 协议规格书。
LCD 这边的变数太多了，一万个工程师可以碰到一万种屏不显示的情况。
网上搜再多资料也没有抓波、抓上电时序，对照官方手册确认 来的实在。


本文地址：http://blog.csdn.net/dearsq/article/details/77341120
作者 Younix，欢迎转载，转载请著名出处，谢谢。

  [1]: http://blog.csdn.net/dearsq/article/details/52354593
  [2]: http://ww4.sinaimg.cn/large/ba061518gw1f75tvya4xlj20t90bf0zo.jpg
  [3]: http://ww2.sinaimg.cn/large/ba061518gw1f75tu7eik2j20930dfwfw.jpg
  [4]: http://ww4.sinaimg.cn/large/ba061518gw1f75u6elg5wj20na0cudi8.jpg
  [5]: http://ww3.sinaimg.cn/large/ba061518gw1f75u78v1czj20c703uwfg.jpg
  [6]: http://ww2.sinaimg.cn/large/ba061518gw1f75ubbrqosj20c703275b.jpg
  [7]: https://ws4.sinaimg.cn/large/ba061518gw1f7aoi0o0haj20dx0mygqr.jpg
  [8]: https://ws2.sinaimg.cn/large/ba061518gw1f7ao7d3tatj20ic0w0n4y.jpg
  [9]: https://ws3.sinaimg.cn/large/ba061518gw1f7aocxg04tj20km0dogod.jpg