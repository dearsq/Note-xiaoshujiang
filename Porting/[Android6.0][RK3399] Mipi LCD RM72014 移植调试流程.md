---
title: [Android6.0][RK3399] Mipi LCD RM72014 移植调试流程
tags: mipi,lcd,rockchip,android
grammar_cjkRuby: true
---

[TOC]

## 根据 datasheet 和 硬件设计填写 dts

### mipi_dsi_init 
```
 disp_mipi_init: mipi_dsi_init{
 	compatible = "rockchip,mipi_dsi_init";
 	rockchip,screen_init	= <1>;
 	rockchip,dsi_lane	= <4>;
 	rockchip,dsi_hs_clk	= <1000>;
 	rockchip,mipi_dsi_num	= <1>; // 有几个屏就填几
 };
 ```
 ### GPIO

![](http://ww1.sinaimg.cn/large/ba061518gy1fhey171zzuj20c00jbwfr.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gy1fheygh9086j20jl012weg.jpg)
```
 	compatible = "rockchip,mipi_power_ctr";
 	mipi_lcd_rst:mipi_lcd_rst {
 		compatible = "rockchip,lcd_rst";
 		rockchip,gpios = <&gpio4 30 GPIO_ACTIVE_HIGH>;  // GPIO4_D6
 		rockchip,delay = <100>;
 	};
```

![](http://ww1.sinaimg.cn/large/ba061518gy1fheyeyrrc8j20gx00swef.jpg)
```
 	mipi_lcd_en:mipi_lcd_en {
 		compatible = "rockchip,lcd_en";
 		rockchip,gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>; //GPIO1_B5
 		rockchip,delay = <20>;
 	};
 	
 ```
 
 ### Display Timing
 
 ![](http://ww1.sinaimg.cn/large/ba061518gy1fhexwybiurj20g40hqdhw.jpg)

```
disp_timings: display-timings {
        native-mode = <&timing0>;
        compatible = "rockchip,display-timings";
        timing0: timing0 {
            screen-type = <SCREEN_MIPI>;        //单mipi SCREEN_MIPI 双mipi SCREEN_DUAL_MIPI
            lvds-format = <LVDS_8BIT_2>;        //不用配置
            out-face    = <OUT_P888>;       //屏的接线格式 
            //配置颜色，可为OUT_P888（24位）、OUT_P666（18位）或者OUT_P565（16位）
            clock-frequency = <120000000>;      //dclk频率，看规格书，或者 H×V×fps
            hactive = <800>;            //水平有效像素
            vactive = <1280>;            //垂直有效像素
            hback-porch = <18>;         //水平同步信号
            hfront-porch = <2>;            //水平同步信号
            vback-porch = <16>;
            vfront-porch = <4>;            
            hsync-len = <18>;           //水平同步信号
            vsync-len = <4>;
            hsync-active = <0>;         //hync 极性控制 置 1 反转极性
            vsync-active = <0>;
            de-active = <0>;            //DEN 极性控制
            pixelclk-active = <0>;          //dclk 极性控制
            swap-rb = <0>;              //设 1 反转颜色
            swap-rg = <0>;
            swap-gb = <0>;
	};
};
```

### init cmd
根据屏场给的时序
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

写出对应的 inital cmd
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

  rockchip,on-cmds5 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x39 0xc3 0x40 0x00 0x28>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds6 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0x50 0x77>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds7 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0xe1 0x66>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds8 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0xdc 0x67>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds9 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0xd3 0xc8>;
 		rockchip,cmd_delay = <0>;
 	};

  rockchip,on-cmds10 {
 		compatible = "rockchip,on-cmds";
 		rockchip,cmd_type = <LPDT>;
 		rockchip,dsi_id = <2>;
 		rockchip,cmd = <0x15 0x50 0x00>;
 		rockchip,cmd_delay = <0>;
 	};

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


## 进行调试