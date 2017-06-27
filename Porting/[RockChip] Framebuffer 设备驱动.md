---
title: [RockChip] Framebuffer 设备驱动
tags: rockchip,framebuffer
grammar_cjkRuby: true
---

## 概念
FrameBuffer 的意思是，帧缓冲。
Frame 帧：你所看到的屏幕的图像，或者在一个窗口中的图像，就叫一帧。
Buffer 缓冲：一段RAM，用来暂存图像数据，这些数据会被直接写入到显示设备。
帧缓冲就相当于介于 图形操作 和 图像输出中间的一个中间人。将程序对图形数据的处理操作，反馈到显示输出上。
**显卡**（显存中的数据） <-> **帧缓冲**（程序对其中的数据进行处理） <-> **显示器**（输出图像）
**帧缓冲可用于，实现原先视频卡并不支持的分辨率:**
显卡可能并不支持你当前某个更大分辨率的显示器，但是可以通过帧缓冲获取显卡的显存中的数据，处理之后，实现更大的分辨率的图像，然后将数据直接输出到显示器上。

## 驱动分析
### 1.Framebuffer帧缓冲设备
#### 1) 重要结构
	Framebuffer 驱动在 Linux 中是标准的显示设备的驱动。
    对于 **PC 系统**，它是显卡的驱动 ；
    对于**嵌入式SOC处理器系统**，它是 LCD 控制器或者其他显示控制器的驱动。
    同时该设备属于一个字符设备，在文件系统中设备节点是 /dev/fbx。    
	一个系统可以有多个显示设备，最常见的有 /dev/fb0    /dev/fb1 ,如果在/dev目录下没有发现这个文件，那么需要去修改 Linux 系统中相应的配置脚本。
     在**安卓系统**中，Framebuffer设备驱动的主设备号通常为 29 ，次设备号递增而生成。
     在此，我借用某内核驱动大牛GQB做的驱动框架图做分析，如有侵权，请联系我删除，谢谢！   
     Framebuff的结构框架和实现：     
