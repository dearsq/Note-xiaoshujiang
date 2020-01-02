---
title: [Android7.1][RK3399] 移远EC20添加4G通话功能-ql-ril.conf
tags: android,ec20
---
Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.126

[TOC]

## 需求
1. 热插拔
2. 默认打开 UVC 功能

## 调试步骤
在移远提供的 ql-ril.conf 中添加
1. 添加 
```
Sim_Hot_Plugging=2
```
2. 添加　
```
At_Cmds_For_Customer_Initialize=AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,0,1;AT+QPCMV=1,2
```
如果不需要打开
```
At_Cmds_For_Customer_Initialize=AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,0,0;AT+QPCMV=0
```
ql-ril.conf 中的内容会在开机的时候由移远提供的 ril 库调用．写入到 EC20 的 NV 中．
即，如果没有其他的 AT 指令将其覆盖，掉电后也不会丢失．

## 调试接口
ql-ril.conf
```bash
#This file is in a state of unavailability.
#In most cases, there is no need to open any option.
#In special cases, please use it under the guidance of FAE.

#LTE_SignalStrength=-1
#LTE_Is_Report_SignalStrength=1
#At_Cmds_For_Customer_Initialize=at+csq;at+cgreg?;at+cops?;at+qcfg="nwscanmodeex"
#At_Cmds_For_Customer_Initialize=AT+QSIMDET=1,1;AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,1,1
At_Cmds_For_Customer_Initialize=AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,0,1;
#Icc_Constants=EF_ICCID
#support_CDMPhone=1
#URC_delay_mseconds=2000
#Query_Available_Networks=1
#0-not support; 1-support low level; 2-support high level
Sim_Hot_Plugging=2

```