---
title: [Android7.1][RK3399] WiFi 吞吐率周期性变差问题(扫描机制)
tags: android
grammar_cjkRuby: true
---

Platform: RK3399  
OS: Android 7.1  
Kernel: v4.4.83

[TOC]

参考文章:
Android wifi扫描机制(Android O): https://blog.csdn.net/h784707460/article/details/79658950
Android wifi PNO扫描流程(Andriod O) :https://blog.csdn.net/h784707460/article/details/79702275

## 四种场景
亮屏情况： 
1. 在WiFi Settings界面，无论WiFi是否有连接，固定扫描时间间隔为10s。 
2. 在非WiFi Settings界面，无论WiFi是否有连接，固定扫描时间间隔以2的倍数慢慢拉大扫描周期，最小为20s，最大为160s. 
> 二进制指数退避扫描, 退避算法:interval*(2^n) .

灭屏情况： 
有保存网络 , 已经连接 , 不扫描.
有保存网络 , 没有连接 , PNO 扫描 (只扫描已经保存的网络) , 间隔 min=20s max=160s

其他情况： 
当没有保存网络的时候，固定扫描时间间隔为 5min。


## 亮屏情况

### WiFi Setting界面 
进入WiFi Setting界面时，会调用对应Activity的onResume()。

```
onResume -> WifiSettings.java
  mWifiTracker.startTracking ->
    startTracking -> WifiTracker.java
      resumeScanning ->
        mScanner.resume ->
         resume->
           sendEmptyMessage(MSG_SCAN); ->
             handleMessage ->   //Scanner类
               mWifiManager.startScan -> //调用WiFi Service开始扫描。
               sendEmptyMessageDelayed(0, WIFI_RESCAN_INTERVAL_MS); //发送下次扫描时间间隔
```
WIFI_RESCAN_INTERVAL_MS默认定义为10秒。
```
// Combo scans can take 5-6s to complete - set to 10s.
private static final int WIFI_RESCAN_INTERVAL_MS = 10 * 1000;          
```
### 非WiFi Setting界面
```
// Start a connectivity scan. The scan method is chosen according to
// the current screen state and WiFi state.
startConnectivityScan ->
  startPeriodicScan ->  //mScreenOn为true
    mPeriodicSingleScanInterval = PERIODIC_SCAN_INTERVAL_MS;    //设置扫描间隔为20s
    startPeriodicSingleScan ->
      mPeriodicSingleScanInterval *= 2; //每扫描一次，时间拉长一倍，最大不能超过MAX_PERIODIC_SCAN_INTERVAL_MS即160s
      startSingleScan ->
        mScanner.startScan  //开始扫描
```


## 灭屏情况
```
startConnectivityScan ->
  startConnectedPnoScan -> //screenOff以及WiFi已经有连接的情况
    scanSettings.periodInMs = CONNECTED_PNO_SCAN_INTERVAL_MS; //设置扫描周期为160S
    mScanner.startConnectedPnoScan ->
      startPnoScan
  startDisconnectedPnoScan -> //screenOff以及WiFi没有连接但有保存的情况
    scanSettings.periodInMs = DISCONNECTED_PNO_SCAN_INTERVAL_MS; //设置扫描周期为20S
    mScanner.startDisconnectedPnoScan ->
      startPnoScan
```
没有保存网络的时候：
```
class DisconnectedState extends State {

    /**
     * If we have no networks saved, the supplicant stops doing the periodic scan.
     * The scans are useful to notify the user of the presence of an open network.
     * Note that these are not wake up scans.
     */
    if (mNoNetworksPeriodicScan != 0 && !mP2pConnected.get()
            && mWifiConfigManager.getSavedNetworks().size() == 0) {
        sendMessageDelayed(obtainMessage(CMD_NO_NETWORKS_PERIODIC_SCAN,
                ++mPeriodicScanToken, 0), mNoNetworksPeriodicScan);
    }
}
```
mNoNetworksPeriodicScan的值被定义在 frameworks/base/core/res/res/values/config.xml中
```
<integer translatable="false" name="config_wifi_framework_scan_interval">300000</integer>1
```
WiFi Setting和非Settings界面的扫描是同时不干预并存工作的.
其中35秒和75秒是非WiFi界面的周期扫描，间隔40秒，说明是第二次(20 x 2)扫描了。 
其他的是在WiFi Settings界面扫描，每10秒一次。