---
title: SOP_MediaPlayer.md
tags: android
grammar_cjkRuby: true
---

## 常用控制方法
Android 通过控制播放器的状态的方式来控制媒体文件的播放，其中：

`setDataSource()` 设置要播放的音频文件位置
`prepare()和 prepareAsync()` 完成准备工作
提供了同步和异步两种方式设置播放器进入prepare状态，
需要注意的是，如果MediaPlayer实例是由create方法创建的，那么第一次启动播放前不需要再调用prepare（）了，因为create方法里已经调用过了。
`start()`是真正启动文件播放的方法，
`pause()` 暂停播放
`stop()` 停止播放
`seekTo()` 是定位方法，可以让播放器从指定的位置开始播放，
需要注意的是该方法是个异步方法，也就是说该方法返回时并不意味着定位完成，尤其是播放的网络文件，真正定位完成时会触发OnSeekComplete.onSeekComplete()，如果需要是可以调用 setOnSeekCompleteListener(OnSeekCompleteListener)设置监听器来处理的。
`release()` 可以释放播放器占用的资源，一旦确定不再使用播放器时应当尽早调用它释放资源。
`reset()` 可以使播放器从 Error 状态中恢复过来，重新会到 Idle 状态。
`isPlaying()` 判断当前的 MediaPlayer 是否正在播放音频
`getDuration()` 获取载入的音频文件的时长

## 使用 SOP
### 1. 实例化
可以使用直接new的方式：
```
	MediaPlayer mp = new MediaPlayer();
```
    
也可以使用create的方式，如：
```
	MediaPlayer mp = MediaPlayer.create(this, R.raw.test_media_file_rsid);//这时就不用调用setDataSource了
```
### 2. 设置音频文件路径 setDataSource
MediaPlayer要播放的文件主要包括3个来源：
a. 用户在应用中事先自带的resource资源
     例如：MediaPlayer.create(this, R.raw.test_media_file_rsid);
b. 存储在SD卡或其他文件路径下的媒体文件
     例如：mp.setDataSource("/sdcard/test.mp3");
c. 网络上的媒体文件
   例如：mp.setDataSource("http://www.xxx.com/test.mp3");

MediaPlayer的setDataSource一共四个方法：
       setDataSource (String path)
       setDataSource (FileDescriptor fd)
       setDataSource (Context context, Uri uri)
       setDataSource (FileDescriptor fd, long offset, long length)

### 3. 进入准备状态 prepare()
### 4. 操作
start() / pause() / reset()

4）设置播放器的监听器：

   MediaPlayer提供了一些设置不同监听器的方法来更好地对播放器的工作状态进行监听，以期及时处理各种情况，

如： setOnCompletionListener(MediaPlayer.OnCompletionListener listener)、

         setOnErrorListener(MediaPlayer.OnErrorListener listener)等,设置播放器时需要考虑到播放器可能出现的情况设置好监听和处理逻辑，以保持播放器的健壮性。