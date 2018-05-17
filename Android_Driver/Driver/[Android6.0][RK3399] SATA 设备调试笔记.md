---
title: [Android6.0][RK3399] SATA 设备调试笔记
tags: 
grammar_cjkRuby: true
---

[TOC]

## SATA 基础知识

Linux 世界中，I/O 设备被分为 字符设备、块设备、网络设备。
SATA 这种存储设备属于块设备。
块设备用来存储定长，且可随时访问的数据块，对块设备的操作都以块（block）为单位进行。
在高性能系统的块设备（block devices）I/O 控制方式中，DMA 和 I/O通道方式比较常用。
前者由 DMA 控制器接管 CPU 总线控制权，数据不经过 CPU 而直接在内存和 I/O 设备间进行块传输，进而提升系统的数据传输效率。
后者可以获得 CPU 和外设间更好的并行能力。

SATA 是一种新型块设备（Serial ATA），这需要我们开发一种功能与性能更强的 I/O 控制器来发挥其高性能。着这控制器就是 ADMA 控制器，它采用一种新的 I/O 控制方式。

SATA 是一种串行架构。同 IDE/ATA、SCSI 接口的块设备相比，SATA 优点大大的。包括 1）pin 更少 2）速度更快，1.0 150MB/s  3.0 600MB/s 3）热插拔 4）拓展性好。
5）成本低，就成本而言，远低于 SCSI 产品。

## SATA 设备调试

当有外置 USB 插入的时候，会产生 /proc/scsi/usb-storage 目录，并在其中产生数字文件（形如 1 2 3 4），此文件存储了设备相关信息。

相应的 /sys/class/scsi_device/ 目录中会有 scsi 设备的目录(ide 硬盘默认无子目录，sata硬盘默认有子目录)，以数字开头（形如 1:0:0:0 2:0:0:0）
这个数字与前面 /proc/scsi/usb-storage目录中的相对应，子目录表示sata硬盘。

/sys/class/scsi_device/2:0:0:0/device/block 中有 sata 设备文件，其中有多个文件，我们关注 removeable 和 dev
```
# cat dev
8:0

#cat removable
0
```
dev 内容形如 8:0 ，就是 /proc/partitions 中设备的 maj:min 主设备号:次设备号。
removable 可以为 0 或者 1 ，1 表示 U 盘，0 表示硬盘。



---


据此，先看usb-storage目录，再到/sys目录下找相应的removable和dev文件，再
查partitions文件，就可以得到设备名、设备信息、可移动标记。


```
root@rk3399_mid:/sys/class/scsi_device/2:0:0:0/device/block/sda # mount        
rootfs / rootfs ro,seclabel,size=953876k,nr_inodes=238469 0 0
tmpfs /dev tmpfs rw,seclabel,nosuid,relatime,mode=755 0 0
devpts /dev/pts devpts rw,seclabel,relatime,mode=600 0 0
proc /proc proc rw,relatime 0 0
sysfs /sys sysfs rw,seclabel,relatime 0 0
selinuxfs /sys/fs/selinux selinuxfs rw,relatime 0 0
none /acct cgroup rw,relatime,cpuacct 0 0
none /sys/fs/cgroup tmpfs rw,seclabel,relatime,mode=750,gid=1000 0 0
tmpfs /mnt tmpfs rw,seclabel,relatime,mode=755,gid=1000 0 0
none /dev/cpuctl cgroup rw,relatime,cpu 0 0
none /dev/cpuset cgroup rw,relatime,cpuset,noprefix,release_agent=/sbin/cpuset_release_agent 0 0
pstore /sys/fs/pstore pstore rw,seclabel,relatime 0 0
/dev/block/platform/fe330000.sdhci/by-name/system /system ext4 ro,seclabel,noatime,nodiratime,noauto_da_alloc,data=ordered 0 0
/dev/block/platform/fe330000.sdhci/by-name/cache /cache ext4 rw,seclabel,nosuid,nodev,noatime,nodiratime,discard,noauto_da_alloc,data=ordered 0 0
/dev/block/platform/fe330000.sdhci/by-name/metadata /metadata ext4 rw,seclabel,nosuid,nodev,noatime,nodiratime,discard,noauto_da_alloc,data=ordered 0 0
tmpfs /storage tmpfs rw,seclabel,relatime,mode=755,gid=1000 0 0
/sys/kernel/debug /sys/kernel/debug debugfs rw,seclabel,relatime,mode=755 0 0
/sys/kernel/debug/tracing /sys/kernel/debug/tracing tracefs rw,seclabel,relatime,mode=755 0 0
none /config configfs rw,relatime 0 0
adb /dev/usb-ffs/adb functionfs rw,relatime 0 0
/dev/block/dm-0 /data f2fs rw,seclabel,nosuid,nodev,noatime,nodiratime,background_gc=on,discard,user_xattr,inline_xattr,inline_data,extent_cache,active_logs=6 0 0
/dev/fuse /mnt/runtime/default/emulated fuse rw,nosuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/fuse /storage/emulated fuse rw,nosuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/fuse /mnt/runtime/read/emulated fuse rw,nosuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/fuse /mnt/runtime/write/emulated fuse rw,nosuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/block/vold/public:8,1 /mnt/meDia_rw/7206F4C406F489FD fuseblk rw,dirsync,nosuid,nodev,noatime,user_id=0,group_id=0,default_permissions,allow_other,blksize=4096 0 0
/dev/fuse /mnt/runtime/default/7206F4C406F489FD fuse rw,nosuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/fuse /storage/7206F4C406F489FD fuse rw,losuid,nodev,noexec,noatime,user_id=1023,group_id=1023,default_permissions,allow_other 0 0
/dev/fuse /mnt/runtime/read/7206F4C406F489FD fuse rw,nosuid,nodev,noexeC,noatime,user_id=10"3,group_id=1023,defAult_permissions,allow_other 0 0
/det/fuse /mnt/runtime/writE/7206F4C406F489FD Fuse rw,nosuid,nodev(noexec,noatime,user_id=1023,group_id=10"3(dEDault_permissions,ahhow_other 0 0
```