![](https://ws2.sinaimg.cn/large/ba061518gw1f7jkue0g3hj20lh0cfq5l.jpg)

我们可以先来看看在framebuffer驱动框架中相关的重要数据结构：
```c
struct fb_ops {
    struct module *owner;
    //检查可变参数并进行设置
    int (*fb_check_var)(struct fb_var_screeninfo *var, struct fb_info *info);
    //根据设置的值进行更新，使之有效
    int (*fb_set_par)(struct fb_info *info);
    //设置颜色寄存器
    int (*fb_setcolreg)(unsigned regno, unsigned red, unsigned green,
                unsigned blue, unsigned transp, struct fb_info *info);
    //显示空白
    int (*fb_blank)(int blank, struct fb_info *info);
    //矩形填充
    void (*fb_fillrect) (struct fb_info *info, const struct fb_fillrect *rect);
    //复制数据
    void (*fb_copyarea) (struct fb_info *info, const struct fb_copyarea *region);
    //图形填充
    void (*fb_imageblit) (struct fb_info *info, const struct fb_image *image);
};
```
这个结构体记录了这个设备驱动的全部相关的信息，
其中就包括设备的设置参数，状态，还有对应底层硬件操作的回调函数。
在Linux中，每一个帧缓冲设备都必须对应一个fb_info，fb_info在/linux/fb.h中：
```c
struct fb_info {
     int node;//驱动的次设备号
     struct fb_var_screeninfo var;
     /* Current var 结构体成员记录用户可修改的显示控制器参数,包括屏幕分辨率还有每个像素点的位数 */
     struct fb_fix_screeninfo fix;  /* Current fix */
     struct fb_videomode *mode; /* current mode */

     struct fb_ops *fbops;
     struct device *device;   /* This is the parent */
     struct device *dev;   /* This is this fb device */

     char __iomem *screen_base; /* Virtual address */
     unsigned long screen_size; /* Amount of ioremapped VRAM or 0 */
     ……
};
```
#### 2) fbmem.c
和其它的内核代码中的字符驱动类似，同样，如果你要使用这个驱动，你必须去注册这个设备驱动。
显示驱动的分析都是由 drivers/video/fbmem.c 开始 。
我们可以发现 fbmem.c 里定义 register_framebuffer/unregister_framebuffer

由分析可以得知，
drivers/video/rockchip/lcdc/rk3288_lcdc.c 中的 probe 函数(rk3288_lcdc_probe)中有调用 rk_fb_register
drivers/video/rockchip/rk_fb.c 中的 rk_fb_register 调用 register_framebuffer
注册了一个平台总线设备的驱动程序。



-----






编写framebuffer用户态程序需要以下步骤:
1、初始化framebuffer
2、向framebuffer写数据
3、退出framebuffer
```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#define    RGB(r,g,b)((r<<16)|(g<<8)|b)
#define    WIDTH   1280
#define    HIGHT   1024

static int Frame_fd ;
static int *FrameBuffer = NULL ;
static int W , H ;

//写framebuffer
int Write_FrameBuffer(const char *buffer);

int main(void)
{
    1、设置长宽，打开fb设备
    W = 1024 ;
    H = 768 ;
    Frame_fd = open("/dev/fb0" , O_RDWR);
    if(-1 == Frame_fd){
perror("open frame buffer fail");
return -1 ;
    }

    2、对framebuffer进行内存映射mmap
    //头文件 <sys/mman.h>
    //函数原型：void* mmap(void* start,size_t length,int prot,int flags,int fd,off_t offset);
    //start：映射区的开始地址，设置为0时表示由系统决定映射区的起始地址。
    //length：映射区的长度。//长度单位是 以字节为单位，不足一内存页按一内存页处理
    //prot：期望的内存保护标志，不能与文件的打开模式冲突。是以下的某个值，可以通过or运算合理地组合在一起
    //flags:相关的标志，就跟open函数的标志差不多的，自己百度去查
    //fd：有效的文件描述词。一般是由open()函数返回，其值也可以设置为-1，此时需要指定flags参数中的MAP_ANON,表明进行的是匿名映射。
    //off_toffset：被映射对象内容的起点。

    //PROT_READ //页内容可以被读取
    //PROT_WRITE //页可以被写入
    //MAP_SHARED //与其它所有映射这个对象的进程共享映射空间。对共享区的写入，相当于输出到文件。直到msync()或者munmap()被调用，文件实际上不会被更新。
    FrameBuffer = mmap(0, 1280*1024*4 , PROT_READ | PROT_WRITE , MAP_SHARED , Frame_fd ,0 );
    if(FrameBuffer == (void *)-1){
perror("memory map fail");
return -2 ;
    }

    3、对framebuffer写数据
    char buffer[WIDTH*HIGHT*3];  //我们要写入的数据
    while(1) {
    Write_FrameBuffer(buffer);
    printf("count:%d \n" , count++);
    }

    4、退出framebuffer
    munmap(FrameBuffer ,  W*H*4); //解除内存映射
    close(Frame_fd);  //关闭文件描述符
    return 0 ;
}
//写framebuffer
int Write_FrameBuffer(const char *buffer)
{
int row  , col ;
char *p = NULL ;
        //遍历分辨率1024*1280的所有像素点
for(row = 0 ; row <1024 ; row++){
   for(col = 0 ; col < 1280 ;  col++){
       if((row < H)  && (col < W)){
   p = (char *)(buffer + (row * W+ col ) * 3);
     //转RGB格式
   FrameBuffer[row*1280+col] = RGB((unsigned char)(*(p+2)),(unsigned char)(*(p+1)),(unsigned char )(*p));
}
   }
}
return 0 ;
}
```
至此，我们的framebuffer上层调用程序就写完了，当然这个程序你看不到什么图片，只能看到一块被映射的区域，然后printf不断的在打印数据。
    如果你有兴趣，可以写一个图片数据进去，这时候要用到bmp，yuyv格式的图片知识，让图片可以显示在屏幕上.
