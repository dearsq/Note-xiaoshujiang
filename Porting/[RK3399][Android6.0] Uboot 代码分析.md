---
title: [RK3399][Android6.0] Uboot 代码分析
tags: uboot,linux
grammar_cjkRuby: true
---

Author: Younix 
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.07

[TOC]

之前曾分析过 展讯平台的 Uboot 流程：http://blog.csdn.net/dearsq/article/details/51063207
也基于 RK3288 分析过 Android 启动流程：
http://blog.csdn.net/dearsq/article/details/53647871

现在借着 RK3399 ，重新整体看一下 uboot 代码。

## 
前一篇文章中我们了解到了`make rk3399_defconfig` 的原理，在 uboot 根目录会生成 `.config` 文件。
然后我们执行 `make` 命令，下面是他的流程：
Makefile 中默认执行 `make all`
```
 815 all:            $(ALL-y)
```
`ALL-y` 需要生成四个目标文件
```
 757 # Always append ALL so that arch config.mk's can add custom ones
 758 ALL-y += u-boot.srec u-boot.bin System.map binary_size_check
```
目标文件1 `u-boot.srec`
```
 844 u-boot.hex u-boot.srec: u-boot FORCE
 845         $(call if_changed,objcopy)
```
目标文件2 `u-boot.bin`
```
 863 u-boot.bin: u-boot FORCE
 864         $(call if_changed,objcopy)
 865         $(call DO_STATIC_RELA,$<,$@,$(CONFIG_SYS_TEXT_BASE))
 866         $(BOARD_SIZE_CHECK)
```
目标文件3 `System.map`
```
1280 System.map:     u-boot
1281                 @$(call SYSTEM_MAP,$<) > $@
```
目标文件4 `binary_size_check`
```
 849 binary_size_check: u-boot.bin FORCE
 850         @file_size=$(shell wc -c u-boot.bin | awk '{print $$1}') ; \
 851         map_size=$(shell cat u-boot.map | \
 852                 awk '/_image_copy_start/ {start = $$1} /_image_binary_end/ {end = $$1} END {if (start      != "" && end != "") print "ibase=16; " toupper(end) " - " toupper(start)}' \
 853                 | sed 's/0X//g' \
 854                 | bc); \
 855         if [ "" != "$$map_size" ]; then \
 856                 if test $$map_size -ne $$file_size; then \
 857                         echo "u-boot.map shows a binary size of $$map_size" >&2 ; \
 858                         echo "  but u-boot.bin shows $$file_size" >&2 ; \
 859                         exit 1; \
 860                 fi \
 861         fi
```

所以可以看到，他们首先都需要 u-boot 这个 elf 文件。
```shell
1128 u-boot: $(u-boot-init) $(u-boot-main) u-boot.lds
1129         $(call if_changed,u-boot__)
1130 ifeq ($(CONFIG_KALLSYMS),y)
1131         $(call cmd,smap)
1132         $(call cmd,u-boot__) common/system_map.o
1133 endif
```
进一步分析 u-boot 依赖于三个参数 `u-boot-init` `u-boot-main` `u-boot.lds`
第一个参数 `u-boot-init` 定义为
```shell
 701 u-boot-init := $(head-y)
 630 head-y := $(CPUDIR)/start.o

```
第二个参数 `u-boot-main`定义为
```shell
702 u-boot-main := $(libs-y)
# libs-y 为各种库和驱动，暂列一些比较关键的
 636 libs-y += lib/
 637 libs-$(HAVE_VENDOR_COMMON_LIB) += board/$(VENDOR)/common/
 638 libs-y += $(CPUDIR)/
 639 ifdef SOC
 640 libs-y += $(CPUDIR)/$(SOC)/
 641 endif
 642 libs-$(CONFIG_OF_EMBED) += dts/
 643 libs-y += arch/$(ARCH)/lib/
 644 libs-y += fs/
 645 libs-y += net/
 646 libs-y += disk/
 647 libs-y += drivers/
 648 libs-y += drivers/dma/
 649 libs-y += drivers/gpio/
 650 libs-y += drivers/i2c/
 651 libs-y += drivers/mmc/
 652 libs-y += drivers/mtd/
 653 libs-$(CONFIG_CMD_NAND) += drivers/mtd/nand/
 654 libs-y += drivers/mtd/onenand/
 655 libs-$(CONFIG_CMD_UBI) += drivers/mtd/ubi/
 656 libs-y += drivers/mtd/spi/
 657 libs-y += drivers/net/
 658 libs-y += drivers/net/phy/
 659 libs-y += drivers/pci/
 660 libs-y += drivers/power/ \
 661         drivers/power/fuel_gauge/ \
 662         drivers/power/mfd/ \
 663         drivers/power/pmic/ \
 664         drivers/power/charge/ \
 665         drivers/power/battery/
 666 libs-y += drivers/spi/
 667 libs-$(CONFIG_FMAN_ENET) += drivers/net/fm/
 668 libs-$(CONFIG_SYS_FSL_DDR) += drivers/ddr/fsl/
 669 libs-y += drivers/serial/
 670 libs-y += drivers/usb/eth/
 671 libs-y += drivers/usb/gadget/
 672 libs-y += drivers/usb/host/
 673 libs-y += drivers/usb/musb/
 674 libs-y += drivers/usb/musb-new/
 675 libs-y += drivers/usb/phy/
 676 libs-y += drivers/usb/ulpi/
 677 libs-y += common/
 678 libs-y += lib/libfdt/
 679 libs-$(CONFIG_API) += api/
 680 libs-$(CONFIG_HAS_POST) += post/
 681 libs-y += test/
 682 libs-y += test/dm/
 683 
 684 ifneq (,$(filter $(SOC), mx25 mx27 mx5 mx6 mx31 mx35 mxs vf610))
 685 libs-y += arch/$(ARCH)/imx-common/
 686 endif
```
值得注意的是，其中的 VENDOR、CPU、SOC、DIR、ARCH 宏是定义在 config.mk 。

第三个参数 u-boot.lds 定义为
```
1245 u-boot.lds: $(LDSCRIPT) prepare FORCE
1246         $(call if_changed_dep,cpp_lds)
```
```
 546 # If there is no specified link script, we look in a number of places for it
 547 ifndef LDSCRIPT
 548         ifeq ($(wildcard $(LDSCRIPT)),)
 549                 LDSCRIPT := $(srctree)/board/$(BOARDDIR)/u-boot.lds
 550         endif
 551         ifeq ($(wildcard $(LDSCRIPT)),)
 552                 LDSCRIPT := $(srctree)/$(CPUDIR)/u-boot.lds
 553         endif
 554         ifeq ($(wildcard $(LDSCRIPT)),)
 555                 LDSCRIPT := $(srctree)/arch/$(ARCH)/cpu/u-boot.lds
 556         endif
 557 endif
```
对于上面三个 lds，优先级从前到后依次增加。

`prepare` 定义：
