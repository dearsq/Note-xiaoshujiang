---
title: [IoT4G] MTK 剥离出 Kernel、Preloader、LittleKernel
tags: 
grammar_cjkRuby: true
---

## 先查看 Android 编译过程中的打印信息
PLATFORM_VERSION_CODENAME=REL
PLATFORM_VERSION=6.0
TARGET_PRODUCT=full_bd6737m_35g_b_m0
TARGET_BUILD_VARIANT=eng
TARGET_BUILD_TYPE=release
TARGET_BUILD_APPS=
TARGET_ARCH=arm
TARGET_ARCH_VARIANT=armv7-a-neon
TARGET_CPU_VARIANT=cortex-a53
TARGET_2ND_ARCH=
TARGET_2ND_ARCH_VARIANT=
TARGET_2ND_CPU_VARIANT=cortex-a53
HOST_ARCH=x86_64
HOST_OS=linux
HOST_OS_EXTRA=Linux-4.2.0-42-generic-x86_64-with-Ubuntu-14.04-trusty
HOST_BUILD_TYPE=release
BUILD_ID=MRA58K
OUT_DIR=out


## 编译 Kernel

```
/kernel-3.18$ find ./arch/arm/ | grep bd6737m_35g_b_m0
./arch/arm/boot/dts/bd6737m_35g_b_m0.dts
./arch/arm/configs/bd6737m_35g_b_m0_debug_defconfig
./arch/arm/configs/bd6737m_35g_b_m0_defconfig

```
###  kernel-3.18$ make -j4 ARCH=arm bd6737m_35g_b_m0_defconfig O=out
```
kernel-3.18$ make ARCH=arm O=out bd6737m_35g_b_m0_defconfig
make[1]: Entering directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out'
  GEN     ./Makefile
warning: (ARCH_REQUIRE_GPIOLIB && PINCTRL_AT91 && PINCTRL_MTK_COMMON && PINCTRL_NOMADIK && MFD_TC6393XB && FB_VIA) selects GPIOLIB which has unmet direct dependencies (ARCH_WANT_OPTIONAL_GPIOLIB || ARCH_REQUIRE_GPIOLIB)
warning: (ARCH_REQUIRE_GPIOLIB && PINCTRL_AT91 && PINCTRL_MTK_COMMON && PINCTRL_NOMADIK && MFD_TC6393XB && FB_VIA) selects GPIOLIB which has unmet direct dependencies (ARCH_WANT_OPTIONAL_GPIOLIB || ARCH_REQUIRE_GPIOLIB)
#
# configuration written to .config
#
make[1]: Leaving directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out'
```

### make -j4 ARCH=arm 
报错 arm-eabi- not found

### make -j4 ARCH=arm CROSS_COMPILE=arm-eabi-
```
$ export PATH=/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/prebuilts/gcc/linux-x86/arm/arm-eabi-4.8/bin:$PATH
$ make -j4 ARCH=arm CROSS_COMPILE=arm-eabi-
  CHK     include/config/kernel.release
  CHK     include/generated/uapi/linux/version.h
/bin/sh: 1: cd: can't cd to /home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/tools/tools/
scripts/Makefile.include:16: *** output directory "/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/tools/tools/" does not exist.  Stop.
make: *** [tools/dct/DrvGen] Error 2
make: *** Waiting for unfinished jobs....
make: *** wait: No child processes.  Stop.
```

