---
title: [TODO][Android5.1][RK3288] Camera（三）OV13850 Camera 调试笔记.md
tags: camera,rockchip
grammar_cjkRuby: true
---


[TOC]

前面五节是基本概念及基本配置，综合了 RK3288、RK3399 中所有关于 Camera 的文档中的内容。
后面两节是调试过程中碰到的具体问题。

## 基本配置与编译

### DTS 配置
打开对应 isp 即可。
我们 isp0 已经用于 HDMI IN 功能。
所以 Camera 使用的是 isp1 。
```
 isp0: isp@ff910000 {
	 …
	 status = "okay";
 }
 isp1: isp@ff920000 {
	 …
	 status = "okay";
 }
 ```

### 代码结构

```
 Android：
 `- hardware/rockchip/camera/
    |- Config
    |  `- cam_board_rk3399.xml      // 摄像头的参数设置
    |- CameraHal             // 摄像头的 HAL 源码
    `- SiliconImage          // ISP 库，包括所有支持模组的驱动源码
       `- isi/drv/OV13850    // OV13850 模组的驱动源码
          `- calib/OV13850.xml // OV13850 模组的调校参数

 Kernel：
 |- kernel/drivers/media/video/rk_camsys  // CamSys 驱动源码
 `- kernel/include/media/camsys_head.h
```


### 管脚配置
需要设置 Camera 的 GPIO 及时钟。
由如下原理图可知，需要配置的有 I2C 的组别、CSI_RST_H、DVP_PDN1_H、CSI_EN_H。

