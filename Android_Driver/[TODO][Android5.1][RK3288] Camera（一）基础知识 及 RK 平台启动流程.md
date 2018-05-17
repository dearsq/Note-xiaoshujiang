---
title: [TODO][Android5.1][RK3288] Camera（一）基础知识 及 RK 平台启动流程
tags: Camera
grammar_cjkRuby: true
---
## 基础
### 模组结构
Camera 模组由
**镜头 LENS
对焦马达 VCM
图像传感器 SENOSOR
图像信号处理器 ISP**
组成
### 成像原理
**镜头（LENS）**拍摄影像——>
**传感器（SENSOR）**接受滤色镜滤波后的光学图像，并转化为电信号——>
**A/D转换器**将模拟图像信号转为数字图像信号——>
**ISP（图像信号处理芯片）**加工处理后，通过 IO 口——>
**CPU**处理成手机屏幕上能够看到的图像。

![](https://ws4.sinaimg.cn/large/ba061518gw1f7crdlw6lmj20h1067wf7.jpg)

更多相关细节：http://ju.outofmemory.cn/entry/118955

### 分类
#### 按模组中的图像传感器
分为 **CCD Sensor** 和 **CMOS Sensor**
CMOS 比 CCD 灵敏度低、噪声大，但是成本低、功耗低、集成度高、体积小。
所以手机和平板大多数是 CMOS 模组。
#### 按接口
按接口来划分，Camera 分为 **DVP** 、 **MIPI**、usb camera。
**DVP**是并口，需要PCLK、VSYNC、HSYNC、D[0：11]——可以是8/10/12bit数据，看 ISP 或 baseband 是否支持；
**MIPI**是LVDS，低压差分串口。只需要要CLKP/N、DATAP/N——最大支持4-lane，一般2-lane可以搞定。
**usb camera** 相当于集 sensor、isp 驱动于一身的消息通，通过 usb 接口对外提供 YUV、MJpeg 等图像数据。
### 按模组是否集成 ISP
按照带不带 ISP（图像信号处理器）来划分，分为 **SoC Sensor** 和 **RAW Sensor**。
**SoC Sensor**：自带 ISP，输出 YUV 数据，使用 CIF 接口（通用摄像头接口）。（CIF 接口不带 ISP ，不对 Camera 效果做处理）
**RAW Sensor**：不带 ISP，输出 sensor 采集原始灰度数据，使用 Mipi 接口。（目前仅 3288 支持这种 Sensor，这种需要我们调试效果，使用 Mipi 接口）
### 对比
MIPI接口比DVP的接口信号线少，由于是低压差分信号，产生的干扰小，抗干扰能力也强。最重要的是 DVP 接口在信号完整性方面受限制，速率也受限制。500W还可以勉强用DVP，800W及以上都采用MIPI接口。
USB摄像头，即插即用比较灵活，但是由于传输速率的瓶颈，其支持分辨率较低。

## 硬件原理
### Mipi Sensor
**原理图**

![](https://ws4.sinaimg.cn/large/ba061518gw1f7cphg4lncj20vd0chtbf.jpg)
串行总线（CSI-2）：clock+、clock-，dataN+，dataN-
控制总线（CCI）：SDA，SCK


### DVP（digital video port）Sensor
**原理图**
![](https://ws4.sinaimg.cn/large/ba061518gw1f7cpq394kuj20se0ggdit.jpg)
输出总线：PWDN、RST、MCLK、SCK、SDA
输入总线：VSYNC、HSYNC、PCLK、DATA[0-7]
电源总线：AVDD（2.8V）、DVDD（1.8V）、DOVDD（2.8V）

## 软件架构
![](https://ws2.sinaimg.cn/large/ba061518gw1f7crxw1oavj20i80fd41i.jpg)
从上至下来看
### Application
package/apps/Camera2 这个 APK
### Framework
/android/frameworks/base/core/java/android/hardware/Camera.java
```java
android.hardware.Camera
```
这个类用来链接或者断开一个 Camera 服务，设置参数，开始、停止预览、拍照等。
这个类和 JNI 中定义的类是一个，有些方法通过JNI的方式调用本地代码得到，有些方法自己实现。

Camera的JAVA native调用部分（JNI）：
/android/frameworks/base/core/jni/android_hardware_Camera.cpp。
Camera.java 承接JAVA 代码到C++ 代码的桥梁。

Camera 框架的 client 部分：
/android/frameworks/av/camera下：
Camera.cpp
CameraParameters.cpp
ICamera.cpp
ICameraClient.cpp
ICameraService.cpp
作为Camera 框架的 Client 客户端部分，与另外一部分内容服务端通过进程间通讯（即Binder 机制）的方式进行通讯。

Camera框架的service部分：
/android/frameworks/av/services/camera/libcameraservice。
CameraService 是 Camera 服务，Camera 框架的中间层，用于链接 CameraHardwareInterface 和 Client 部分 ，它通过调用实际的 Camera 硬件接口来实现功能，即下面要提到的HAL层。

### HAL
Camerahal是根据CameraHardwareInterface规定的接口，依据V4l2 规范实例化底层硬件驱动，使用ioctl 方式调用驱动,驱动相关的driver，实现对camera硬件的操作。
代码目录说明：
Android：
|
| hardware\rk29\camera
	|
    |CameraHal                       
        |
        |CameraHal.cpp     
        |CameraHal.h
        |CameraHal_Module.cpp
        |CameraHal_Module.h
        |CameraSocAdapter.cpp
        |CameraHalUtil.cpp
        |AppMsgNotifier.cpp
        |CameraAdapter.cpp

### Kernel
video4linux2(V4L2) 是 Linux内核中关于视频设备的内核驱动，它为Linux中视频设备访问提供了通用接口。
#### V4L2
![](https://ws4.sinaimg.cn/large/ba061518gw1f7csqjakwyj20hi0csmyi.jpg)
#### 代码目录
V4L2 的驱动源码在 drivers/media/video目录下，主要核心代码有：
v4l2-dev.c       //linux版本2视频捕捉接口,主要结构体 video_device 的注册
v4l2-common.c     //在 Linux 操作系统体系采用低级别的操作一套设备 structures/vectors 的通用视频设备接口
v4l2-device.c            //V4L2的设备支持。注册v4l2_device
v4l22-ioctl.c             //处理V4L2的ioctl命令的一个通用的框架
v4l2-subdev.c          //v4l2子设备
v4l2-mem2mem.c      //内存到内存为 Linux 和 videobuf 视频设备的框架，设备的辅助函数，使用其源和目的地videobuf缓冲区。

### 重要结构体
![](https://ws3.sinaimg.cn/large/ba061518gw1f7csvkusehj20hn045gm9.jpg)
v4l2_device 设备结构体
这个定义在linux/media/v4l2-device.h当中定义
```c
struct v4l2_device {
//指向设备模型的指针
struct device *dev;
#if defined(CONFIG_MEDIA_CONTROLLER)
//指向一个媒体控制器的指针
struct media_device *mdev;
#endif
//管理子设备的双向链表，所有注册到的子设备都需要加入到这个链表当中
struct list_head subdevs;
//全局锁
spinlock_t lock;
//设备名称
char name[V4L2_DEVICE_NAME_SIZE];
//通知回调函数，通常用于子设备传递事件，这些事件可以是自定义事件
void (*notify)(struct v4l2_subdev*sd, uint notification, void *arg);
//控制句柄
struct v4l2_ctrl_handler*ctrl_handler;
//设备的优先级状态，一般有后台，交互，记录三种优先级，依次变高
struct v4l2_prio_state prio;
//ioctl操作的互斥量
struct mutex ioctl_lock;
//本结构体的引用追踪
struct kref ref;
//设备释放函数
void (*release)(struct v4l2_device*v4l2_dev);
};

v4l2_subdev 子设备结构：
struct v4l2_subdev {
#if defined(CONFIG_MEDIA_CONTROLLER)
//媒体控制器的实体，和v4l2_device
struct media_entity entity;
#endif
struct list_head list;
struct module *owner;
u32 flags;
//指向一个v4l2设备
struct v4l2_device *v4l2_dev;
//子设备的操作函数集
const struct v4l2_subdev_ops *ops;
//子设备的内部操作函数集
const struct v4l2_subdev_internal_ops*internal_ops;
//控制函数处理器
struct v4l2_ctrl_handler*ctrl_handler;
//子设备的名称
char name[V4L2_SUBDEV_NAME_SIZE];
//子设备所在的组标识
u32 grp_id;
//子设备私有数据指针，一般指向总线接口的客户端
void *dev_priv;
//子设备私有的数据指针，一般指向总线接口的host端
void *host_priv;
//设备节点
struct video_device devnode;
//子设备的事件
unsigned int nevents;
};

video_device
struct video_device{
#if defined(CONFIG_MEDIA_CONTROLLER)
struct media_entity entity;
#endif
const struct v4l2_file_operations*fops;
struct device dev; /* v4l device */
struct cdev *cdev; /* characterdevice */
struct device *parent; /* deviceparent */
struct v4l2_device *v4l2_dev; /*v4l2_device parent */
struct v4l2_ctrl_handler*ctrl_handler;
struct v4l2_prio_state *prio;
char name[32];
int vfl_type;
int minor;
u16 num;
unsigned long flags;
int index;
spinlock_t fh_lock; /* Lock forall v4l2_fhs */
struct list_head fh_list; /* List ofstruct v4l2_fh */
int debug; /* Activates debuglevel*/
v4l2_std_id tvnorms; /* Supported tvnorms */
v4l2_std_id current_norm; /* Currenttvnorm */
void (*release)(struct video_device*vdev);
const struct v4l2_ioctl_ops*ioctl_ops;
struct mutex *lock;
};
```

#### V4L2 主要 IO 操作
V4L2驱动的Video设备在用户空间通过各种ioctl调用进行控制，并且可以使用mmap进行内存映射。V4l2主要的IO操作：
VIDIOC_REQBUFS：分配内存
VIDIOC_QUERYBUF：把VIDIOC_REQBUFS中分配的数据缓存转换成物理地址
VIDIOC_QUERYCAP：查询驱动功能
VIDIOC_ENUM_FMT：获取当前驱动支持的视频格式
VIDIOC_S_FMT：设置当前驱动的频捕获格式
VIDIOC_G_FMT：读取当前驱动的频捕获格式
VIDIOC_TRY_FMT：验证当前驱动的显示格式
VIDIOC_CROPCAP：查询驱动的修剪能力
VIDIOC_S_CROP：设置视频信号的边框
VIDIOC_G_CROP：读取视频信号的边框
VIDIOC_QBUF：把数据从缓存中读取出来
VIDIOC_DQBUF：把数据放回缓存队列
VIDIOC_STREAMON：开始视频显示函数
VIDIOC_STREAMOFF：结束视频显示函数。

### 模组驱动
代码目录：
模组驱动源码：driver/media/video/
├── ./gc0308.c
├── ./gc0309.c
├── ./gc0328.c
├── ./gc0329.c
├── ./gc2015.c
├── ./gc2035.c
├── ./hm5065.c
├── ./hm5065.h
├── ./ov2659.c
├── ./ov5640_af_firmware.c
├── ./ov5640.c
├── ./ov5640.h
├── ./generic_sensor.c
├── ./generic_sensor.h

为了简化模组驱动调试，目前模组驱动接口统一做到generic_sensor.c ，generic_sensor.h 这两个文件。
驱动主要围绕v4l2_subdev_core_ops ，v4l2_subdev_video_ops 这两个结构体来实现：
```c
static struct v4l2_subdev_core_ops sensor_subdev_core_ops = {\
	.init		= generic_sensor_init,\
	.g_ctrl 	= generic_sensor_g_control,\
	.s_ctrl 	= generic_sensor_s_control,\
	.g_ext_ctrls		  = generic_sensor_g_ext_controls,\
	.s_ext_ctrls		  = generic_sensor_s_ext_controls,\
	.g_chip_ident	= generic_sensor_g_chip_ident,\
	.ioctl = generic_sensor_ioctl,\
	.s_power = generic_sensor_s_power,\
};\
\
static struct v4l2_subdev_video_ops sensor_subdev_video_ops = {\
	.s_mbus_fmt = generic_sensor_s_fmt,\
	.g_mbus_fmt = generic_sensor_g_fmt,\
    .cropcap = generic_sensor_cropcap,\
	.try_mbus_fmt	= generic_sensor_try_fmt,\
	.enum_mbus_fmt	= generic_sensor_enum_fmt,\
	.enum_frameintervals = generic_sensor_enum_frameintervals,\
	.s_stream   = generic_sensor_s_stream,\
	.enum_framesizes = generic_sensor_enum_framesizes,\
};\
```
sensor_probe（）函数v4l2_i2c_subdev_init（）将sensor_ops加入v4l2_subdev->ops中去了。保证v4l2_subdev和i2c_client能够互相找到，使得soc_camera子系统能够顺利调用相关的ops 。


模组驱动文件（如ov5640.c）则主要填充初始化，预览，录像，全分辨率拍照，白平衡，曝光度等系列。
```
sensor_init_data[]
sensor_preview_data[]
sensor_720p[]
sensor_1080p[]
sensor_fullres_lowfps_data[]
sensor_fullres_highfps_data[]
sensor_WhiteBalanceSeqe[]
sensor_ExposureSeqe[]
```

arch/arm/mach-rockchip/rk_camera.c文件实现对摄像头dts配置的解析，并对摄像头的供电，pwrdn,rst,等进行控制。
```c
rk_dts_sensor_probe()   //摄像头dts配置的解析
rk_sensor_power()      //对摄像头供电进行控制
rk_sensor_ioctrl()      //对pwrdn,rst等io进行控制
```

## 调试流程
### 驱动移植
参考现在的驱动进行驱动移植，注意总线参数配置。
```
#define SENSOR_BUS_PARAM (V4L2_MBUS_MASTER
                           |V4L2_MBUS_PCLK_SAMPLE_RISING
                           |V4L2_MBUS_HSYNC_ACTIVE_HIGH
                           |V4L2_MBUS_VSYNC_ACTIVE_LOW
                           |V4L2_MBUS_DATA_ACTIVE_HIGH  
                           |SOCAM_MCLK_24MHZ)
```
rk3288-cif-sensor.dtsi 根据硬件原理图配置 PWRDN(power down)、PWR(power)、RESET 等 IO 信息 和 I2C、CIF 通道：
DTS 中有很多宏 是在 kernel/arch/arm/mach-rockchip/rk3288-cif-sensor.dtsi 中定义的
```dtsi
gc0308{
			is_front = <1>;		//前置后置
			rockchip,power = <&gpio2 GPIO_B2 GPIO_ACTIVE_HIGH>; 			//PWR 脚
			rockchip,powerdown = <&gpio1 GPIO_B2 GPIO_ACTIVE_HIGH>;	   //PWRDN 脚
			pwdn_active = <gc0308_PWRDN_ACTIVE>;									  
			pwr_active = <PWR_ACTIVE_HIGH>;
			mir = <0>;																							   //是否镜像
			flash_attach = <0>;																				 //是否可用闪光灯
			resolution = <gc0308_FULL_RESOLUTION>;								      //分辨率
			powerup_sequence = <gc0308_PWRSEQ>;
			orientation = <0>;		
			i2c_add = <gc0308_I2C_ADDR>;
			i2c_rata = <100000>;
			i2c_chl = <1>;
			cif_chl = <0>;
			mclk_rate = <24>;
		};
```
Rk3288 ,rk3368 配置对应的cam_board.xml文件：
```xml
				<Sensor>
					<SensorName name="OV8858" ></SensorName>
					<SensorLens name="LG-9569A2"></SensorLens>
					<SensorDevID IDname="CAMSYS_DEVID_SENSOR_1B"></SensorDevID>
					<SensorHostDevID busnum="CAMSYS_DEVID_MARVIN" ></SensorHostDevID>
					<SensorI2cBusNum busnum="3"></SensorI2cBusNum>
					<SensorI2cAddrByte byte="2"></SensorI2cAddrByte>
					<SensorI2cRate rate="100000"></SensorI2cRate>
					<SensorMclk mclk="24000000"></SensorMclk>
					<SensorAvdd name="NC" min="0" max="0"></SensorAvdd>
					<SensorDovdd name="NC" min="18000000" max="18000000"></SensorDovdd>
					<SensorDvdd name="NC" min="0" max="0"></SensorDvdd>
					<SensorGpioPwdn ioname="RK30_PIN2_PB7" active="0"></SensorGpioPwdn>
					<SensorGpioRst ioname="NC" active="0"></SensorGpioRst>
					<SensorGpioPwen ioname="RK30_PIN0_PC1" active="1"></SensorGpioPwen>
					<SensorFacing facing="back"></SensorFacing>
					<SensorInterface interface="MIPI"></SensorInterface>
					<SensorMirrorFlip mirror="0"></SensorMirrorFlip>
					<SensorOrientation orientation="0"></SensorOrientation>
					<SensorPowerupSequence seq="1234"></SensorPowerupSequence>					
				<SensorFovParemeter h="60.0" v="60.0"></SensorFovParemeter>
					<SensorAWB_Frame_Skip fps="15"></SensorAWB_Frame_Skip>					
					<SensorPhy phyMode="CamSys_Phy_Mipi" lane="2"  phyIndex="1" sensorFmt="CamSys_Fmt_Raw_10b"></SensorPhy>
				</Sensor>
```
USB摄像头主要注意确认如下配置是否选上：

```c
Device Drivers ‐‐‐>
    <*> Multimedia support ‐‐‐>
        [*] Media USB Adapters ‐‐‐>
              <*> USB Video Class (UVC)
```

### 驱动调试
编译烧录后，先确认 i2c 能否正常通信，video 节点是否创建。打开摄像头应用看图像数据是否接受成功，预览图像是否正常显示，如果没有注意检查 SENSOR_BUS_PARAM 是否设置正确。

## 问题汇总
### i2c通讯异常
确认i2c 通道和地址配置是否正确；
检查pwdn,pwr,reset配置和模组接口是否和硬件匹配；
实地测量pwdn,reset，mclk,摄像头供电输出；
注意IO电压的一致性。
### 收不到图像数据

#### DVP接口模组
确认cif通道是否配对；
确认模组排线是否太长，是否有干扰,是否两个摄像头都处于工作状态；
加强模组驱动能力；
测量时钟数据波形。

#### MIPI 接口模组
确认MIPI通道是否配置正确；
Lane 数是否配置正确；
测试数据波形，确认信号质量。

### 摄像头角度
判断拍照和预览角度是否一致，调整配置角度；
判断偏的角度是180度还是mirror,flip,调整模组寄存器；
如果偏90度，确认模组打样，模组长边是否和屏的长边平行。

### 摄像效果问题
观察具体效果，如果只是前帧有问题，可以通过前帧过滤进行处理；
如果是曝光度问题，可以调整默认曝光度进行调整；
如果是图像边界上有几个像素的花条，可以通过CIF控制器少采几行的方法绕过去。
其它色彩，白平衡等效果问题soc sensor找模组原厂支持,如果是rk3288 ,rk3368 上的mipi rawdata sensor 则需要确认模组是否我们这边已调过，如果没有要申请效果调试。

### 功耗大
确认摄像头是否常供电，调整通过mpu 或者 IO去控制供电开关；
确认摄像头不活动时，模组相关IO是否设为高组态：
如gc2035设为高阻态和恢复输出设置：
```c
static int sensor_activate_cb(struct i2c_client *client)
{
	sensor_write(client, 0xf2, 0x70);  //正常输出
	sensor_write(client, 0xf3, 0xff);
	sensor_write(client, 0xf5, 0x30);
	return 0;
}
/*
* the function is called in close sensor
*/
static int sensor_deactivate_cb(struct i2c_client *client)
{
	sensor_write(client, 0xf2, 0x00);  //高阻态
	sensor_write(client, 0xf3, 0x00);
	sensor_write(client, 0xf5, 0x00);
	return 0;
}
```


















## 启动流程
### mediaservice
#### init.rc 文件
```rc
service media /system/bin/mediaserver
	class	main
	user	media
    group audio camera inet net_bt net_bt_admin net_bw_acct drmrpc mediadrm radio
    ioprio rt 4
```
在启动 mediaserver 的时候
#### main_mediaserver.cpp
```cpp
int main(int argc,char** argv)
{
	AudioFlinger::instantiate();
    MediaPlayerService::instantiate();
    CameraService::instantiate();	//cameraservice 启动
    registerExtensions();
    ProcessState::self()->startThreadPool();
    IPCThreadState::self()->joinThreadPool();
}
```
启动服务中有个关键函数：
```cpp
camera_get_number_of_cameras
//用来获取 camera 的个数和 camera 相关参数
```
```
#define CAMERAS_SUPPORT_MAX 2
rk_cam_info_t gCamInfos[CAMERAS_SUPPORT_MAX];
static signed int gCamerasNumber
```
获取参数到 gCamInfos 中，这里也可以看到最多支持两个摄像头。
### v4l2_subdev
v4l2_device 下面一个层次是 v4l2_subdev
如果说 camera host 是一个 v4l2_device，则 camera 模组 是一个 v4l2_subdev
host 和 模组之间的通信一般采用 I2C。

Camera 驱动文件和 v4l2_device 都在 kernel/drivers/media/video 下面。
其中代码比较简单，是一些寄存器数组和简单寄存器逻辑判断组成（如 af），数组包括初始化，预览分辨率，最大分辨率，还有各种效果如曝光，白平衡等需要设置的寄存器组，和设置它们的函数。

### v4l2_device
如上面所说，camera host 是一个 v4l2_device 设备，即我们的 CIF 相关的驱动。CIF 驱动较 sub_dev 复杂一点。


![](http://ww4.sinaimg.cn/large/ba061518gw1f6e8brzm1jj20mh0dntc1.jpg)