### make -j4 O=out ARCH=arm CROSS_COMPILE=arm-eabi-
```
$ mkdir out
$ make -j4 O=out ARCH=arm CROSS_COMPILE=arm-eabi-

make[1]: Entering directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out'
  GEN     ./Makefile
  HOSTCC  scripts/basic/fixdep
  HOSTCC  scripts/kconfig/conf.o
  HOSTCC  scripts/kconfig/zconf.tab.o
  HOSTLD  scripts/kconfig/conf
scripts/kconfig/conf --silentoldconfig Kconfig
warning: (ARCH_REQUIRE_GPIOLIB && PINCTRL_AT91 && PINCTRL_MTK_COMMON && PINCTRL_NOMADIK && MFD_TC6393XB && FB_VIA) selects GPIOLIB which has unmet direct dependencies (ARCH_WANT_OPTIONAL_GPIOLIB || ARCH_REQUIRE_GPIOLIB)
warning: (ARCH_REQUIRE_GPIOLIB && PINCTRL_AT91 && PINCTRL_MTK_COMMON && PINCTRL_NOMADIK && MFD_TC6393XB && FB_VIA) selects GPIOLIB which has unmet direct dependencies (ARCH_WANT_OPTIONAL_GPIOLIB || ARCH_REQUIRE_GPIOLIB)
make[1]: Leaving directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out'
make[1]: Entering directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out'
  CHK     include/config/kernel.release
  GEN     ./Makefile
  CHK     include/generated/uapi/linux/version.h
  UPD     include/generated/uapi/linux/version.h
../tools/dct/DrvGen ../drivers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws arch/arm/boot/dts/ arch/arm/boot/dts/ cust_dtsi
  HOSTCC  scripts/dtc/dtc.o
  CC      scripts/mod/empty.o
  UPD     include/config/kernel.release
  HOSTCC  scripts/dtc/flattree.o
  HOSTCC  scripts/mod/mk_elfconfig
  CC      scripts/mod/devicetable-offsets.s
In file included from ../include/asm-generic/int-ll64.h:10:0,
                 from ../arch/arm/include/asm/types.h:4,
                 from ../include/uapi/linux/types.h:4,
                 from ../include/linux/types.h:5,
                 from ../include/linux/mod_devicetable.h:11,
                 from ../scripts/mod/devicetable-offsets.c:2:
../include/uapi/asm-generic/int-ll64.h:11:29: fatal error: asm/bitsperlong.h: No such file or directory
 #include <asm/bitsperlong.h>
                             ^
compilation terminated.
make[3]: *** [scripts/mod/devicetable-offsets.s] Error 1
make[2]: *** [scripts/mod] Error 2
make[2]: *** Waiting for unfinished jobs....
  HOSTCC  scripts/dtc/fstree.o
  Using .. as source for kernel
  .. is not clean, please run 'make mrproper'
  in the '..' directory.
make[1]: *** [prepare3] Error 1
make[1]: *** Waiting for unfinished jobs....
  HOSTCC  scripts/dtc/data.o
  HOSTCC  scripts/dtc/livetree.o
  HOSTCC  scripts/dtc/treesource.o
  HOSTCC  scripts/dtc/srcpos.o
[dct info] ver_main: #1 ver_sub: #1 build time: 2015.10.15
[dct info] run code: #01.31.2018 16:03:09 #1033151218
[dct info] parameter count: 5
[dct info] param #0: ../tools/dct/DrvGen
[dct info] param #1: ../drivers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws
[dct info] param #2: arch/arm/boot/dts/
[dct info] param #3: arch/arm/boot/dts/
[dct info] param #4: cust_dtsi
  HOSTCC  scripts/dtc/checks.o
  HOSTCC  scripts/dtc/util.o
[dct info]source_file:/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/d
rivers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws
[dct info]gen_path:/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out/
arch/arm/boot/dts
[dct info]log_path:/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out/
arch/arm/boot/dts
[dct info]gen_files: 
=>> cust_dtsi
[dct info]dws file(/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/driv
ers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws) info: xml version: , xml Encoding: 
[dct warning]cannot parse dws file /home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/
kernel-3.18/drivers/misc/mediatek/mach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws: Encountered incorrect
ly encoded content.
[dct info]try to read dws file by using old dct tool.
  SHIPPED scripts/dtc/dtc-lexer.lex.c
  SHIPPED scripts/dtc/dtc-parser.tab.h
  SHIPPED scripts/dtc/dtc-parser.tab.c
  HOSTCC  scripts/dtc/dtc-lexer.lex.o
Enter main function!
The 0th param is: 
/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/tools/dct/old_dct/DrvGe
n
The 1th param is: 
/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/drivers/misc/mediatek/m
ach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws
The 2th param is: 
/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out/arch/arm/boot/dts/
The 3th param is: 
/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/out/arch/arm/boot/dts/
The 4th param is: 
cust_dtsi
begin to open log file!
DCT gen no log file for AOSP!
start to gen code!
start to read workspace!
/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-3.18/drivers/misc/mediatek/m
ach/mt6735/bd6737m_35g_b_m0/dct/dct/codegen.dws
start to parse fig file!
  HOSTCC  scripts/dtc/dtc-parser.tab.o
  HOSTLD  scripts/dtc/dtc
start to parse fig file!
Start to gen cust_eint.dtsi...
Gen cust_eint.dtsi successfully
Start to gen cust_gpio_usage_mapping.dtsi...
Gen cust_gpio_usage_mapping.dtsi file successfully!.
Start to gen cust_md1_eint.dtsi...
Gen cust_md1_eint.dtsi file successfully!.
Gen cust_pmic.dtsi file successfully!.
Start to gen cust_adc.dtsi...
Gen cust_adc.dtsi file successfully!.
Start to gen cust_clk_buf.dtsi...
Gen cust_clk_buf.dtsi file successfully!
Start to gen cust_kpd.dtsi...
Gen cust_kpd.dtsi file successfully!.
Start to gen cust_i2c.dtsi...
Gen cust_i2c.dtsi file successfully!.
make[1]: *** [scripts] Error 2
make[1]: Leaving directory `/home/orangepi/Public/MTK_SDK/OrangePi_4G-IoT_Linux/iot02_export/code/kernel-
3.18/out'
make: *** [sub-make] Error 2

