---
title: [RK3399] Camera（二）Linux 中的 V4L2
tags: camera
grammar_cjkRuby: true
---

Platform: RK3399
OS: Android 6.0
Kernel: 4.4
Version: v2017.04

[TOC]

## 什么是 V4L2
Video for Linux 2 是 Linux 内核中关于视频设备的内核驱动框架，为上层访问底层设备提供了统一的接口。
一共支持 5 类设备，视频采集（输入）设备、视频输出设备、直接传输接口（Output Overlay）、视频间隔消隐信号接口（VBI）、收音机（radio）。
我们本文只讨论 Camera，也就是 视频采集设备。

## Linux 中的 V4L2

### 1. 整体结构

本小节参考归纳自 廖老师的内容：http://blog.csdn.net/paul_liao/article/details/8915781

![V4L2 在 Linux 中的结构图][1]

可以看到整个结构包括四个部分：

1. 字符设备驱动核心： V4L2 本身为一个字符设备（Chrdev），具有字符设备的所有特性。
2. V4L2 核心：用来构建一个内核中标准视频设备的框架，为视频操作提供统一接口。 drivers/media/v4l2-core
3. 平台 V4L2 设备驱动：在 V4L2 框架下，根据平台自身特性实现与平台相关的 V4L2 驱动部分，包括注册 video_device 和 v4l2_dev。
4. 具体 sensor 驱动：实现各种设备控制方法供上层调用，完成 上电、提供工作时钟、视频图像裁剪、流 IO 开启等功能。

重点在于上面第二部分 V4L2 核心 ，drivers/media/v4l2-core 中的代码按照功能又可以分为四类：
1. 核心模块实现 v4l2-dev.c ：申请 Chardev，注册 Class，提供 Video Device 注册 注销等函数。
2. 框架 v4l2-device.c v4l2-subdev.c v4l2-fh.c v4l2-ctrls.c：构建 V4L2 框架。
3. Videobuf 管理 videobuf2-core2.c videobuf2-dma-contig.c videobuf2-dma-sg.c videobuf2-memops.c videobuf2-vmalloc.c v4l2-mem2mem.c ：完成 VideoBuffer 的分配、管理、注销
4. IOCTL 框架，v4l2-ioctl.c ：构建 V4L2 Ioctl 框架。

### 2. v4l2 框架部分代码分析
这部分的文件在 v4l2-device.c v4l2-subdev.c v4l2-fh.c v4l2-ctrls.c
v4l2-device.c 中，
v4l2_device 充当了父设备，通过链表将注册到其下的所有子设备（Grabber采集器、VBI、Radio）管理起来。
v4l2_subdev 是子设备，其包含了对设备操作的 ops 和 ctrls。
video_device 用于创建子设备节点，将操作设备的接口暴露给用户空间。
v4l2_fh 是每个子设备的句柄，在打开设备节点文件时设置，方便上层索引到 v4l2_ctrl_handler，后者用来管理设备，包括调节饱和度、对比度、白平衡等。

#### **v4l2_device**
```c
struct v4l2_device {
         structlist_head subdevs;    //用链表管理注册的subdev
         charname[V4L2_DEVICE_NAME_SIZE];    //device 名字
         structkref ref;      //引用计数
         ……
};
//V4l2_device的注册和注销：
int v4l2_device_register(struct device*dev, struct v4l2_device *v4l2_dev)
static void v4l2_device_release(struct kref *ref)
```
#### **v4l2_subdev**
子设备 v4l2_subdev 中包含了其相关的属性和操作
```c
struct v4l2_subdev {
 		//指向父设备
         structv4l2_device *v4l2_dev;
		 //提供一些控制v4l2设备的接口
         conststruct v4l2_subdev_ops *ops;
		 //向V4L2框架提供的接口函数。只能被V4L2框架层调用。在注册或打开子设备时，进行一些辅助性操作。
         conststruct v4l2_subdev_internal_ops *internal_ops;
		 //subdev控制接口
         structv4l2_ctrl_handler *ctrl_handler;
         /* namemust be unique */
         charname[V4L2_SUBDEV_NAME_SIZE];
         /*subdev device node */
         structvideo_device *devnode;  
};
struct v4l2_subdev_ops {
		//视频设备通用的操作：初始化、加载FW、上电和RESET等
         conststruct v4l2_subdev_core_ops        *core;
		//tuner特有的操作
         conststruct v4l2_subdev_tuner_ops      *tuner;
		//audio特有的操作
         conststruct v4l2_subdev_audio_ops      *audio;
		//视频设备的特有操作：设置帧率、裁剪图像、开关视频流等
         conststruct v4l2_subdev_video_ops      *video;
…
};
//Subdev 的注册和注销
int v4l2_device_register_subdev(struct v4l2_device*v4l2_dev, struct v4l2_subdev *sd);
void v4l2_device_unregister_subdev(struct v4l2_subdev*sd);
```
每个子设备驱动都要实现一个 v4l2_subdev 结构体，它可以内嵌到其他结构体中，也可以独立使用。

