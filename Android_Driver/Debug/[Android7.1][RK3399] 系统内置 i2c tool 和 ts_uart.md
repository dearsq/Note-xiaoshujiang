---
title:[Android7.1][RK3399] 系统内置 i2c tool 和 ts_uart
date: 2019-12-17 21:00:00
tags: Linux

---


## 基本概念
i2c tool 包括 i2cdetect / i2cdump / i2cget / i2cset 
使用说明往上一抓一大吧，不再赘述

ts_uart.bin 是用于测试串口的小程序
使用方法如下：
```shell
rk3399_mid_pi:/ # ts_uart.bin                                                
 Use the following format to run the HS-UART TEST PROGRAM
 ts_uart v1.0
 For sending data: 
 ./ts_uart <tx_rx(s/r)> <file_name> <baudrate> <flow_control(0/1)> <max_delay(0-100)> <random_size(0/1)>
```
 **tx_rx** : send data from file (s) or receive data (r) to put in file
 **file_name** : file name to send data from or place data in
 **baudrate** : baud rate used for TX/RX
 **flow_control** : enables (1) or disables (0) Hardware flow control using RTS/CTS lines
 **max_delay** : defines delay in seconds between each data burst when sending. Choose 0 for continuous stream.
 **random_size** : enables (1) or disables (0) random size data bursts when sending. Choose 0 for max size.
 max_delay and random_size are useful for sleep/wakeup over UART testing. ONLY meaningful when sending data

比如：
 Sending data (no delays)
 ts_uart s init.rc 115200 0 0 0 /dev/ttyS0
 loop back mode:
 ts_uart m init.rc 115200 0 0 0 /dev/ttyS0
 receive then send
 ts_uart r init.rc 115200 0 0 0 /dev/ttyS0


## 内置步骤
rk3399_mid_pi.mk
```mk
@@ -84,6 +84,14 @@ PRODUCT_COPY_FILES += \
    device/rockchip/rk3399/rk3399_all/video_status:system/etc/video_status \
    device/rockchip/common/resolution_white.xml:/system/usr/share/resolution_white.xml
 
+#for debug //i2c-Tools & ts_uart.bin
+PRODUCT_COPY_FILES += \
+   device/rockchip/rk3399/rk3399_mid_pi/bin/i2cdetect:system/bin/i2cdetect \
+   device/rockchip/rk3399/rk3399_mid_pi/bin/i2cdump:system/bin/i2cdump \
+   device/rockchip/rk3399/rk3399_mid_pi/bin/i2cget:system/bin/i2cget \
+   device/rockchip/rk3399/rk3399_mid_pi/bin/i2cset:system/bin/i2cset \
+   device/rockchip/rk3399/rk3399_mid_pi/bin/ts_uart.bin:system/bin/ts_uart.bin
+
```