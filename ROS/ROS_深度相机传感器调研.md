title: ROS_深度相机传感器调研
date: 2020-7-23 21:00:00
tags: Robot,机器人,

---

本文的观点大部分来自于网络搜集的论文、杂志、博客。
是个人的学习阶段整理的资料，如果错误还望海函指正。

[TOC]

深度相机主流的有三种类型：
* TOF 
	* i-ToF
	* d-ToF
* 双目
	* RGB 双目
	* IR 双目
* 结构光
	* 单目IR+投影IR点阵
	* 双目IR+投影IR点阵
	* 单目IR+投影相移条纹
 
 
 后文是对比三种主流相机的各项指标。
 包括：
 ```
#### 工作原理
#### 硬件指标
#####  功耗
#####  测量精度
#####  分辨率
#####  帧率
#####  量产标定
#### 技术瓶颈
 ```
 
 ### ToF

 ToF 全称 Time-of-Flight ，分为 
 i-ToF(indirect Time-of-Flight) 相位测距
 d-Tof(direct Time-of-Flight）时间测距

#### 工作原理
ToF 技术测量相机是指主动投射出的光束经过目标表面反射后被相机接收这个过程的来回的飞行时间，基于光速即可获得目标到相机的距离。
ToF 传感器给到光源驱动芯片调制信号，调制信号控制激光器发出高频脉冲调制(CW正弦 / PL脉冲)的近红外光，遇到物体漫反射后，接收端通过发射光与接收光的相位差或时间差来计算深度信息。
![enter description here](./images/1595493968644.png)
其中 i-ToF 是根据 CIS（Camera Image Sensor）获取到的模拟信号进行测距。
其中 d-ToF 是根据 SPAD Array（单光子雪崩二极管阵列）获取的数字信号进行测距。

#### 硬件指标
##### 功耗
ToF 的方案功耗偏高，全面照射，且高频脉冲。
i-ToF 的功耗高
d-ToF 的功耗中

#####  测量精度
和距离呈线性关系
在厘米级别

#####  分辨率
一般达不到 VGA（640x480）

#####  帧率
高 100+ fps

##### 量产标定
i-ToF 麻烦
d-ToF 中等

#### 技术瓶颈
1. 飞点噪声（Flying pixels）
每个像素都具有一定的物理尺寸，在测量物体边缘时，单个像素会同时接收到前景和背景反射回来的光线；二者产生的能量叠加在一起，使得传感器获取的原始数据中包含多个距离的信息，解算相位计算距离时将得到错误的深度测量值。
导致物体边缘处往往存在大量错误的深度测量值，生成3D点云后,视觉上表现为飞在空中的无效点。
即无法有效获取物体边缘的3D信息。
通过边缘检测算法解决。
2. 多径干扰（Multi-Path Interference，MPI）
真实场景中存在复杂的漫反射甚至镜面反射，
导致原理上会使得测量值变大，严重影响三维重建的效果。
无法解决。
3. 强度误差（Intensity Realted Error）
同一平面上不同反射率的区域体现出不同的深度。
4. 远距离-高精度矛盾（Trade-off between range and precision）
5. 高频驱动
为了保证测量精度，CW-iToF采用提高调制频率的方式，PL-iToF则采用窄脉冲高峰值功率的驱动方式。综合起来，iToF对于驱动芯片的主要需求是高调制频率和高峰值功率。
6. 片上集成
主流的i-ToF传感器像素一般在QVGA（320x240）上下


### 双目

#### 工作原理
三角几何视差来获得目标到相机的距离信息。
具体的说，就是从两个相机观察同一物体，被观测物体在两个相机中拍摄到的图像中的位置会有一定位置差。
距离越近，视差越大。在已知两个相机间距等相对位置关系的情况下，即可通过相似三角形的原理计算出被摄物到相机的距离。

![enter description here](./images/1595493146218.png)

![enter description here](./images/1595493159487.png)

#### 硬件指标
##### 功耗
低～高 都有，大部分功耗比较低
#####  测量精度
近距离有着很高的精度，但是误差会随着距离增大而平方变大。
近距离可达毫米级别。
#####  分辨率
RGB双目 可达2k分辨率
#####  帧率
高60fps
##### 量产标定
容易
#### 技术瓶颈
1. 计算量大。
通过加算法芯片 ASIC 解决。
2. 依赖被摄物体纹理和环境光照。
比如白墙，无法匹配对应像素的问题。

### 结构光
#### 工作原理
原理本质和双目的一样，也是使用三角法。
![enter description here](./images/1595493170390.png)

单目IR+投影IR点阵
双目IR+投影IR点阵
单目IR+投影相移条纹

#### 硬件指标
##### 功耗
中，需要投射图案，只照射局部区域
#####  测量精度
近距离有着很高的精度，但是误差会随着距离增大而平方变大。
近距离可达毫米级别。
#####  分辨率
可以达到1080P
#####  帧率
低 30fps
##### 量产标定
中等难度
#### 技术瓶颈
1. 高计算量。
通过加算法芯片 ASIC 解决。
2. 深度突变处的数据缺失
通过基于 ARM 的软核算法即可解决。
 
 
 ### 市场主流方案
 
#### Intel Realsense SR300 
类型：结构光（编码光）
![enter description here](./images/1595494407932.png)
![enter description here](./images/1595494411074.png)

距离：0.2-1.5米

介绍：
https://www.intelrealsense.com/coded-light/
论坛：https://community.intel.com/t5/tag/Intel%C2%AE%20RealSense/tg-p/tag-id/513
采购：
https://store.intelrealsense.com/buy-intel-realsense-depth-module-sr300.html

### Intel Realsense D435
类型：结构光（主动立体IR）
![enter description here](./images/1595494484438.png)

距离：0.1-10米
介绍：
https://www.intelrealsense.com/zh-hans/depth-camera-d435/


### 乐动 TOF IDC3224R_LD01
3D TOF 高分辨率深度摄像头

![enter description here](./images/1595494531739.png)

范围：0.2-4米
分辨率：320x240
FOV：92°X 74°X 57°

应用场景：机器人精准定位与建图、导航与避障、人脸/肢体/物体识别、AR/VR等。
介绍：https://www.ldrobot.com/product/43


### 乐视LeTMC-520 （奥比中光）
三目相机
IR投影 


![enter description here](./images/1595494702321.png)

![enter description here](./images/1595494721728.png)

![enter description here](./images/1595494751591.png)