![](http://ww1.sinaimg.cn/large/ba061518gy1fhzquc8sqmj20k20g4gn4.jpg)

I2C 通道为 I2C1

CSI_RET_H 对应 GPIO0_B0

![](http://ww1.sinaimg.cn/large/ba061518gy1fhzqy0ipzjj20ji00zdft.jpg)


DVP_PDN1_H 对应 GPIO2_D4

![](http://ww1.sinaimg.cn/large/ba061518gy1fhzqyzkicoj20es015749.jpg)

CSI_EN_H 对应 GPIO1_A4

![](http://ww1.sinaimg.cn/large/ba061518gy1fhzqzpwznrj20l700m3yf.jpg)


### 配置 Android

修改 hardware/rockchip/camera/Config/cam_board_rk3399.xml 来注册摄像头：

#### Sensor 名称
```
<SensorName name="OV13850" ></SensorName>
```
该名字必须与 Sensor 驱动名字一致。驱动格式如下
libisp_isi_drv_OV13850.so
用户可在编译 Android 完成后在目录 out/target/product/rk3399_mid/system/lib/hw/ 找到该文件

#### Sensor 软件标识
```
<SensorDevID IDname="CAMSYS_DEVID_SENSOR_1B"></SensorDevID>
```
保证驱动标识不一致即可，可选项有
CAMSYS_DEVID_SENSOR_1A  //已经由 HDMI IN 使用
CAMSYS_DEVID_SENSOR_1B
CAMSYS_DEVID_SENSOR_2

#### 采集控制器名称
```
<SensorHostDevID busnum="CAMSYS_DEVID_MARVIN" ></SensorHostDevID>
```
目前可选的仅有
CAMSYS_DEVID_MARVIN

#### I2C 通道
```
<SensorI2cBusNum busnum="1"></SensorI2cBusNum>
```
参考原理图，我们所用的是 I2C1

#### Sensor 寄存器地址长度
```
<SensorI2cAddrByte byte="2"></SensorI2cAddrByte>
```
#### Sensor 的 I2C 频率
单位：Hz，用于设置 I2C 的频率。
```
<SensorI2cRate rate="100000"></SensorI2cRate>
```
#### Sensor 输入时钟频率
单位：Hz，用于设置摄像头的时钟。
```
<SensorMclk mclk="24000000" delay="1000"></SensorMclk>
```
#### Sensor AVDD 的 PMU LDO 名称
如果不是连接到 PMU，那么只需填写 NC。
```
<SensorAvdd name="NC" min="28000000" max="28000000" delay="0"></SensorAvdd>
```
#### Sensor DVDD 的 PMU LDO 名称
```
<SensorDvdd name="NC" min="12000000" max="12000000" delay="0"></SensorDvdd>
```
#### Sensor DOVDD 的 PMU LDO 名称
```
<SensorDovdd name="NC" min="18000000" max="18000000" delay="5000"></SensorDovdd>
```
如果不是连接到 PMU，那么只需填写 NC。
注意 min 以及 max 值必须填写，这决定了 Sensor 的 IO 电压。

#### Sensor PowerDown 引脚
```
<SensorGpioPwdn ioname="RK30_PIN2_PB6" active="0"></SensorGpioPwdn>  //mipi
<SensorGpioPwdn ioname="RK30_PIN2_PB4" active="0"></SensorGpioPwdn> //dvp
```
直接填写名称即可，active 填写休眠的有效电平。

#### Sensor Reset 引脚。
```
<SensorGpioRst ioname="RK30_PIN0_PB0" active="0"></SensorGpioRst>
```
直接填写名称即可，active 填写复位的有效电平。

#### Sensor Power 引脚
```
<SensorGpioPwen ioname="RK30_PIN1_PC7" active="1"></SensorGpioPwen>
```
直接填写名称即可, active 填写电源有效电平。

#### 选择 Sensor 作为前置还是后置
```
<SensorFacing facing="back"></SensorFacing>
```
可填写 "front" 或 "back"。

#### Sensor 的接口方式
```
<SensorInterface mode="MIPI"></SensorInterface>
```
可填写如下值：
CCIR601
CCIR656
MIPI
SMIA

#### Sensor 的镜像方式
```
<SensorMirrorFlip mirror="0"></SensorMirrorFlip>
```
目前暂不支持。

#### Sensor 的角度信息
```
<SensorOrientation orientation="0"></SensorOrientation>
```
#### 物理接口设置
**MIPI**
```
<SensorPhy phyMode="CamSys_Phy_Mipi" lane="2" phyIndex="1" sensorFmt="CamSys_Fmt_Raw_10b">   </SensorPhy>
  ```
 hyMode：Sensor 接口硬件连接方式，对 MIPI Sensor 来说，该值取 "CamSys_Phy_Mipi"
 Lane：Sensor mipi 接口数据通道数
 Phyindex：Sensor mipi 连接的主控 mipi phy 编号
 sensorFmt：Sensor 输出数据格式,目前支持 CamSys_Fmt_Raw_10b

**DVP**
```
<SensorPhy phyMode="CamSys_Phy_Cif" sensor_d0_to_cif_d ="2" cif_num="0" sensorFmt="CamSys_Fmt_Raw_10b"></SensorPhy>
```
phyMode： Sensor 接口硬件连接方式，DVP Sensor 接口则为：CamSys_Phy_Cif
sensor_d0_to_cif_d：Sensor DVP 输出数据位 D0 对应连接的主控 DVP 接口的数据位号码
cif_num：Sensor DVP 连接到主控 DVP 接口编号
sensorFmt：Sensor 输出的数据格式,目前版本支持填写 CamSys_Fmt_Yuv422_8b


### 编译内核 
需将 drivers\media\video\rk_camsys 驱动源码编进内核，其配置方法如下：

在内核源码目录下执行命令：
```
make menuconfig
```
然后将以下配置项打开：
```
Device Drivers  --->
 <*>Multimedia support  --->
        <*>camsys driver
         RockChip camera system driver  --->
                  <*> camsys driver for marvin isp
                  < > camsys driver for cif
```
最后执行：
```
make ARCH=arm64 rk3399-orangepi.img 
```


## 调试流程

### I2C 不正常

根据 datasheet 

![](http://ww1.sinaimg.cn/large/ba061518gy1fi7vvv4920j20mi0jgtal.jpg)