#### **video_device**
用于在 /dev 目录下生成设备文件，把操作设备的接口暴露给用户空间。
```c
struct video_device
{
         conststruct v4l2_file_operations *fops;  //V4L2设备操作集合

         /*sysfs */
         structdevice dev;             /* v4l device */
         structcdev *cdev;            //字符设备

         /* Seteither parent or v4l2_dev if your driver uses v4l2_device */
         structdevice *parent;              /* deviceparent */
         structv4l2_device *v4l2_dev;          /*v4l2_device parent */

         /*Control handler associated with this device node. May be NULL. */
         structv4l2_ctrl_handler *ctrl_handler;

         /* 指向video buffer队列*/
         structvb2_queue *queue;
         intvfl_type;      /* device type */
         intminor;  //次设备号

         /* V4L2file handles */
         spinlock_t                  fh_lock; /* Lock for allv4l2_fhs */
         structlist_head        fh_list; /* List ofstruct v4l2_fh */

         /*ioctl回调函数集，提供file_operations中的ioctl调用 */
         conststruct v4l2_ioctl_ops *ioctl_ops;
         ……
};
//Video_device 分配和释放，用于分配和释放 video_device 结构体
struct video_device *video_device_alloc(void);
void video_device_release(struct video_device *vdev);
//Video_device 的注册和注销
static inline int __must_check video_register_device(struct video_device *vdev, int type, int nr);
void video_unregister_device(struct video_device* vdev);
//type 是设备类型：VFL_TYPE_GRABBER、VFL_TYPE_VBI、VFL_TYPE_RADIO和VFL_TYPE_SUBDEV。
//nr 是设备节点名标号：/dev/video[nr]
```

#### **v4l2_fh** 和 **v4l2_ctrl_handler**
v4l2_fh 是用来 保存 subdev 特有的操作（v4l2_ctrl_handler），内核提供一组 v4l2_fh 的操作方法，一般在打开设备节点时进行注册。
```c
//初始化v4l2_fh，添加v4l2_ctrl_handler到v4l2_fh：
void v4l2_fh_init(struct v4l2_fh *fh, structvideo_device *vdev);
//添加v4l2_fh到video_device，方便核心层调用到：
void v4l2_fh_add(struct v4l2_fh *fh)
```
v4l2_ctrl_handler 是用于保存子设备控制方法集的结构体。
对于视频设备这些ctrls包括设置亮度、饱和度、对比度和清晰度等。
用链表的方式来保存ctrls，可以通过v4l2_ctrl_new_std函数向链表添加ctrls。
```c
struct v4l2_ctrl *v4l2_ctrl_new_std(structv4l2_ctrl_handler *hdl,
                            conststruct v4l2_ctrl_ops *ops,
                            u32id, s32 min, s32 max, u32 step, s32 def)
//hdl是初始化好的v4l2_ctrl_handler结构体；
//ops是v4l2_ctrl_ops结构体，包含ctrls的具体实现；
//id是通过IOCTL的arg参数传过来的指令，定义在v4l2-controls.h文件；
//min、max用来定义某操作对象的范围。如：
v4l2_ctrl_new_std(hdl, ops, V4L2_CID_BRIGHTNESS,-208, 127, 1, 0);
//用户空间可以通过ioctl的VIDIOC_S_CTRL指令调用到v4l2_ctrl_handler，id透过arg参数传递
```

### 3. Ioctl 框架部分代码分析
以 Video Capture Interface 为例来分析从下到上其 ioctl 接口代码流程。

