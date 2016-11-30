---
title: Cardboard Treasure Hunter 代码分析
tags: VR,Cardboard
grammar_cjkRuby: true
---

### Manifest file
```xml
<manifest ...
    <uses-permission android:name="android.permission.NFC" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

    <uses-permission android:name="android.permission.VIBRATE" />
    ...
    <uses-sdk android:minSdkVersion="19" android:targetSdkVersion="23"/>
    <uses-feature android:glEsVersion="0x00020000" android:required="true" />
    <application
            ...
        <activity
                android:name=".MainActivity"
                android:screenOrientation="landscape">
                ...

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
                <category android:name="com.google.intent.category.CARDBOARD" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### Extend GvrActivity
GvrActivity 是最基本的 activity，它提供了 Google VR 设备的简单集成。它暴露时间来和 VR 进行交互，并且处理创建 VR 渲染的一些细节。

GvrActivity 是沉浸模式（ immersive mode），系统 UI 被隐藏，内容将会占据整个屏幕。这是 VR app 的要求，因为只有 activity 全屏的情况下 GvrView 才会渲染。

MainActivity extends GvrActivity，implements GvrView.StereoRenderer。
GvrView.StereoRenderer 这个接口是为渲染器设计的，它将会委托所有的立体渲染细节给视图。接口器应该简单的渲染一个视图，因为他们常常变换参数。所有的立体渲染和畸变校正细节都是从渲染器中抽象出来的，并由内部视图管理。

### Define a GvrView
所有用户接口元素都是用 View 实现的。Google VR SDK 提供了 GvrView，用来进行 VR 渲染。

```xml
<com.google.vr.sdk.base.GvrView
    android:id="@+id/gvr_view"
    android:layout_width="fill_parent"
    android:layout_height="fill_parent"
    android:layout_alignParentTop="true"
    android:layout_alignParentLeft="true" />
```
主 activity 中的 onCreate() 里面来初始化。
```java
/**
 * Sets the view to our GvrView and initializes the transformation matrices
 * we will use to render our scene.
 */
@Override
public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.common_ui);
    GvrView gvrView = (GvrView) findViewById(R.id.gvr_view);
    // Associate a GvrView.StereoRenderer with gvrView.
    gvrView.setRenderer(this);
    // Associate the gvrView with this activity.
    setGvrView(gvrView);

    // Initialize other objects here.
    ...
}
```
### Render View
一旦你得到了 GvrView 并将它和 渲染器（Renderer） 关联，接下来将它与 activity 关联。
Google VR 支持两种渲染器（Renderer），最快的方法还是采用 GvrView.StereoRenderer，它包括了以下方法
* onNewFrame(), called every time that app renders.
* onDrawEye(), called for each eye with different eye parameters.

用法和 OpenGL 应用类似。

### Implement onNewFrame
在渲染单个眼睛之前，使用onNewFrame（）方法来对渲染逻辑进行编码。任何不特定于单个视图的 每帧操作 都应在此处发生。这是更新模型的好地方。在这个片段中，变量 mHeadView 包含头的位置。该值需要保存以供稍后使用，以判断用户是否正在查看宝藏:
```java
/**
 * Prepares OpenGL ES before we draw a frame.
 * @param headTransform The head transformation in the new frame.
 */
@Override
public void onNewFrame(HeadTransform headTransform) {
    ...
    headTransform.getHeadView(mHeadView, 0);
    ...
}
```

### Implement onDrawEye
onDrawEye（）接口来执行每眼配置。

下面的代码展示了如何获得 视图转化为矩阵、透视转换为矩阵。
你要确保是低延迟。Eye 对象包括了 眼睛的变换和投影矩阵。
```java
/**
 * Draws a frame for an eye.
 *
 * @param eye The eye to render. Includes all required transformations.
 */
