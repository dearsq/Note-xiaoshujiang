---
title: [Linux][RK3399] ISP 矫正算法的移植
tags: isp
grammar_cjkRuby: true
---

OS:Debian9
Hardware:RK3399

[TOC]

## 一、搭建编译环境
### 1. 首先需要搭建 Gstreamer 环境
```
$ sudo apt install -y bison flex libffi-dev libmount-dev libpcre3 libpcre3-dev zlib1g-dev libssl-dev gtk-doc-tools build-essential libtool libdrm-dev
```
### 2. 安装移植过程中的工具
如果你是刚搭建好的 OS，可能会碰到一些工具依赖的问题。罗列如下：
#### 1）xz 解压工具
```
# apt install xz-utils
```
#### 2）automake 工具
比如出现如下错误：
`./autogen.sh: 11: ./autogen.sh: autoreconf: not found`
```
# apt install autoconf automake autopoint
```


### 2. 安装 ORC 支持库
在编译 gst-plugins-base 的时候会依赖这个库
```
mkdir ISP_3A_Porting
cd ISP_3A_Porting
wget https://gstreamer.freedesktop.org/src/orc/orc-0.4.27.tar.xz --no-check-certificate

xz -d orc-0.4.27.tar.xz
tar -xvf orc-0.4.27.tar

cd orc-0.4.27
./autogen.sh --prefix=/usr
make
make  install
```

### 3. 安装 GLIB 支持库
```
wget http://ftp.acc.umu.se/pub/GNOME/sources/glib/2.52/glib-2.52.3.tar.xz
# xz -d glib-2.52.3.tar.xz
# tar xvf glib-2.52.3.tar 
# cd glib-2.52.3 
# ./autogen.sh 
# make 
# make install 
```

#### GLIB 所依赖的包
在 `./autogen.sh` 时
```
configure: error: 
*** You must have either have gettext support in your C library, or use the
*** GNU gettext library. (http://www.gnu.org/software/gettext/gettext.html
```
需要
```
apt install gettext
```
### 4. 安装 Gstreamer 程序包
https://gstreamer.freedesktop.org/src/

```
mkdir gstreamer
cd gstreamer
```


```
wget https://gstreamer.freedesktop.org/src/gstreamer/gstreamer-1.12.2.tar.xz
xz -d gstreamer-1.12.2.tar.xz
tar -xvf gstreamer-1.12.2.tar
cd gstreamer-1.12.2
./autogen.sh 
make 
make install
```

```
wget https://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-1.12.2.tar.xz
xz -d gst-plugins-base-1.12.2.tar.xz
tar -xvf gst-plugins-base-1.12.2.tar
cd gst-plugins-base-1.12.2
./autogen.sh 
make 
make install
```

```
wget https://gstreamer.freedesktop.org/src/gst-plugins-good/gst-plugins-good-1.12.2.tar.xz
xz -d gst-plugins-good-1.12.2.tar.xz
tar -xvf gst-plugins-good-1.12.2.tar
cd gst-plugins-good-1.12.2
./autogen.sh 
make 
make install 
```

```
wget https://gstreamer.freedesktop.org/src/gst-plugins-bad/gst-plugins-bad-1.12.2.tar.xz
xz -d gst-plugins-bad-1.12.2.tar.xz
tar -xvf gst-plugins-bad-1.12.2.tar
cd gst-plugins-bad-1.12.2
./autogen.sh 
make 
make install 
```


```
wget https://gstreamer.freedesktop.org/src/gst-plugins-ugly/gst-plugins-ugly-1.12.2.tar.xz
xz -d gst-plugins-ugly-1.12.2.tar.xz
tar -xvf gst-plugins-ugly-1.12.2.tar
cd gst-plugins-ugly-1.12.2
./autogen.sh 
make 
make install 
```

### 5. 安装使用 Gstreamer rkisp elemennt
在开发板上解压并安装 Gstreamer 的  插件 camera-isp-gstreamer-v1.1.2.tar.gz
```
tar -zxvf camera-isp-gstreamer-v1.1.2.tar.gz
cd camera-app-gstreamer
./autogen.sh --prefix=/usr/local --enable-gst --enable-rkiq
make
make install
```