用户空间通过打开 /dev/ 目录下的设备节点，获取到文件的 file 结构体，
通过系统调用 ioctl 把 cmd 和 arg 传到内核。
通过一系列的调用，
最终调用到 \_\_video_do_ioctl 函数，
然后通过 cmd 检索 v4l2_ioctls[]，判断是 INFO_FL_STD 还是 INFO_FL_FUNC ，
如果是 INFO_FL_STD ，会直接调用到视频设备驱动中的 video_device->v4l2_ioctl_ops 函数集
如果是 INFO_FL_FUNC，会先调用到 V4L2 自己实现的标准回调函数，然后根据 arg 再调用到 video_device->v4l2_ioctl_ops 或 v4l2_fh->v4l2_ctl_handler 函数集。

![视频采集流程][2]

#### 3.0 IO 访问的三种方式
根据 IO 访问的方式不同，我们视频采集的方式自然也有三种
1. read/write
2. V4L2_MEMORY_MMAP
3. V4L2_MEMORY_USERPTR

我们采用的是第二种 mmap 内存映射缓存区的方式。
当 Camera Sensor 捕捉到图像并通过并口 或者 MIPI 传输到 CAMIF ，CAMIF 可以对图像数据进行调整（裁剪、翻转、格式转换）。
之后 DMA 控制器设置 DMA 通道请求 AHB 将图像数据传到分配好的 DMA 缓冲区。
之后 mmap 操作将缓冲区映射到用户空间，应用就可以直接访问缓冲区的数据。

#### 3.1 打开设备文件
两种方式：
1）非阻塞
```
int cameraFd;
cameraFd = open("/dev/video0", O_RDWR | O_NONBLOCK, 0);
```
这种模式下，即使没有捕获到视频信息，也要把缓存 DQBUFF 中的内容返回给上层应用。
2）阻塞
```
cameraFd = open("/dev/video0". O_RDWR, 0);
```
#### 3.2 取得设备所提供的功能（Capability）
通过 IOCTL 获得设备提供的功能（Capability）即查询设备属性，包括：可读、可写、调制方式、支持 VBI。
capabilities 常用值:  
V4L2_CAP_VIDEO_CAPTURE    // 是否支持图像获取  
```
struct v4l2_capability capability;
int ret = ioctl(fd, VIDIOC_QUERYCAP, &capability);
```
```
structv4l2_capability  
{  
	__u8 driver[16];     // 驱动名字  
	__u8 card[32];       // 设备名字  
	__u8bus_info[32]; // 设备在系统中的位置  
	__u32 version;       // 驱动版本号  
	__u32capabilities;  // 设备支持的操作  
	__u32reserved[4]; // 保留字段  
};  
```

#### 3.3  取得/设定视频所支持的制式
通过 IOCTL 取得或者设定 视频制式。就电视而言，我国是 PAL，欧洲国家为 NTSC。
获得：
```
v4l2_std_id std;
do {
    ret = ioctl(fd,VIDIOC_QUERYSTD, &std);
} while (ret == -1 && errno == EAGAIN);
switch (std) {
    case V4L2_STD_NTSC:
	    //....
	case V4L2_STD_PAL:
	    //....
}
```
设置：
```
struct v4l2_format fmt;
memset (&fmt, 0 ,sizeof(fmt) );
fmt.type				= V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width	= 720;
fmt.fmt.pix.height	= 576;
fmt.fmt.pix.field	= V4L2_PIX_FMT_YUYV;
fmt.fmt.pix.field	= V4L2_FIELD_INTERLACED;
if ( ioctl (fd, VIDIOC_S_FMT, &fmt) == -1 ) {
	return -1;
}
```

#### 3.4 向驱动申请帧缓存
通过 IOCTL 申请存储空间（帧缓存）来存放我们采集到的视频。一般不超过 5 个。
```
struct v4l2_requestbuffers req;
if ( ioctl (fd,VIDIOC_REQBUFS, &req ) == -1) {
    return -1;
}
```
v4l2_requestbuffers 中会定义缓存的数量，驱动据此申请对应数量的视频缓存。