@Override
public void onDrawEye(Eye eye) {
    GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT | GLES20.GL_DEPTH_BUFFER_BIT);
    ...
    // Apply the eye transformation to the camera.
    Matrix.multiplyMM(mView, 0, eye.getEyeView(), 0, mCamera, 0);

    // Set the position of the light
    Matrix.multiplyMV(mLightPosInEyeSpace, 0, mView, 0, LIGHT_POS_IN_WORLD_SPACE, 0);

    // Build the ModelView and ModelViewProjection matrices
    // for calculating cube position and light.
    float[] perspective = eye.getPerspective(Z_NEAR, Z_FAR);
    Matrix.multiplyMM(mModelView, 0, mView, 0, mModelCube, 0);
    Matrix.multiplyMM(mModelViewProjection, 0, perspective, 0, mModelView, 0);
    drawCube();

    // Draw the rest of the scene.
    ...
}
```
事件的顺序是 
1. Treasure 进入 Eye 的区域
2. 应用投影矩阵，这为指定的眼睛提供渲染场景。
3. Google VR SDK 自动应用畸变算法，来渲染最终的场景。

### Rendering spatial audio
onCreate（）方法初始化3D音频引擎。 GvrAudioEngine的构造函数中的第二个参数允许用户指定定义空间化保真度的渲染模式。
```java
gvrAudioEngine =
    new GvrAudioEngine(this, GvrAudioEngine.RenderingMode.BINAURAL_HIGH_QUALITY);
```
要在用户暂停应用程序时禁用音频，并在恢复时再次启用，请分别在onPause（）和onResume（）函数调用gvrAudioEngine.pause（）;和gvrAudioEngine.resume（）。
声音文件可在播放期间流式传输或在播放前预先载入内存。此预加载应在单独的线程上执行，以避免主线程的阻塞。
```java
new Thread(
        new Runnable() {
          @Override
          public void run() {
            gvrAudioEngine.preloadSoundFile(SOUND_FILE);
          }
        })
    .start();
```
One can create, position, and play back sound objects at any time, using createSoundObject(). Any number of sound objects can be created from the same preloaded sound file. Note that if sounds have not previously been preloaded, the sound file will be streamed from disk on playback.
```java
// Start spatial audio playback of SOUND_FILE at the model postion. The returned
// sourceId handle allows for repositioning the sound object whenever the cube
// position changes.
sourceId = gvrAudioEngine.createSoundObject(SOUND_FILE);
gvrAudioEngine.setSoundObjectPosition(
    sourceId, modelPosition[0], modelPosition[1], modelPosition[2]);
gvrAudioEngine.playSound(sourceId, true /* looped playback */);
```
The sourceId handle can be used to reposition the sound during run time.
```java
// Update the sound location to match it with the new cube position.
if (sourceId != GvrAudioEngine.INVALID_ID) {
  gvrAudioEngine.setSoundObjectPosition(
      sourceId, modelPosition[0], modelPosition[1], modelPosition[2]);
}
```
In the onNewFrame method, we get a quaternion representing the latest position of the user's head, and pass that to setHeadRotation() to update the gvrAudioEngine.
```java
// Update the 3d audio engine with the most recent head rotation.
headTransform.getQuaternion(headRotation, 0);
gvrAudioEngine.setHeadRotation(
    headRotation[0], headRotation[1], headRotation[2], headRotation[3]);
Calls to gvrAudioEngine.update() should be made once per frame.
```


### Handling inputs
Cardboard  Viewers 包含使用了触摸模拟器的触发按钮（Trigger Button）。当您拉动触发器时，Viewwer 触摸您的手机屏幕。这些触发事件由Google VR SDK为您检测。

要在用户拉动触发器时提供 自定义行为，要在 activity 中重写 GvrActivity.onCardboardTrigger（）。在寻宝应用程序中，例如，当你找到一个宝藏并拉动触发器，立方体移动到一个新的地方。
```java
/**
 * Called when the Cardboard trigger is pulled.
 */
@Override
public void onCardboardTrigger() {
    if (isLookingAtObject()) {
        hideObject();
    }

    // Always give user feedback
    mVibrator.vibrate(50);
}
```