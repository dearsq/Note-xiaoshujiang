---
title: [Android7.1][RK3399] 只保留 USB Camera (去掉对 Mipi DVP Camera 的支持)
tags: android
grammar_cjkRuby: true
---

## 应用场景
rk3399平台可以支持多种不同接口的Camera,如MIPI, DVP, UVC camera。 
对于DVP,MIPI的Camera,对应的配置是放在cam_board.xml的。 
因此如果只使用UVC Camera，那么只要移除此文件就可以了。

## 解决方案
```
--- a/Config/rk32xx_camera.mk
+++ b/Config/rk32xx_camera.mk
       hardware/rockchip/camera/SiliconImage/isi/drv/GS8604/calib/GS8604_lens_9569A2.xml:system/etc/GS8604_lens_9569A2.xml \ hardware/rockchip/camera/SiliconImage/isi/drv/GS8604/calib/GS8604_lens_40100A.xml:system/etc/GS8604_lens_40100A.xml \
     hardware/rockchip/camera/SiliconImage/isi/drv/OV2680/calib/OV2680.xml:system/etc/OV2680.xml \
-    hardware/rockchip/camera/SiliconImage/isi/drv/HM5040/calib/HM5040.xml:system/etc/HM5040.xml \
-    hardware/rockchip/camera/Config/cam_board_rk3399.xml:system/etc/cam_board.xml
+    hardware/rockchip/camera/SiliconImage/isi/drv/HM5040/calib/HM5040.xml:system/etc/HM5040.xml
+    #hardware/rockchip/camera/Config/cam_board_rk3399.xml:system/etc/cam_board.xml
```
改动之后，camera_get_number_of_cameras()中的读取cam_board.xml的代码就会失效，相关代码：
```
int camera_get_number_of_cameras(void)
{
....
    profiles = camera_board_profiles::getInstance();
    nCamDev = profiles->mDevieVector.size();
    LOGD("board profiles cam num %d\n", nCamDev);
    //由于读取不到配置，所以nCamDev为0.
    if (nCamDev>0){
        camera_board_profiles::LoadSensor(profiles);
        char sensor_ver[32];

        for (i=0; (i<nCamDev); i++) 
        {  
            LOGE("load sensor name(%s) connect %d\n", profiles->mDevieVector[i]->mHardInfo.mSensorInfo.mSensorName, profiles->mDevieVector[i]->mIsConnect);
            if(profiles->mDevieVector[i]->mIsConnect==1){
                rk_sensor_info *pSensorInfo = &(profiles->mDevieVector[i]->mHardInfo.mSensorInfo);

                camInfoTmp[cam_cnt&0x01].pcam_total_info = profiles->mDevieVector[i];     
                strncpy(camInfoTmp[cam_cnt&0x01].device_path, pSensorInfo->mCamsysDevPath, sizeof(camInfoTmp[cam_cnt&0x01].device_path));
                strncpy(camInfoTmp[cam_cnt&0x01].driver, pSensorInfo->mSensorDriver, sizeof(camInfoTmp[cam_cnt&0x01].driver));
                unsigned int SensorDrvVersion = profiles->mDevieVector[i]->mLoadSensorInfo.mpI2cInfo->sensor_drv_version;
                memset(version,0x00,sizeof(version));
                sprintf(version,"%d.%d.%d",((SensorDrvVersion&0xff0000)>>16),
                        ((SensorDrvVersion&0xff00)>>8),SensorDrvVersion&0xff);

                if(pSensorInfo->mFacing == RK_CAM_FACING_FRONT){     
                    camInfoTmp[cam_cnt&0x01].facing_info.facing = CAMERA_FACING_FRONT;                  
                } else {
                    camInfoTmp[cam_cnt&0x01].facing_info.facing = CAMERA_FACING_BACK;
                } 

                memset(sensor_ver,0x00,sizeof(sensor_ver));
                if (strlen(pSensorInfo->mSensorName) < (sizeof(sensor_ver)-16))
                    sprintf(sensor_ver,"%s%s%s","sys_graphic.",pSensorInfo->mSensorName,".ver");
                else 
                    sprintf(sensor_ver,"%s",pSensorInfo->mSensorName);                
                property_set(sensor_ver, version);  

                camInfoTmp[cam_cnt&0x01].facing_info.orientation = pSensorInfo->mOrientation;
                cam_cnt++;

                unsigned int CamsysDrvVersion = profiles->mDevieVector[i]->mCamsysVersion.drv_ver;
                memset(version,0x00,sizeof(version));
                sprintf(version,"%d.%d.%d",((CamsysDrvVersion&0xff0000)>>16),
                    ((CamsysDrvVersion&0xff00)>>8),CamsysDrvVersion&0xff);
                property_set(CAMERAHAL_CAMSYS_VERSION_PROPERTY_KEY,version);
            }
        }
    }
....
}
```