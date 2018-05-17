---
title: [Android] 文件系统分区挂载流程
tags: 
grammar_cjkRuby: true
---

//DRAFT
//TODO

最近在玩 RK 的板子，想要将 Ubuntu 移植上去，对比之前做 Android 的时候，发现他们的 Kernel 部分完全一样。
那么 Linux 发行版 和 Android 系统他们之间的差别究竟是怎样的呢？
差别在于 Kernel 启动后，挂载的分区有所差别。所进入的 rootfs（根文件系统）不同。
之前有写一篇关于 Android 启动流程的文章。

## 分区挂载配置文件 fstab
Android 5.1 & 6.0 的分区挂载配置文件是 fstab.\*.\*  ，比如 ./device/rockchip/rk3399/fstab.rk30board.bootmode.emmc 
```fstab
<src> <mount point>  <filesystem type> <mount flags parameters>     <fs_mgr_flags> 
/dev/block/platform/fe330000.sdhci/by-name/system         /system             ext4      ro,noatime,nodiratime,noauto_da_alloc                                  wait,resize
```
其中 **mount flags parameters** 文件系统的参数： 
rw/ro : 是否以以只读或者读写模式挂载 
async/sync : 设置是否为同步方式运行 
auto/noauto : 当下载mount -a 的命令时，此文件系统是否被主动挂载。默认为auto 
exec/noexec : 限制此文件系统内是否能够进行”执行”的操作 
user/nouser : 是否允许用户使用mount命令挂载 
suid/nosuid ： 是否允许SUID的存在 
usrquota : 启动文件系统支持磁盘配额模式 
grpquota : 启动文件系统对群组磁盘配额模式的支持 
defaults ： 同时具有rw,suid,dev,exec,auto,nouser,async等默认参数的设置

通过配置 fstab，vold 服务通过 process_config 函数调用 fs_mgr_read_fstab 来完成对分区文件的解析。

## init 获取 fstab 的配置信息
kernel 加载完后第一个执行的是 init 进程，init 进程会根据 init.rc 的规则启动进程或者服务，这个我之前有写一篇文章讲述。
init.rc 通过 import /init.${ro.hardware}.rc导入平台的规则。device/rockchip/common/init.rk30board.rc中：
```
import init.${ro.hardware}.bootmode.{ro.bootmode}.rc    
```
这里导入的便是  init.rk30board.bootmode.emmc.rc
device/rockchip/common/init.rk30board.bootmode.emmc.rc 中：
```
on fs
    write /sys/block/mmcblk0/bdi/read_ahead_kb 2048
    mount_all fstab.rk30board
```
mount_all 表示执行 do_mount_all 函数，其参数为 fstab.rk30board。
在 system/core/init/keyworks.h 中定义 `KEYWORD(mount_all,   COMMAND, 1, do_mount_all)`

这个函数的定义在 system/core/init/builtins.c 
```
/*
 * This function might request a reboot, in which case it will
 * not return.
 */
int do_mount_all(int nargs, char **args)
{
    pid_t pid;
    int ret = -1;
    int child_ret = -1;
    int status;
    const char *prop;
    struct fstab *fstab;

    if (nargs != 2) {
        return -1;
    }

    /*
     * Call fs_mgr_mount_all() to mount all filesystems.  We fork(2) and
     * do the call in the child to provide protection to the main init
     * process if anything goes wrong (crash or memory leak), and wait for
     * the child to finish in the parent.
     */
    pid = fork();
    if (pid > 0) {
        /* Parent.  Wait for the child to return */
        int wp_ret = TEMP_FAILURE_RETRY(waitpid(pid, &status, 0));
        if (wp_ret < 0) {
            /* Unexpected error code. We will continue anyway. */
            NOTICE("waitpid failed rc=%d, errno=%d\n", wp_ret, errno);
        }

        if (WIFEXITED(status)) {
            ret = WEXITSTATUS(status);
        } else {
            ret = -1;
        }
    } else if (pid == 0) {
        /* child, call fs_mgr_mount_all() */
        klog_set_level(6);  /* So we can see what fs_mgr_mount_all() does */
        fstab = fs_mgr_read_fstab(args[1]);     //解析分区文件fstab
        child_ret = fs_mgr_mount_all(fstab);
        fs_mgr_free_fstab(fstab);
        if (child_ret == -1) {
            ERROR("fs_mgr_mount_all returned an error\n");
        }
        _exit(child_ret);
    } else {
        /* fork failed, return an error */
        return -1;
    }

    if (ret == FS_MGR_MNTALL_DEV_NEEDS_ENCRYPTION) {
        property_set("vold.decrypt", "trigger_encryption");
    } else if (ret == FS_MGR_MNTALL_DEV_MIGHT_BE_ENCRYPTED) {
        property_set("ro.crypto.state", "encrypted");
        property_set("vold.decrypt", "trigger_default_encryption");
    } else if (ret == FS_MGR_MNTALL_DEV_NOT_ENCRYPTED) {
        property_set("ro.crypto.state", "unencrypted");
        /* If fs_mgr determined this is an unencrypted device, then trigger
         * that action.
         */
        action_for_each_trigger("nonencrypted", action_add_queue_tail);
    } else if (ret == FS_MGR_MNTALL_DEV_NEEDS_RECOVERY) {
        /* Setup a wipe via recovery, and reboot into recovery */
        ERROR("fs_mgr_mount_all suggested recovery, so wiping data via recovery.\n");
        ret = wipe_data_via_recovery();
        /* If reboot worked, there is no return. */
    } else if (ret > 0) {
        ERROR("fs_mgr_mount_all returned unexpected error %d\n", ret);
    }
    /* else ... < 0: error */

    return ret;
}
```
