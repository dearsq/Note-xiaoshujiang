---
title: [Android6.0][RK3399] 更换64GeMMC后无法启动的问题
tags: rockchip,emmc
grammar_cjkRuby: true
---


## 错误日志
```
[    2.002835] dwmmc_rockchip fe310000.dwmmc: IDMAC supports 32-bit address mode.
[    2.002992] dwmmc_rockchip fe310000.dwmmc: Using internal DMA controller.
[    2.003029] dwmmc_rockchip fe310000.dwmmc: Version ID is 270a
[    2.003094] dwmmc_rockchip fe310000.dwmmc: DW MMC controller at irq 25,32 bit host data width,256 deep fifo
[    2.003164] dwmmc_rockchip fe310000.dwmmc: No vmmc regulator found
[    2.003178] dwmmc_rockchip fe310000.dwmmc: No vqmmc regulator found
[    2.004431] dwmmc_rockchip fe320000.dwmmc: IDMAC supports 32-bit address mode.
[    2.004506] dwmmc_rockchip fe320000.dwmmc: Using internal DMA controller.
[    2.004526] dwmmc_rockchip fe320000.dwmmc: Version ID is 270a
[    2.004580] dwmmc_rockchip fe320000.dwmmc: DW MMC controller at irq 26,32 bit host data width,256 deep fifo
[    2.004704] dwmmc_rockchip fe320000.dwmmc: No vmmc regulator found
[    2.005047] rockchip-iodomain ff770000.syscon:io-domains: Setting to 3300000 done
[    2.005203] rockchip-iodomain ff770000.syscon:io-domains: Setting to 3300000 done
[    2.017696] mmc_host mmc0: Bus speed (slot 0) = 400000Hz (slot req 400000Hz, actual 400000HZ div = 0)
[    2.031967] dwmmc_rockchip fe320000.dwmmc: 1 slots initialized
[    2.032446] sdhci-pltfm: SDHCI platform and OF driver helper
[    2.034361] sdhci-arasan fe330000.sdhci: No vmmc regulator found
[    2.034386] sdhci-arasan fe330000.sdhci: No vqmmc regulator found
[    2.062984] mmc1: SDHCI controller on fe330000.sdhci [fe330000.sdhci] using ADMA
[    2.115687] mmc1: MAN_BKOPS_EN bit is not set
[    2.131736] mmc1: new HS400 MMC card at address 0001
[    2.132971] mmcblk1: mmc1:0001 MCG8GC 58.2 GiB 
[    2.133959] mmcblk1boot0: mmc1:0001 MCG8GC partition 1 4.00 MiB
[    2.134926] mmcblk1boot1: mmc1:0001 MCG8GC partition 2 4.00 MiB
[    2.135958] mmcblk1rpmb: mmc1:0001 MCG8GC partition 3 4.00 MiB
[    2.136600]      uboot: 0x000400000 -- 0x000800000 (4 MB)
[    2.136622]      trust: 0x000800000 -- 0x000c00000 (4 MB)
[    2.136635]       misc: 0x000c00000 -- 0x001000000 (4 MB)
[    2.136647]   resource: 0x001000000 -- 0x002000000 (16 MB)
[    2.136659]     kernel: 0x002000000 -- 0x003800000 (24 MB)
[    2.136671]       boot: 0x003800000 -- 0x005800000 (32 MB)
[    2.136684]   recovery: 0x005800000 -- 0x008800000 (48 MB)
[    2.136696]     backup: 0x008800000 -- 0x00f800000 (112 MB)
[    2.136708]      cache: 0x00f800000 -- 0x017800000 (128 MB)
[    2.136721]     system: 0x017800000 -- 0x0d7800000 (3072 MB)
[    2.136735]   metadata: 0x0d7800000 -- 0x0d8800000 (16 MB)
[    2.136748] baseparamer: 0x0d8800000 -- 0x0d8c00000 (4 MB)
[    2.136761]        frp: 0x0d8c00000 -- 0x0d8c80000 (0 MB)
[    2.136773]   userdata: 0x0d8c80000 -- 0xe8f400000 (56167 MB)
[    2.136816]  mmcblk1: p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14

[    2.481883] dwmmc_rockchip fe310000.dwmmc: IDMAC supports 32-bit address mode.
[    2.482061] dwmmc_rockchip fe310000.dwmmc: Using internal DMA controller.
[    2.482113] dwmmc_rockchip fe310000.dwmmc: Version ID is 270a
[    2.482169] dwmmc_rockchip fe310000.dwmmc: DW MMC controller at irq 25,32 bit host data width,256 deep fifo
[    2.482287] dwmmc_rockchip fe310000.dwmmc: No vmmc regulator found
[    2.482316] dwmmc_rockchip fe310000.dwmmc: No vqmmc regulator found
[    2.482769] dwmmc_rockchip fe310000.dwmmc: allocated mmc-pwrseq
[    2.494688] mmc_host mmc2: Bus speed (slot 0) = 400000Hz (slot req 400000Hz, actual 400000HZ div = 0)
[    2.507803] dwmmc_rockchip fe310000.dwmmc: 1 slots initialized

[    2.556671] mmc2: queuing unknown CIS tuple 0x80 (2 bytes)
[    2.559525] mmc2: queuing unknown CIS tuple 0x80 (3 bytes)
[    2.561212] mmc2: queuing unknown CIS tuple 0x80 (3 bytes)
[    2.565389] mmc2: queuing unknown CIS tuple 0x80 (7 bytes)

[    2.623906] mmc_host mmc2: Bus speed (slot 0) = 200000000Hz (slot req 208000000Hz, actual 200000000HZ div = 0)
[    2.628545] init: OK,EMMC DRIVERS INIT OK

[    2.932402] EXT4-fs (mmcblk1p10): mounted filesystem with ordered data mode. Opts: noauto_da_alloc
[    2.932568] fs_mgr: __mount(source=/dev/block/platform/fe330000.sdhci/by-name/system,target=/system,type=ext4)=0
[    2.933322] EXT4-fs (mmcblk1p9): Ignoring removed nomblk_io_submit option
[    2.937456] EXT4-fs (mmcblk1p9): mounted filesystem with ordered data mode. Opts: nomblk_io_submit,errors=remount-ro
[    2.937600] fs_mgr: check_fs(): mount(/dev/block/platform/fe330000.sdhci/by-name/cache,/cache,ext4)=0: Success
[    2.956910] fs_mgr: check_fs(): unmount(/cache) succeeded
[    2.958200] fs_mgr: Running /system/bin/e2fsck on /dev/block/platform/fe330000.sdhci/by-name/cache
[    2.964050] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    2.966278] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    2.966313] mmcblk1: retrying because a re-tune was needed
[    2.988024] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    2.990140] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    2.990184] mmcblk1: error -84 transferring data, sector 973048, nr 256, cmd response 0x900, card status 0x0
[    2.990260] mmcblk1: retrying using single block read
[    3.038680] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.040785] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.040818] mmcblk1: retrying because a re-tune was needed
[    3.059313] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.061430] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.061469] mmcblk1: error -84 transferring data, sector 972800, nr 224, cmd response 0x900, card status 0x0
[    3.061536] mmcblk1: retrying using single block read
[    3.106220] mmcblk1: error -84 transferring data, sector 972989, nr 35, cmd response 0x900, card status 0x0
[    3.106289] blk_update_request: I/O error, dev mmcblk1, sector 972989
[    3.141668] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.143802] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.143850] mmcblk1: retrying because a re-tune was needed
[    3.162815] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.165056] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.165113] mmcblk1: error -84 transferring data, sector 972984, nr 8, cmd response 0x900, card status 0x0
[    3.165155] mmcblk1: retrying using single block read
[    3.184661] mmcblk1: error -84 transferring data, sector 972989, nr 3, cmd response 0x900, card status 0x0
[    3.184715] blk_update_request: I/O error, dev mmcblk1, sector 972989
[    3.204352] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.206483] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.206525] mmcblk1: retrying because a re-tune was needed
[    3.225395] mmc1: Got data interrupt 0x00000002 even though no data operation was in progress.
[    3.227528] mmcblk1: error -110 sending stop command, original cmd response 0x900, card status 0x400900
[    3.227572] mmcblk1: error -84 transferring data, sector 972984, nr 8, cmd response 0x900, card status 0x0
[    3.227603] mmcblk1: retrying using single block read
[    3.246588] mmcblk1: error -84 transferring data, sector 972989, nr 3, cmd response 0x900, card status 0x0
[    3.246633] blk_update_request: I/O error, dev mmcblk1, sector 972989
[    3.263636] e2fsck[225]: unhandled level 3 translation fault (7) at 0x7f9fc2d4a4, esr 0x82000007
[    3.263682] pgd = ffffffc0e8e0c000
[    3.263702] [7f9fc2d4a4] *pgd=00000000e8473003, *pud=00000000e8473003, *pmd=00000000e8479003, *pte=0000000000000000
[    3.263758] 
[    3.263783] CPU: 4 PID: 225 Comm: e2fsck Not tainted 4.4.36 #633
[    3.263807] Hardware name: rockchip,rk3399-excavator-edp (DT)
[    3.263829] task: ffffffc0e8534980 ti: ffffffc0e858c000 task.ti: ffffffc0e858c000
[    3.263854] PC is at 0x7f9fc2d4a4
[    3.263871] LR is at 0x44
[    3.263888] pc : [<0000007f9fc2d4a4>] lr : [<0000000000000044>] pstate: a0000000
[    3.263908] sp : 0000007fd2ee0430
[    3.263924] x29: 0000007fd2ee0430 x28: 0000007fd2ee0600 
[    3.263957] x27: 00000000ffffffd8 x26: 0000007fd2ee05d0 
[    3.263989] x25: 0000000000000000 x24: 0000007fd2ee0c58 
[    3.264020] x23: 00000000ffffffff x22: 0000007f9fc39170 
[    3.264050] x21: 0000007fd2ee05c0 x20: 0000007fd2ee06b8 
[    3.264080] x19: 0000007fd2ee05b4 x18: 0000000000000000 
[    3.264110] x17: 0000007fd2ee0da0 x16: 00000000ffffffe0 
[    3.264140] x15: 0000000000000000 x14: 0000000000000000 
[    3.264201] x13: 0000007fd2ee0630 x12: 0000007fd2ee05a7 
[    3.264232] x11: 0000007fd2ee05a8 x10: 0000007fd2ee0d78 
[    3.264263] x9 : 0000007f9fc56018 x8 : 0000000000000064 
[    3.264293] x7 : 0000007f9fc56098 x6 : 0000007fd2ee06c8 
[    3.264323] x5 : 0000007f9fc56c58 x4 : 0000007f9fc3bf70 
[    3.264353] x3 : 0000000000000002 x2 : 0000000000000030 
[    3.264383] x1 : 0000000000000003 x0 : 00000000ffffffd8 
[    3.264413] 
[    3.264907] e2fsck: e2fsck terminated by signal 7

```
后面则是重复出现上面这个 ` mounted filesystem with ordered data mode. Opts: noauto_da_alloc,discard` 的错误.

## 解决方案

从 Log 上来看, 显然是 fe330000 的有问题. 查看 fe330000 是 sdhci. 所以确定是 EMMC 有问题.
在系统起来后, eMMC 的 clock 为 200MHZ , 尝试降低 eMMC CLK Frequence , 发现 50MHZ 100MHZ 150MHZ 系统均可以正常启动.
后来和硬件沟通, 了解到这个是由于硬件上 eMMC 走线有问题. 导致信号不完整.

```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399-vop-clk-set.dtsi b/arch/arm64/boot/dts/rockchip/rk3399-vop-clk-set.dtsi
index 0ca60fb..e1d2563 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399-vop-clk-set.dtsi
+++ b/arch/arm64/boot/dts/rockchip/rk3399-vop-clk-set.dtsi
@@ -51,7 +51,8 @@
 &sdhci {
                assigned-clocks = <&cru SCLK_EMMC>;
                assigned-clock-parents = <&cru PLL_GPLL>;
-               assigned-clock-rates = <200000000>;
+               //assigned-clock-rates = <200000000>;
+               assigned-clock-rates = <150000000>;
 };
```