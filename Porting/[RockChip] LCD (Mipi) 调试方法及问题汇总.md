---
title: [rockchip] LCD 调试方法及问题汇总
tags: rk,lcd,mipi
grammar_cjkRuby: true
---
## 调试流程
### 设置 dts 中的参数 并 配置管脚
仿造平台的其他 lcd-*-mipi.dtsi 编写 lcd-xxx-mipi.dtsi 后 需要在 主 dts 文件中包含这个 dtsi
```
#include “lcd-xxx-mipi.dtsi“
```
先看屏的手册
![](http://ww3.sinaimg.cn/large/ba061518gw1f75t1eozbij20rs0jbtc3.jpg)
里面的关键信息有 **分辨率**（540×960） **接口**（2条lanes）
```c
## MIPI Host配置
disp_mipi_init: mipi_dsi_init{
		compatible = "rockchip,mipi_dsi_init";

		/* 是否要在 dtsi 中初始化 1 0 */
		rockchip,screen_init	= <1>;

		/* 要几条数据 lane ，根据原理图和 mipi 规格书*/
		rockchip,dsi_lane		= <2>;

		/* ddr clk 一条 lane 的传输速率 Mbits/s  */
		/* 100 + H_total×V_total×fps×3（一个rgb为3字节）×8（8bits）/lanes  */
        /* 这里的 total 指的是 sync + front + back + active */
        /* 比如 H_total = Hsync + HFP(hfront-proch)  + HBP(hback-porch) + Hactive  */
		rockchip,dsi_hs_clk		= <1000>;

		/* 单mipi 还是双 mipi*/
		rockchip,mipi_dsi_num	= <1>;
};
```
**看原理图，完成管脚的配置**
![](http://ww3.sinaimg.cn/large/ba061518gw1f75tavt1wmj20g40qddim.jpg)
可以看到，我这里只用到了 LCD_RST，没有用到 LCD_EN （是  VCC_LCD）,说明是默认使能的，也没有 LCD_CS
所以进行如下配置
```
## 屏电源控制配置
disp_mipi_power_ctr: mipi_power_ctr {
		compatible = "rockchip,mipi_power_ctr";
		mipi_lcd_rst:mipi_lcd_rst{
				compatible = "rockchip,lcd_rst";
				rockchip,gpios = <&gpio2 GPIO_B7 GPIO_ACTIVE_LOW>;
				rockchip,delay = <100>;
		};
        /*
		// 配置 lcd_en GPIO 哪一路 ，有可能没有 LCD_EN 那么就是 VCC 常供电
		mipi_lcd_en:mipi_lcd_en {
				compatible = "rockchip,lcd_en";
				rockchip,gpios = <&gpio0 GPIO_C1 GPIO_ACTIVE_HIGH>;
				rockchip,delay = <100>;
		};
        */
        //还可能有片选 cs
};
```
**根据屏的规格书 完成 timings 配置**
垂直方向的信息：
![](http://ww2.sinaimg.cn/large/ba061518gw1f75tgnkgoaj20r007z76z.jpg)
重要的参数有 垂直同步信号 VFP VBP VS 对应填充到屏参中的 Vfront-proch Vback-proch Vsync-len
同样
水平方向的信息：
![](http://ww2.sinaimg.cn/large/ba061518gw1f75tkaa6bbj20sj09swhq.jpg)
要注意的是， HS HBP HFP 虽然最小值是 5，但是不能设置的这么低
因为后面还有两条要求，HBLK = HS + HBP + HFP >= 24   且  HS + HBP  > 19
所以最初设置 HS = HBP = HFP = 10
```dts
// lcd-xxx-mipi.dtsi 中的 屏参
disp_timings: display-timings {
		native-mode = <&timing0>;
		compatible = "rockchip,display-timings";
		timing0: timing0 {
			screen-type = <SCREEN_MIPI>;		//单mipi SCREEN_MIPI 双mipi SCREEN_DUAL_MIPI
			lvds-format = <LVDS_8BIT_2>;		//不用配置
			out-face    = <OUT_P888>;		//屏的接线格式
			//配置颜色，可为OUT_P888（24位）、OUT_P666（18位）或者OUT_P565（16位）
			clock-frequency = <120000000>;		//dclk频率，看规格书，或者 H×V×fps
			hactive = <540>;			//水平有效像素
			vactive = <960>;			//垂直有效像素
			hback-porch = <80>;			//水平同步信号
			hfront-porch = <81>;			//水平同步信号
			vback-porch = <21>;
			vfront-porch = <21>;			
			hsync-len = <10>;			//水平同步信号
			vsync-len = <3>;
			hsync-active = <0>;			//hync 极性控制 置 1 反转极性
			vsync-active = <0>;
			de-active = <0>;			//DEN 极性控制
			pixelclk-active = <0>;			//dclk 极性控制
			swap-rb = <0>;				//设 1 反转颜色
			swap-rg = <0>;
			swap-gb = <0>;
```
### 背光部分
**在 rk3288-tb_8846.dts 中还需要打开 mipi 相关的通道 并 配置背光相关的信息。**
首先根据这颗背光 IC 的 datasheet
![](http://ww4.sinaimg.cn/large/ba061518gw1f75tvya4xlj20t90bf0zo.jpg)
我们了解到 EN 拉高时背光使能，拉低时背光禁能; FB 接受反馈信号，动态控制背光亮度
![](http://ww2.sinaimg.cn/large/ba061518gw1f75tu7eik2j20930dfwfw.jpg)
我们知道这颗背光芯片有两种调光方式
一是 EN 输入 PWM 信号进行调光
二是 EN 使能后，通过 FB 获得反馈信号进行调光。
根据我们的原理图
![](http://ww4.sinaimg.cn/large/ba061518gw1f75u6elg5wj20na0cudi8.jpg)
![](http://ww3.sinaimg.cn/large/ba061518gw1f75u78v1czj20c703uwfg.jpg)
BL_EN 是普通的 GPIO ，LCDC_BL 是支持 PWM 输出的管脚，所以得知我们硬件采用的是第二种调光方式
```dts
backlight {
		compatible = "pwm-backlight";
		pwms = <&pwm0 0 25000>;		//在这里配置采用的是 pwm0 还是 pwm1
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
		enable-gpios = <&gpio7 GPIO_A2 GPIO_ACTIVE_HIGH>;	//BL_EN 背光使能管脚
	};
```
### LCD 初始化序列 cmds
最后如果有初始化序列的，打开之前的 screen-init = < 1 > ，并且填充初始化序列
```
## 屏初始化序列
disp_mipi_init_cmds: screen-on-cmds {
		compatible = "rockchip,screen-on-cmds";
		/*rockchip,cmd_debug = <1>;
		rockchip,on-cmds1 { //指的是一条初始化命令
				compatible = "rockchip,on-cmds";
				rockchip,cmd_type = <LPDT>;		//命令是在 low power（LPDT）还是 high speed（HSDT）下发送
				rockchip,dsi_id = <2>;			//选择通过哪个mipi发送 0==》单mipi0  1==》mipi1 2==》双mipi0+1
				rockchip,cmd = <0x05 0x01>;		//初始化命令
					//第一个字节 DSI 数据类型; 第二个字节为 LCD 的 CMD; 后面为指令内容
				rockchip,cmd_delay = <0>;
		};
		*/
};
```
值得一讲的是 cmd，一般屏厂或者FAE都会给出初始化序列。
比如这里我拿到的是 MTK 平台的 LCD 初始化代码：
```
data_array[0]=0x00043902;
data_array[1]=0x8983FFB9;
dsi_set_cmdq(&data_array, 2, 1);
MDELAY(10);
```
分析得知
array[0] 中 04 代表要传输的**字节数**，3902 代表传输的是**长包数据**
//MTK平台 3900 代表不传值 3905 表示传一个数据 3902 表示传多个数据
array[1] 中的参数全部为传输的参数，而且正确的传参数据为 B9 FF 83 89
所以移植到 RK 平台就是：
```
rockchip,on-cmds1 {
					        compatible = "rockchip,on-cmds";
							rockchip,cmd_type = <LPDT>;
							rockchip,dsi_id = <0>;
							rockchip,cmd = <0x39 0xB9 0xFF 0x83 0x89>;
                            //0x39 为 DSI 数据类型、  0xB9 为LCD CMD、后面为参数
							rockchip,cmd_delay = <10>;
}
```
我们根据 这块 lcd 的 规格书，也能够验证结果初始化命令参数的正确性：
![](http://ww1.sinaimg.cn/large/ba061518gw1f7adg4pesoj20az063dgd.jpg)

另外值得一说的是大部分初始化代码的最后一般都是 exit_sleep 和 display_on。
```
rockchip,on-cmds15 {
					        compatible = "rockchip,on-cmds";
							rockchip,cmd_type = <LPDT>;
							rockchip,dsi_id = <0>;
							rockchip,cmd = <0x05 dcs_exit_sleep_mode>;
							rockchip,cmd_delay = <120>;
					};
					rockchip,on-cmds16 {
					        compatible = "rockchip,on-cmds";
							rockchip,cmd_type = <LPDT>;
							rockchip,dsi_id = <0>;
							rockchip,cmd = <0x05 dcs_set_display_on>;
							rockchip,cmd_delay = <100>;
					};
```
这里 dcs_exit_sleep_mode dcs_set_display_on 在 drivers/video/rockchip/transmitter/mipi_dsi.h 中有定义
```
#define dcs_set_display_on	0x29
#define dcs_exit_sleep_mode 0x11
```
所以表示的 0x05 0x11 表示的含义为，短包传输  发送 exit_sleep_mode 命令
这两个命令后的**延时****相当重要**！！务必确认好。
### 打开 config
根据 RK 手册中的要求
make menuconfig
打开三个宏
![](http://ww2.sinaimg.cn/large/ba061518gw1f75ubbrqosj20c703275b.jpg)
这里也可以顺手把 LVDS 的相关代码给关掉

### 检查电压
先不要接上屏，编译完代码烧录后开机。
检查原理图上各个供电管脚的电压（DVDD、IOVDD 是否为 3.3V，VDD_LCDA 是否为 5-10V，VDD_LCDK 是否为 0V），确认电压正常后，关机，上屏，结合 开机log 看能否正常开机。

### 调试顺序
#### 背光有没有亮
背光没亮的话确认一下接上屏的时候，量一量 VDD_LCDA 的电压为多少（串联电路大概能到 20V+）
没有就去检查背光电路供电电压和 backlight 相关的配置
#### 开机 以及 从休眠状态唤醒 都没有显示内容
之所以这样说是因为可能存在 休眠唤醒 能显示，但 开机 无法显示的情况
如果两种情况都没有显示，那么很有可能是 cmds 或者 timing 仍然有问题
1. 用示波器量波形看 DCLKP 的频率为多少，是否为 clock-frequence 中设置的（可能实际的会略低一点）
2. 量 RST 是否有一个 高-低-高 的变化，没有则是 rst 设置的触发方式可能反了
3. 在 RST 高低高后会开始传输数据，量 lanes 是否有数据输出。抓取数据需要专门的仪器，我们用示波器大致看看有没有数据输出就够了。

我在调试的时候就发现 lane 一直为低电平，没有数据传输，然后采取量 RST 发现唤醒屏后待到屏幕快灭了 RST 才会被拉高。跟代码发现 RK 平台的实现是
```
！你设置的触发电平
你设置的触发电平
```
但是我设置的触发电平是 低电平有效 ACTIVE_LOW
即
```
！ACTIVE_LOW
ACTIVE_LOW
```
即先高再低，所以是错的，改为 ACTIVE_HIGH 后正常。
但是虽然填的是 ACTIVE_HIGH ，但是应该还是属于低电平有效的，这里是 RK 平台 driver 的实现有问题。
修改后 lane 有数据传递了。

但是有数据传递仍然怎么样都没有显示。
这时候有极大可能是 cmds 有问题。
下面着重讲一下我 cmds 碰到的问题。
#### 我碰到的 cmds 问题
我当时拿到 MTK 平台参数的时候，有的参数超过了 32个字节（有个有36个字节，有个有39个字节），完成 dtsi 中 cmds 编写后
烧录，板子跑飞，空指针异常。
发现传递 这个超长 参数的时候有内存溢出情况。
于是跟代码发现 dcs_cmd.cmds 的大小为 int cmds[32]，所以擅自想当然的将包拆成了 39 = 28+11，还将其中的延时设置为 0 。
这样当然是不行的。但是一切都是基于这个拆了包的 cmds 来调，走了不少弯路。
后来一切的其他参数都确定没问题了。
于是去联系原厂的工程师，说平台参数大小有限制，咨询拆包是否可行。他们说建议修改 cmds[32] 改成了 cmds[400] 。
修改后发现屏幕终于点亮了。
终于点亮了。
点亮了。

## 问题集锦
**RK 手册中已经有相当一部分很有参考价值的了。**
这里的一部分是自己碰到的，有的是查资料时候收集到觉得很有意义的，都放这里了。
### 我调试中碰到的问题
1. 在点亮屏后刚开始有开机 logo 闪烁，向右偏移了近半个屏幕的长度，等问题。
重新确认 **clock-frequence** 后发现少打了一个 0 。
修改后解决了 闪烁，大偏移 的问题。
2. 最初偏移还是有点大，如下图。
![](https://ws4.sinaimg.cn/large/ba061518gw1f7aoi0o0haj20dx0mygqr.jpg)
稍微降低 hs_clk ，由 504 降低到 496 解决。
3. 垂直方向会显示多一点内容，如下图。
![](https://ws2.sinaimg.cn/large/ba061518gw1f7ao7d3tatj20ic0w0n4y.jpg)
调整 VFP 后解决，将 VFP 增大为 15 。
4. 下面会有黑边，如下图。
![](https://ws4.sinaimg.cn/large/ba061518gw1f7aoa5m9wsj20cb07m3zd.jpg)
稍微增大 VBP 后解决，将 VBP 增大为 15。
5. 开机 android 最左边会被裁剪一部分，如下图。
![](https://ws3.sinaimg.cn/large/ba061518gw1f7aocxg04tj20km0dogod.jpg)
增大 HBP 后解决，将 HBP 由 10 增加到 30。
至此屏幕已完美显示。
### 其他一些杂散的需要确认的内容
是否有framebuffer輸出，要是改動了display這塊的clk很有可能沒有buffer輸出的，可以通過cat /dev/graphyics/fb0查看有沒有輸出字符。（我是通过google 插件 vysor 直接连接开发板看有没有内容显示，windows 平台也可以用 total control 软件来看）
### 数据为 8 位、16位
数据为 8 位  和 16 位 的时候，写命令和数据的函数要注意变化。
会发现 如果 参数为 8 位的时候， 传输模式会自动由 LP 模式 变成 HS 模式。
### 显示偏移、图像位置偏差
timing 中的参数设置有误。优先确认。
看着图像调节前扫、回扫进行左右上下移动
### 白屏
随机出现白屏有可能是静电问题，把LCD拿到头发上擦几下，如果很容易出现白屏那肯定就是静电问题了。另外一个在有Backend IC的情况下，也有可能bypass没处理好。
### 屏在进出睡眠或者显示过程中白屏
sleep out（0x11）和 display on（0x29）之间需要 mdelay（120ms）左右。
### 屏休眠唤醒后四周有白色痕迹
检查下是不是屏的供电电源在休眠时没有关闭,导致屏上的电荷无法释放, 产生这种极化现象。
### 花屏
**timing 中的参数设置有误。优先确认。**
花屏 还有可能是总线速度有问题
**开机就花屏**最简单的解决方式是，在 Init 结束的地方加一个刷黑屏的功能。也可以在睡眠函数里加延时函数。
### 屏幕抖动
测时序，延时不足。
适当地降低 clk，或者调节下 Vcom，确保屏供电电源波纹不大。
### 屏幕闪动
通过调节电压来稳定，一般调节的电压为VRL、VRH、VDV和VCM
### 调节对比度
VRL、VRH、VDV和VCM，这些电压也可以用来调节亮暗（对比度）
也可以通过调节Gamma值来实现，要调节的对象为 PRP、PRN、VRP、VRN 等
### 确认有没有 framebuffer 输出
要是改动了display这块的clk很有可能没有buffer输出的，可以通过cat /dev/graphyics/fb0 查看有没有输出字符
如果有说明是 mipi 还没有调通，如果没有说明是 fb 有问题
### 图像颜色不正常
可能时钟型号极性反了
可能 VCOM 调节不正常
进行 GAMMA 校正

## EDP 屏调试问题汇总
确保上电时序正确,先将 uboot-logo-on=0,打印 kernel log。
### hw lt err
检查下硬件连线,edp 屏的连接线
上传输的高速的差分信号,所以对线的要求很高,要求线要包地,而且不能太长。
如果硬件上的问题排查了,仍然有这样的错误,可以在 rk32_dp.c 文件中手动修改代码,得到想要的 lane 数和 lane speed:
rk32_edp_probe 函数中可以修改这两个变量值:
edp->video_info.link_rate= LINK_RATE_2_70GBPS;//LINK_RATE_1_62GBPS
edp->video_info.lane_count = LANE_CNT4;//LANE_CNT2
### max link rate:1.62Gps max number of lanes:4
说明读取屏的 lane 数和 lane speed 正常,那么可以与屏的 datasheet 中对比下,看读取的结果是否是正确的,如果是正确的试着降低 dclk 的值。如果不正确可以在rk32_dp.c 文件中这样修改试下:
```
static int rk32_edp_init_training(struct rk32_edp *edp)
{
		int retval;
		/*
		* MACRO_RST must be applied after the PLL_LOCK to avoid
		* the DP inter pair skew issue for at least 10 us
		*/
		rk32_edp_reset_macro(edp);
		retval = rk32_edp_get_max_rx_bandwidth(edp,	&edp->link_train.link_rate);
++    retval = rk32_edp_get_max_rx_lane_count(edp,	&edp->link_train.lane_count);
		edp->link_train.link_rate = LINK_RATE_2_70GBPS;//LINK_RATE_1_62GBPS
		edp->link_train.lane_count = LANE_CNT4;//LANE_CNT2
		...
}
```
### edp pll locked
```bash
[ 1.336855] rk32-edp rk32-edp: edp pll locked
[ 1.337492] rk32-edp rk32-edp: max link rate:1.62Gps max number of lanes:4
[ 1.343428] rk32-edp rk32-edp: hw lt err:6
[ 1.343438] rk32-edp rk32-edp: link train failed!
```
屏的转接排线长了,后面改短了就可以了

## RGB 屏调试问题汇总
### 8 位 串口屏蓝色无法正常显示
调节 out_face 为 out_s888dumy,红色和绿色可以显示,但颜色位置是颠倒的,后面看 TRM
发现 RK 平台发送红绿蓝的格式为 BGR+DUMMY
![](https://ws2.sinaimg.cn/large/ba061518gw1fbgptmu2iuj20ir01gmxe.jpg)
屏接收的格式可能为 dummy+RGB,这样主控端发送的 B 就被认为是 dummy 舍弃了,然
后只剩下 RG,B 接收的是 dummy 数据为空,后面将格式改为 dummy+rgb 后成功显示全
部颜色
### 3128 平台 rgb 屏插入 hdmi 后 RGB 屏显示异常
插入 hdmi 后系统的时钟输出直接供给 HDMI 模块,显示 720p 的数据, RGB 屏的 clk 和数据通过一个 Scaler 模块,输出的 clk 值可能有所降低,可以调试屏的 clk 参数。
### spi 接口屏需要发初始化命令，代码添加位置
可以在 rk_disp_pwr_enable 这个函数结束处添加屏的初始化命令。如果有下电命令的话,要在 rk_disp_pwr_disable 开始处添加。
### 初始化命令点亮屏，代码添加位置
初始化命令添加的地方应该在 rk3288_lcdc_open 函数中的 clk 打开后添加。


## 感谢
这段时间基本上把有些 Mipi 移植和 RK 平台 LCD 移植的文章看遍了。以下文章很有帮助。本文的问题集锦部分有一部分是将以下文章中的内容搜罗过来的：
[android lcd調試 高通平台lcd調試深入分析總結（mipi和rgb接口）](http://fanli7.net/a/bianchengyuyan/C__/20130104/283658.html)


最后，得感谢这段时间师兄 Baker 和 Nick 的指点。
还有网上两位 RK 刘哥和“llg”和“勇气” 的指点。
收益颇丰。谢谢谢谢！
