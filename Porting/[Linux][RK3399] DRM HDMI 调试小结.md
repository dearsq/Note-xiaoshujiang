---
title: [Linux][RK3399] HDMI 调试小结
tags: hdmi,rockchip
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 

## 调试流程

### 确认板子是否识别到了显示器的 EDID
```
 echo 0x1f > /sys/module/drm/parameters/debug
```
插拔一下hdmi
然后dmesg | grep drm, 看看里面的信息是否解析到了edid
```
[  405.576876] EDID block is all zeroes
[  405.577224] rockchip-drm display-subsystem: HDMI-A-1: EDID block 0 invalid.
[  405.687232] EDID block is all zeroes
[  405.687590] rockchip-drm display-subsystem: HDMI-A-1: EDID block 0 invalid.
```
EDID = 0 
这个就是显示器被识别为DVI的主因, 当无法读出edid时, hdmi驱动可能就会以dvi显示输出

### 测一下hdmi驱动是否可以支持hdmi输出
使能 CONFIG_DRM_LOAD_EDID_FIRMWARE
（参考 https://markyzq.gitbooks.io/rockchip_drm_integration_helper/content/zh/drm_config_load_firmware.html ）


将附件的 acer_edid.bin 推到板子上, 以下是android上的例子, linux上也可以进行类似操作
```
adb push acer_edid.bin /data
adb shell:
   mount -o rw,remount /
   cp /data/acer_edid.bin /lib/firmware/
   echo HDMI-A-1:acer_edid.bin > /sys/module/drm_kms_helper/parameters/edid_firmware
```
采用 acer_edid.bin 模拟 EDID 后分辨率由 DVI 800×600@60HZ 变为 DVI 1920×1080@60HZ 。但是依旧无法识别 HDMI。
热插拔信息：
```
[  211.948958] [drm:edid_load] Got external EDID base block and 1 extension from "acer_edid.bin" for connector "HDMI-A-1"
[  211.949953] [drm:drm_edid_block_valid] *ERROR* EDID checksum is invalid, remainder is 4
[  212.066567] [drm:edid_load] Got external EDID base block and 1 extension from "acer_edid.bin" for connector "HDMI-A-1"
[  212.067598] [drm:drm_edid_block_valid] *ERROR* EDID checksum is invalid, remainder is 4
```


## 错误信息
### No drm_driver.set_busid() implementation provided by 0x.... Use drm_dev_set_unique() to set the unique

1）dev->driver->set_busid 回调没有被赋值
2）dev->unique == NULL 

set_busid 没有对应回调是正常的，RK 平台未对其进行实现，一般在 PC 平台会对其进行实现。

dev->unique == NULL 不正常。
RK VR SDK 中 DRM 框架太旧了，通过升级 DRM 框架解决。

#### drivers/gpu/drm/rockchip/rockchip_drm_fbdev.c:64:2: error: unknown field 'fb_dmabuf_export' specified in initializer
  .fb_dmabuf_export = rockchip_fbdev_get_dma_buf,

/home/younix/rk_op_linux_3399/kernel/include/linux/fb.h
```
	/* Export the frame buffer as a dmabuf object */
	struct dma_buf *(*fb_dmabuf_export)(struct fb_info *info);
```

#### kernel/drivers/gpu/drm/drm_prime.c:545: undefined reference to 'dma_buf_get_release_callback_data'

需要对比修改 文件：/home/younix/rk_op_linux_3399/kernel/drivers/dma-buf/dma-buf.c

## 参考资料
Kernel Doc
https://www.kernel.org/doc/htmldocs/drm/ 
The DRM/KMS subsystem from a newbie's point of view 
http://events.linuxfoundation.org/sites/events/files/slides/brezillon-drm-kms.pdf
DRM Maintainer 总结的资料：https://markyzq.gitbooks.io/rockchip_drm_integration_helper/content/zh/
