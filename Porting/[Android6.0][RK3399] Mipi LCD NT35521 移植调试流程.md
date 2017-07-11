---
title: [Android6.0][RK3399] Mipi LCD NT35521 移植调试流程
tags: mipi,lcd,rockchip,android
grammar_cjkRuby: true
---


## 根据 datasheet 和 硬件设计填写 dts

### mipi_dsi_init
```
disp_mipi_init: mipi_dsi_init{
 	compatible = "rockchip,mipi_dsi_init";
 	rockchip,screen_init	= <1>;
 	rockchip,dsi_lane	= <4>;
 	rockchip,dsi_hs_clk	= <1000>;
 	rockchip,mipi_dsi_num	= <1>;
 };
```

### GPIO

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0saeborj20hy0is3zs.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0th3mo3j20um0bl75k.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0v0p25cj20dn00sjra.jpg)
```
 	mipi_lcd_en:mipi_lcd_en {
 		compatible = "rockchip,lcd_en";
 		rockchip,gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>;
 		rockchip,delay = <20>;
 	};
```

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0v5djgnj20js01f0st.jpg)
```
 	mipi_lcd_rst:mipi_lcd_rst {
 		compatible = "rockchip,lcd_rst";
 		rockchip,gpios = <&gpio4 30 GPIO_ACTIVE_HIGH>;
 		rockchip,delay = <100>;
 	};
```

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0v9tkn6j20pf00l3yh.jpg)
```
backlight: backlight {
		status = "disabled";
		compatible = "pwm-backlight";
		pwms = <&pwm0 0 25000 0>;
		brightness-levels = <
								...
										>;
```

### Display Timing

![](http://ww1.sinaimg.cn/large/ba061518gy1fhg0ycyre2j20mm0bqmzz.jpg)
```
  disp_timings: display-timings {
  	native-mode = <&timing0>;
  	compatible = "rockchip,display-timings";
  	timing0: timing0 {
  		screen-type = <SCREEN_MIPI>;
  		lvds-format = <LVDS_8BIT_2>;
  		out-face    = <OUT_P888>;
  		clock-frequency = <76000000>;
  		hactive = <800>;
  		vactive = <1280>;
  		hback-porch = <80>;
  		hfront-porch = <80>;
  		vback-porch = <23>;
  		vfront-porch = <18>;
  		hsync-len = <0>;
  		vsync-len = <0>;
  		hsync-active = <0>;
  		vsync-active = <0>;
  		de-active = <0>;
  		pixelclk-active = <0>;
  		swap-rb = <0>;
  		swap-rg = <0>;
  		swap-gb = <0>;
  		//screen-width = <68>;
  		//screen-hight = <120>;
	};
```
### init cmd
屏场给的 Init cmd 序列是 MTK 平台的。
形如
```
data_array[0]=0x00043902;
data_array[1]=0x8983FFB9; 
dsi_set_cmdq(&data_array, 2, 1); 
MDELAY(10);
```
转换规则在 http://blog.csdn.net/dearsq/article/details/52354593
讲的很详细。
不再赘述了。
这个屏竟然有 112 条 inital cmd 。第一次碰到这么多 cmd 的屏。

## 进行调试