#### 3.5 获取每个缓存的信息 并 映射到用户空间（mmap）
通过 IOCTL VIDIOC_QUERYBUF 获取帧缓存地址。
利用 **mmap**() 转换成上层的绝对地址，**并将这个帧缓存放在缓存队列中**，以便存放采集到的数据。
```
typedef struct VideoBuffer {
	void *start;
	size_t length;
} VideoBuffer;

VideoBuffer* buffers = calloc( req.count, sizeof(*buffers) );
struct v4l2_buffer buf; //声明一个视频帧

//对帧缓存中的视频帧进行映射
for (numBufs = 0; numBufs < req.count; numBufs++) {
	memset ( &buf, 0 , sizeof(buf) );
	buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE; //采集类
	buf.memory = V4L2_MEMORY_MMAP;
	buf.index = numBufs;
	// 获取缓存帧信息
	if ( ioctl ( fd, VIDIOC_QUERYBUF, &buf) == -1 ) {
		return -1;
	}

	buffers[numBufs].length = buf.length;
	//转换成绝对地址
	buffers[numBufs].start = mmap (NULL, buf.length.
													PROT_READ | PORT_WRITE,
													MAP_SHARED,
													fd, buf.m.offset );
	if ( buffers[numBufs].start == MAP_FAILED) {
		return -1;
	}

	// 放入缓存队列，以便存放采集到的数据
	if (ioctl (fd, VIDIOC_QBUF, &buf ) == -1) {
		return -1;
	}
}
```

#### 3.6 启动视频采集
存储空间 OK ， 接下来应该开始捕获视频数据。

> Linux OS 将系统使用的内存划分为 用户空间 和 内核空间。
> 应用程序可以直接访问 用户空间 的内存的地址，不可以访问 内核空间。
> 但是 V4L2 捕获的数据最初是存放在 内核空间的，所以应用程序需要通过某些手段转换地址，进而访问该段内存。

三种视频采集（IO访问）方式：
1）read、write
2）mmap 内存映射
3）userptr 用户指针：内存由应用程序分配，并把地址传递到内核中的驱动程序，由 V4L2 驱动程序直接将数据填充到用户空间的内存中。（v4l2_requestbuffers.memory 设置为 V4L2_MEMORY_USERPTR）。

userptr > mmap > read/write

调用 IOCTL 的 VIDIOC_STREAMON 命令来启动视频采集。
```
int buf_type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
int ret = ioctl ( fd, VIDIOC_STREAMON, &buf_type );
```

#### 3.7 环形缓冲队列的处理
通过 IOCTL 的 VIDIOC_DQBUF 和 VIDIOC_QBUF：
取出 FIFO 缓存中已采样的帧缓存，将处理完的缓存放在缓存队列尾部，以便视频采集过程可以循环使用他们。
流程如下图：

![Buffer 管理][3]

代码如下：
```
struct v4l2_buffer buf;
memset （&buf, 0 ,sizeof( buf ) );
buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buf.memory = V4L2_MEMORY_MMAP;
buf.index = 0;
//读缓存
if ( ioctl (cameraFd, VIDIOC_DQBUF, &buf) == -1)
{
	return -1;
}
//... 视频处理算法
//重新放入缓存队列
if ( ioctl (cameraFd, VIDIOC_QBUF, &buf) == -1)
{
	return -1;
}
```
#### 3.8 停止视频采集
通过 IOCTL 停止视频采集：
```
int ret = ioctl (fd, VIDIOC_STREAMOFF, &buf_type);
```
#### 3.9 关闭相应设备
```
close(fd);
```

归纳其视频采集流程如下图：

![视频采集流程][4]


##  Android 上层调用 V4L2 接口

为了让 Android 上层利用到 Camera 驱动、利用 Camera 模组采集想要的视频图像数据，我们也应该 Android 的 Framework 实现相应的 HAL 与 Service 。 如图：

![Android Camera 系统架构图][5]


  [1]: http://wx2.sinaimg.cn/large/ba061518ly1fgsk63wmkej20h70fitbm.jpg
  [2]: http://wx2.sinaimg.cn/large/ba061518ly1fgqotebmf2j208u08fjs0.jpg
  [3]: http://img.my.csdn.net/uploads/201211/16/1353038230_2495.png
  [4]: http://img.my.csdn.net/uploads/201211/16/1353038220_9320.png
  [5]: http://wx3.sinaimg.cn/large/ba061518ly1fgrn51p62dj20o70nj79a.jpg