```

```
  CC      drivers/misc/mediatek/imgsensor/src/mt6735m/gc2355_mipi_raw/gc2355mipi_Sensor.o
../drivers/misc/mediatek/imgsensor/src/mt6735m/gc2355_mipi_raw/gc2355mipi_Sensor.c:48:18: error: 'GC2355_
SENSOR_ID' undeclared here (not in a function)
     .sensor_id = GC2355_SENSOR_ID,        //record sensor id defined in Kd_imgsensor.h
                  ^
make[7]: *** [drivers/misc/mediatek/imgsensor/src/mt6735m/gc2355_mipi_raw/gc2355mipi_Sensor.o] Error 1
  LD      drivers/misc/mediatek/irtx/built-in.o
make[6]: *** [drivers/misc/mediatek/imgsensor/src/mt6735m/gc2355_mipi_raw] Error 2
make[5]: *** [drivers/misc/mediatek/imgsensor/src/mt6735m] Error 2
make[4]: *** [drivers/misc/mediatek/imgsensor/src] Error 2
make[4]: *** Waiting for unfinished jobs....
```




---

help:
        @echo  'Cleaning targets:'
        @echo  '  clean           - Remove most generated files but keep the config and'
        @echo  '                    enough build support to build external modules'
        @echo  '  mrproper        - Remove all generated files + config + various backup files'
        @echo  '  distclean       - mrproper + remove editor backup and patch files'
        @echo  ''
        @echo  'Configuration targets:'
        @$(MAKE) -f $(srctree)/scripts/kconfig/Makefile help
        @echo  ''
        @echo  'Other generic targets:'
        @echo  '  all             - Build all targets marked with [*]'
        @echo  '* vmlinux         - Build the bare kernel'
        @echo  '* modules         - Build all modules'
        @echo  '  modules_install - Install all modules to INSTALL_MOD_PATH (default: /)'
        @echo  '  firmware_install- Install all firmware to INSTALL_FW_PATH'
        @echo  '                    (default: $$(INSTALL_MOD_PATH)/lib/firmware)'
        @echo  '  dir/            - Build all files in dir and below'
        @echo  '  dir/file.[oisS] - Build specified target only'
        @echo  '  dir/file.lst    - Build specified mixed source/assembly target only'
        @echo  '                    (requires a recent binutils and recent build (System.map))'
        @echo  '  dir/file.ko     - Build module including final link'
        @echo  '  modules_prepare - Set up for building external modules'
        @echo  '  tags/TAGS       - Generate tags file for editors'
        @echo  '  cscope          - Generate cscope index'
        @echo  '  gtags           - Generate GNU GLOBAL index'
        @echo  '  kernelrelease   - Output the release version string (use with make -s)'
        @echo  '  kernelversion   - Output the version stored in Makefile (use with make -s)'
        @echo  '  image_name      - Output the image name (use with make -s)'
        @echo  '  headers_install - Install sanitised kernel headers to INSTALL_HDR_PATH'; \
         echo  '                    (default: $(INSTALL_HDR_PATH))'; \
         echo  ''
        @echo  'Static analysers'
        @echo  '  checkstack      - Generate a list of stack hogs'
        @echo  '  namespacecheck  - Name space analysis on compiled kernel'
        @echo  '  versioncheck    - Sanity check on version.h usage'
        @echo  '  includecheck    - Check for duplicate included header files'
        @echo  '  export_report   - List the usages of all exported symbols'
        @echo  '  headers_check   - Sanity check on exported headers'
        @echo  '  headerdep       - Detect inclusion cycles in headers'
        @$(MAKE) -f $(srctree)/scripts/Makefile.help checker-help
        @echo  ''
        @echo  'Kernel selftest'
        @echo  '  make V=0|1 [targets] 0 => quiet build (default), 1 => verbose build'
        @echo  '  make V=2   [targets] 2 => give reason for rebuild of target'
        @echo  '  make O=dir [targets] Locate all output files in "dir", including .config'
        @echo  '  make C=1   [targets] Check all c source with $$CHECK (sparse by default)'
        @echo  '  make C=2   [targets] Force check of all c source with $$CHECK'
        @echo  '  make RECORDMCOUNT_WARN=1 [targets] Warn about ignored mcount sections'
        @echo  '  make W=n   [targets] Enable extra gcc checks, n=1,2,3 where'
        @echo  '                1: warnings which may be relevant and do not occur too often'
        @echo  '                2: warnings which occur quite often but may still be relevant'
        @echo  '                3: more obscure warnings, can most likely be ignored'
        @echo  '                Multiple levels can be combined with W=12 or W=123'
        @echo  ''
        @echo  'Execute "make" or "make all" to build all targets marked with [*] '
        @echo  'For further info see the ./README file'


```
```