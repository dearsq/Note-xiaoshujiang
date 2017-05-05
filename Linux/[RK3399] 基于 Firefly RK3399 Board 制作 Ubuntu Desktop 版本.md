---
title: [RK3399] 基于 Firefly RK3399 Board 制作 Ubuntu Desktop 版本
tags: rockchip,ubuntu
grammar_cjkRuby: true
---

# 基于 Firefly RK3399 Board 制作 Ubuntu 桌面版本

Platform: RK3399
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04


## 编译 u-boot
```
cd u-boot
make rk3399_defconfig
make ARCHV=aarch64 -j8
```
制作出来的文件包括 
uboot.img
trust.img
RK3399MiniLoaderAll_V1.05.bin

## 编译 kernel
```
cd kernel
make ARCH=arm64 firefly_linux_defconfig
make ARCH=arm64 rk3399-firefly-mini-linux.img -j8
```
制作出来的文件包括 
kernel.img
resource.img
arch/arm64/boot/Image

## 整合内存盘 打包成 boot.img
### 创建内存盘 Ramdisk
```
git clone -b for-kernel_4.4 https://github.com/TeeFirefly/initrd.git
make -C initrd
```
会生成 initrd.img
### 打包内核和内存盘
```
mkbootimg --kernel arch/arm64/boot/Image --ramdisk initrd.img --second resource.img -o boot.img
```
会生成 boot.img

## 修改 parameter.txt 文件
CMDLINE: console=tty0 console=ttyFIQ0 root=/dev/mmcblk1p5 rw rootwait rootfstype=ext4 init=/sbin/init mtdparts=rk29xxnand:0x00002000@0x00002000(uboot),0x00002000@0x00004000(trust),0x00010000@0x00006000(boot),0x00002000@0x00016000(backup),-@0x00018000(rootfs)



## 制作根文件系统

### 下载和解压　ubuntu-base
mkdir ubuntu-desktop
sudo tar -xpf ubuntu-base-16.04.1-base-arm64.tar.gz -C ubuntu-desktop

### 修改配置及更新软件

#### 将本机网络配置拷贝到文件系统中
sudo cp -b /etc/resolv.conf ubuntu-desktop/etc/resolv.conf

####　拷贝 qemu
sudo cp /usr/bin/qemu-aarch64-static ubuntu-desktop/usr/bin

#### 进入根文件系统进行操作
sudo chroot ubuntu-desktop 
如果产生报错 **问题2**

#### 更新和安装
apt update
apt upgrade
apt install vim git #根据需求添加
apt install xubuntu-desktop #这一步根据网速差别可能长达十几个小时，这也是 base 版本和 desktop 版本的区别所在

#### 添加账户并设置密码
useradd -s '/bin/bash' -m -G adm,sudo orangepi
passwd orangepi #给 orangepi 这个用户设置密码
passwd root #给 root 用户设置密码

#### 退出
exit


### 开始制作 rootfs
查看文件系统大小
sudo du -sh ubuntu-desktop
4.7G ubuntu-desktop
分配 8GB，count 根据实际自己的大小进行修改
dd if=/dev/zero of=rootfs.img bs=1M count=8096
sudo mkfs.ext4 rootfs.img
mkdir -pv rootfs_mnt
sudo mount rootfs.img rootfs_mnt
sudo cp -rfp ubuntu-desktop/* rootfs_mnt/
sudo umount -R rootfs_mnt
e2fsck -p -f rootfs.img
resize2fs -M rootfs.img

rootfs.img 即为最终根文件系统的镜像文件

## 问题汇总

### 问题2
chroot: failed to run command ‘/usr/bin/bash’: No such file or directory
手动指定 bash 路径
sudo chroot ubuntu-desktop /bin/bash