```
     version                    : 1.1.1
     enable debug               : no
     enable profiling           : no
     build GStreamer plugin     : yes
     build aiq analyzer         : no
     use local aiq              : no
     use local atomisp          : yes
     have opencl lib            : yes
     have opencv lib            : no
     enable 3a lib              : no
     enable smart analysis lib  : no
     enable dvs                 : no
     enable libxcam-capi lib    : yes
     enable  lib    : yes
```


#### 解决缺少 libdrm-dev 的问题：
**make[2]: Entering directory '/home/linaro/Desktop/camera-app-gstreamer/xcore'
drm_display.h:30:17: fatal error: drm.h: No such file or directory
 #include <drm.h>**

这实际上是因为 libdrm 没有安装导致的：
```
apt install libdrm-dev
```

#### 
```
root@linaro-alip:/home/linaro/Desktop/camera-app-gstreamer# make
make  all-recursive
make[1]: Entering directory '/home/linaro/Desktop/camera-app-gstreamer'
Making all in xcore
make[2]: Entering directory '/home/linaro/Desktop/camera-app-gstreamer/xcore'
/bin/bash ../libtool  --tag=CXX   --mode=link g++ -fPIC -DSTDC99 -W -Wall -D_REENTRANT -Wformat -Wformat-p
libtool: link: g++  -fPIC -DPIC -shared -nostdlib /usr/lib/gcc/arm-linux-gnueabihf/6/../../../arm-linux-g1
../ext/rkisp/lib/librkisp.so: file not recognized: File format not recognized
collect2: error: ld returned 1 exit status
Makefile:583: recipe for target 'libxcam_core.la' failed
make[2]: *** [libxcam_core.la] Error 1
make[2]: Leaving directory '/home/linaro/Desktop/camera-app-gstreamer/xcore'
Makefile:427: recipe for target 'all-recursive' failed
make[1]: *** [all-recursive] Error 1
make[1]: Leaving directory '/home/linaro/Desktop/camera-app-gstreamer'
Makefile:359: recipe for target 'all' failed
make: *** [all] Error 2
```


这是因为 RK 提供的 librkisp.so 的编译环境和我们不一样。需要提供我们的编译工具 arm-linux-gnueabihf 给他们，重新编译一份 librkisp.so 给我们。

PS: ubuntu 下的编译工具为 /usr/lib/gcc/aarch64-linux-gnu

使用重新编译后的 librkisp.so 后问题解决。

#### opencl 依赖问题

需要参照 https://www.freedesktop.org/wiki/Software/Beignet/


#### 
dpkg: error processing archive /var/cache/apt/archives/ocl-icd-opencl-dev_2.2.11-1_armhf.deb (--unpack):
 trying to overwrite '/usr/lib/arm-linux-gnueabihf/pkgconfig/OpenCL.pc', which is also in package libmali-rk-dev:armhf 1.5-6
Errors were encountered while processing:
 /var/cache/apt/archives/ocl-icd-opencl-dev_2.2.11-1_armhf.deb
E: Sub-process /usr/bin/dpkg returned an error code (1)

```
apt remove libmali-rk
```

#### 
dpkg: error processing archive /var/cache/apt/archives/ocl-icd-opencl-dev_2.2.11-1_armhf.deb (--unpack):
 trying to overwrite '/usr/lib/arm-linux-gnueabihf/libOpenCL.so', which is also in package libmali-rk-midgard-t86x-r14p0:armhf 1.5-6
Errors were encountered while processing:
 /var/cache/apt/archives/ocl-icd-opencl-dev_2.2.11-1_armhf.deb
 
 ```
 apt remove libmali-rk-midgard-t86x-r14p0
 ```

#### 



root@firefly:~# ldconfig -p | grep isp
        liburl-dispatcher.so.1 (libc6,AArch64) => /usr/lib/aarch64-linux-gnu/liburl-dispatcher.so.1
        libnss_nisplus.so.2 (libc6,AArch64, OS ABI: Linux 3.7.0) => /lib/aarch64-linux-gnu/libnss_nisplus2
        libnss_nisplus.so (libc6,AArch64, OS ABI: Linux 3.7.0) => /usr/lib/aarch64-linux-gnu/libnss_nisplo
