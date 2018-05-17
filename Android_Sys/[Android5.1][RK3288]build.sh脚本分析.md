---
title: [Android5.1][RK3288]build.sh脚本分析
tags: rockchip
grammar_cjkRuby: true
---

```bash
#!/bin/bash

source build/envsetup.sh >/dev/null && setpaths
TARGET_PRODUCT=`get_build_var TARGET_PRODUCT`

# source environment and chose target product
DEVICE=`get_build_var TARGET_PRODUCT`
BUILD_VARIANT=`get_build_var TARGET_BUILD_VARIANT`
UBOOT_DEFCONFIG=rk3288_defconfig
KERNEL_DEFCONFIG=rockchip_defconfig 
KERNEL_DTS=rk3288-tb_8846
PACK_TOOL_DIR=RKTools/linux/Linux_Pack_Firmware
IMAGE_PATH=rockdev/Image-$TARGET_PRODUCT
export PROJECT_TOP=`gettop`

lunch $DEVICE-$BUILD_VARIANT

PLATFORM_VERSION=`get_build_var PLATFORM_VERSION`
DATE=$(date  +%Y%m%d.%H%M)
STUB_PATH="$KERNEL_DTS"_"$PLATFORM_VERSION"_"$DATE"_RELEASE_TEST
#STUB_PATH=rk3288-tb_8846_
STUB_PATH="$(echo $STUB_PATH | tr '[:lower:]' '[:upper:]')"
export STUB_PATH=$PROJECT_TOP/$STUB_PATH
export STUB_PATCH_PATH=$STUB_PATH/PATCHES



# build uboot
echo "start build uboot"
cd u-boot && make distclean && make $UBOOT_DEFCONFIG && make -j32 && cd -
if [ $? -eq 0 ]; then
    echo "Build uboot ok!"
else
    echo "Build uboot failed!"
    exit 1
fi




# build kernel
echo "start build kernel"
cd kernel && make $KERNEL_DEFCONFIG && make $KERNEL_DTS.img -j32 && cd -
if [ $? -eq 0 ]; then
    echo "Build kernel ok!"
else
    echo "Build kernel failed!"
    exit 1
fi




# build android
echo "start build android"
make installclean
make -j32
if [ $? -eq 0 ]; then
    echo "Build android ok!"
else
    echo "Build android failed!"
    exit 1
fi



# mkimage.sh
echo "make and copy android images"
./mkimage.sh
if [ $? -eq 0 ]; then
    echo "Make image ok!"
else
    echo "Make image failed!"
    exit 1
fi
cp -f $IMAGE_PATH/* $PACK_TOOL_DIR/rockdev/Image/

# copy images to rockdev
echo "copy u-boot images"
cp u-boot/uboot.img $PACK_TOOL_DIR/rockdev/Image/
cp u-boot/RK3288UbootLoader* $PACK_TOOL_DIR/rockdev/RK3288UbootLoader.bin

echo "copy kernel images"
cp kernel/resource.img $PACK_TOOL_DIR/rockdev/Image
cp kernel/kernel.img $PACK_TOOL_DIR/rockdev/Image

echo "copy manifest.xml"
cp manifest.xml $IMAGE_PATH/manifest_${DATE}.xml

cd RKTools/linux/Linux_Pack_Firmware/rockdev && ./mkupdate.sh
if [ $? -eq 0 ]; then
    echo "Make update image ok!"
else
    echo "Make update image failed!"
    exit 1
fi
cd -

mkdir -p $STUB_PATH

#Generate patches
.repo/repo/repo forall  -c '[ "$REPO_REMOTE" = "rk" -a "$REPO_RREV" != "refs/tags/android-4.4.4_r2" ] && { REMOTE_DIFF=`git log $REPO_REMOTE/$REPO_RREV..HEAD`; LOCAL_DIFF=`git diff`; [ -n "$REMOTE_DIFF" ] && { mkdir -p $STUB_PATCH_PATH/$REPO_PATH/; git format-patch $REPO_REMOTE/$REPO_RREV..HEAD -o $STUB_PATCH_PATH/$REPO_PATH; } || :; [ -n "$LOCAL_DIFF" ] && { mkdir -p $STUB_PATCH_PATH/$REPO_PATH/; git reset HEAD ./; git diff > $STUB_PATCH_PATH/$REPO_PATH/local_diff.patch; } || :; }'
#Copy stubs
cp manifest.xml $STUB_PATH/manifest_${DATE}.xml

mkdir -p $STUB_PATCH_PATH/kernel
cp kernel/.config $STUB_PATCH_PATH/kernel

mkdir -p $STUB_PATH/IMAGES/
#mv $PACK_TOOL_DIR/rockdev/Image/* $STUB_PATH/IMAGES/
mv RKTools/linux/Linux_Pack_Firmware/rockdev/update.img $STUB_PATH/IMAGES/
mv $PACK_TOOL_DIR/rockdev/RK3288UbootLoader.bin $STUB_PATH/IMAGES/
cp $PACK_TOOL_DIR/rockdev/parameter $STUB_PATH/IMAGES/
cp $STUB_PATH/IMAGES/update.img rockdev/Image-$TARGET_PRODUCT
#
#Save build command info
echo "UBOOT:  defconfig: $UBOOT_DEFCONFIG" >> $STUB_PATH/build_cmd_info
echo "KERNEL: defconfig: $KERNEL_DEFCONFIG, dts: $KERNEL_DTS" >> $STUB_PATH/build_cmd_info
echo "ANDROID:$DEVICE-$BUILD_VARIANT" >> $STUB_PATH/build_cmd_info

```