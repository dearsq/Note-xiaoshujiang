---
title: [RK3399] Camera 驱动代码浅析（一）Linux 中的 V4L2
tags: camera
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 

[TOC]

## Linux 中的 V4L2

以 Video Capture Interface 为例来分析从下到上其代码流程。

![视频采集流程][1]

### 1. 打开设备文件
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
### 2. 取得设备所提供的功能（Capability）
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

### 3.  取得/设定视频所支持的制式
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

### 4. 向驱动申请帧缓存
通过 IOCTL 申请存储空间（帧缓存）来存放我们采集到的视频。一般不超过 5 个。
```
struct v4l2_requestbuffers req;
if ( ioctl (fd,VIDIOC_REQBUFS, &req ) == -1) {
    return -1;
}
```
v4l2_requestbuffers 中会定义缓存的数量，驱动据此申请对应数量的视频缓存。

### 5. 获取每个缓存的信息 并 映射到用户空间（mmap）
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

### 6. 启动视频采集
存储空间 OK ， 接下来应该开始捕获视频数据。

> Linux OS 将系统使用的内存划分为 用户空间 和 内核空间。
> 应用程序可以直接访问 用户空间 的内存的地址，不可以访问 内核空间。
> 但是 V4L2 捕获的数据最初是存放在 内核空间的，所以应用程序需要通过某些手段转换地址，进而访问该段内存。

三种视频采集方式：
1）read、write
2）mmap 内存映射
3）userptr 用户指针：内存由应用程序分配，并把地址传递到内核中的驱动程序，由 V4L2 驱动程序直接将数据填充到用户空间的内存中。（v4l2_requestbuffers.memory 设置为 V4L2_MEMORY_USERPTR）。

userptr > mmap > read/write 

调用 IOCTL 的 VIDIOC_STREAMON 命令来启动视频采集。
```
int buf_type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
int ret = ioctl ( fd, VIDIOC_STREAMON, &buf_type );
```

### 7. 环形缓冲队列的处理
通过 IOCTL 的 VIDIOC_DQBUF 和 VIDIOC_QBUF：
取出 FIFO 缓存中已采样的帧缓存，将处理完的缓存放在缓存队列尾部，以便视频采集过程可以循环使用他们。
流程如下图：

![Buffer 管理][2]

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
### 8. 停止视频采集
通过 IOCTL 停止视频采集：
```
int ret = ioctl (fd, VIDIOC_STREAMOFF, &buf_type);
```
### 9. 关闭相应设备
```
close(fd);
```

归纳其视频采集流程如下图：

![视频采集流程][3]


##  Android 上层中的 V4L2

为了让 Android 上层利用到 Camera 驱动、利用 Camera 模组采集想要的视频图像数据，我们也应该 Android 的 Framework 实现相应的 HAL 与 Service 。 如图：

![Android Camera 系统架构图][4]


  [1]: http://wx2.sinaimg.cn/large/ba061518ly1fgqotebmf2j208u08fjs0.jpg
  [2]: http://img.my.csdn.net/uploads/201211/16/1353038230_2495.png
  [3]: http://img.my.csdn.net/uploads/201211/16/1353038220_9320.png
  [4]: http://wx3.sinaimg.cn/large/ba061518ly1fgrn51p62dj20o70nj79a.jpg