root@firefly:~# 
root@firefly:~# 
root@firefly:~# ldconfig -p | grep atom
        libatomic.so.1 (libc6,AArch64) => /usr/lib/aarch64-linux-gnu/libatomic.so.1




#### 如果开发板没有环境，可以在主机上进行交叉编译：
```
export PATH=/path/to/cross-compiler:$PATH 
CC=aarch64-linux-gcc ./autogen.sh --prefix=/home/out --host=aarch64-linux --enable-gst --enable-rkiq 
```
configure:3124: checking for aarch64-linux-gcc
configure:3151: result: aarch64-linux-gcc
configure:3420: checking for C compiler version
configure:3429: aarch64-linux-gcc --version >&5
./configure: line 3431: aarch64-linux-gcc: command not found
```
CC=aarch64-linux-gnu-gcc ./autogen.sh --prefix=/home/younix/rk-linux/rootfs/camera-app-gstreamer/out --host=aarch64-linux-gnu --enable-gst --enable-rkiq

```
遇到问题
```
YounixPC# make
make  all-recursive
make[1]: Entering directory '/home/younix/rk-linux/rootfs/camera-app-gstreamer'
Making all in xcore
make[2]: Entering directory '/home/younix/rk-linux/rootfs/camera-app-gstreamer/xcore'
/bin/bash ../libtool  --tag=CXX   --mode=link g++ -fPIC -DSTDC99 -W -Wall -D_REENTRANT -Wformat -Wformat-security -fstack-protector -std=c++0x -I/usr/include/libdrm -I../ext/rkisp/include   -g -O2 -no-undefined -v
ersion-number 1:1:1 -pthread   -o libxcam_core.la -rpath /home/younix/rk-linux/rootfs/camera-app-gstreamer/out/lib libxcam_core_la-analyzer_loader.lo libxcam_core_la-smart_analyzer_loader.lo libxcam_core_la-buffer_pool.lo libxcam_core_la-device_manager.lo libxcam_core_la-pipe_manager.lo libxcam_core_la-dma_video_buffer.lo libxcam_core_la-dynamic_analyzer.lo libxcam_core_la-dynamic_analyzer_loader.lo libxcam_core_la-smart_analyzer.lo libxcam_core_la-smart_analysis_handler.lo libxcam_core_la-smart_buffer_priv.lo libxcam_core_la-fake_poll_thread.lo libxcam_core_la-handler_interface.lo libxcam_core_la-image_processor.lo libxcam_core_la
-image_projector.lo libxcam_core_la-image_file_handle.lo libxcam_core_la-poll_thread.lo libxcam_core_la-swapped_buffer.lo libxcam_core_la-uvc_device.lo libxcam_core_la-v4l2_buffer_proxy.lo libxcam_core_la-v4l2_dev
ice.lo libxcam_core_la-video_buffer.lo libxcam_core_la-xcam_analyzer.lo libxcam_core_la-x3a_analyzer.lo libxcam_core_la-x3a_analyzer_manager.lo libxcam_core_la-x3a_analyzer_simple.lo libxcam_core_la-x3a_image_proc
ess_center.lo libxcam_core_la-x3a_stats_pool.lo libxcam_core_la-x3a_result.lo libxcam_core_la-x3a_result_factory.lo libxcam_core_la-xcam_common.lo libxcam_core_la-xcam_buffer.lo libxcam_core_la-xcam_thread.lo libx
cam_core_la-x3a_analyze_tuner.lo libxcam_core_la-x3a_ciq_tuning_handler.lo libxcam_core_la-x3a_ciq_tnr_tuning_handler.lo libxcam_core_la-x3a_ciq_bnr_ee_tuning_handler.lo libxcam_core_la-x3a_ciq_wavelet_tuning_hand
ler.lo libxcam_core_la-drm_bo_buffer.lo libxcam_core_la-drm_display.lo libxcam_core_la-drm_v4l2_buffer.lo -ldl -lpthread  -ldrm  -L../ext/rkisp/lib -lrkisp   -L../ext/rkisp/lib -lrkisp
libtool: link: g++  -fPIC -DPIC -shared -nostdlib /usr/lib/gcc/x86_64-linux-gnu/5/../../../x86_64-linux-gnu/crti.o /usr/lib/gcc/x86_64-linux-gnu/5/crtbeginS.o  .libs/libxcam_core_la-analyzer_loader.o .libs/libxcam
_core_la-smart_analyzer_loader.o .libs/libxcam_core_la-buffer_pool.o .libs/libxcam_core_la-device_manager.o .libs/libxcam_core_la-pipe_manager.o .libs/libxcam_core_la-dma_video_buffer.o .libs/libxcam_core_la-dynam
ic_analyzer.o .libs/libxcam_core_la-dynamic_analyzer_loader.o .libs/libxcam_core_la-smart_analyzer.o .libs/libxcam_core_la-smart_analysis_handler.o .libs/libxcam_core_la-smart_buffer_priv.o .libs/libxcam_core_la-f
ake_poll_thread.o .libs/libxcam_core_la-handler_interface.o .libs/libxcam_core_la-image_processor.o .libs/libxcam_core_la-image_projector.o .libs/libxcam_core_la-image_file_handle.o .libs/libxcam_core_la-poll_thre
ad.o .libs/libxcam_core_la-swapped_buffer.o .libs/libxcam_core_la-uvc_device.o .libs/libxcam_core_la-v4l2_buffer_proxy.o .libs/libxcam_core_la-v4l2_device.o .libs/libxcam_core_la-video_buffer.o .libs/libxcam_core_
la-xcam_analyzer.o .libs/libxcam_core_la-x3a_analyzer.o .libs/libxcam_core_la-x3a_analyzer_manager.o .libs/libxcam_core_la-x3a_analyzer_simple.o .libs/libxcam_core_la-x3a_image_process_center.o .libs/libxcam_core_
la-x3a_stats_pool.o .libs/libxcam_core_la-x3a_result.o .libs/libxcam_core_la-x3a_result_factory.o .libs/libxcam_core_la-xcam_common.o .libs/libxcam_core_la-xcam_buffer.o .libs/libxcam_core_la-xcam_thread.o .libs/l
ibxcam_core_la-x3a_analyze_tuner.o .libs/libxcam_core_la-x3a_ciq_tuning_handler.o .libs/libxcam_core_la-x3a_ciq_tnr_tuning_handler.o .libs/libxcam_core_la-x3a_ciq_bnr_ee_tuning_handler.o .libs/libxcam_core_la-x3a_
ciq_wavelet_tuning_handler.o .libs/libxcam_core_la-drm_bo_buffer.o .libs/libxcam_core_la-drm_display.o .libs/libxcam_core_la-drm_v4l2_buffer.o   -ldl -lpthread -ldrm -L../ext/rkisp/lib -lrkisp -L/usr/lib/gcc/x86_6
4-linux-gnu/5 -L/usr/lib/gcc/x86_64-linux-gnu/5/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/5/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/us
r/lib/gcc/x86_64-linux-gnu/5/../../.. -lstdc++ -lm -lc -lgcc_s /usr/lib/gcc/x86_64-linux-gnu/5/crtendS.o /usr/lib/gcc/x86_64-linux-gnu/5/../../../x86_64-linux-gnu/crtn.o  -fstack-protector -g -O2 -pthread   -pthre
ad -Wl,-soname -Wl,libxcam_core.so.1 -o .libs/libxcam_core.so.1.1.1
/usr/bin/ld: skipping incompatible ../ext/rkisp/lib/librkisp.so when searching for -lrkisp
/usr/bin/ld: cannot find -lrkisp
collect2: error: ld returned 1 exit status
Makefile:583: recipe for target 'libxcam_core.la' failed
make[2]: *** [libxcam_core.la] Error 1
make[2]: Leaving directory '/home/younix/rk-linux/rootfs/camera-app-gstreamer/xcore'
Makefile:427: recipe for target 'all-recursive' failed
make[1]: *** [all-recursive] Error 1
make[1]: Leaving directory '/home/younix/rk-linux/rootfs/camera-app-gstreamer'
Makefile:359: recipe for target 'all' failed
make: *** [all] Error 2
```