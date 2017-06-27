---
title: [NFC] NFC 程序设计（基础知识）
tags: nfc,android,nfcadapter,nfcmanager
grammar_cjkRuby: true
---
android 官方手册：[NFC Developer][1]

Android平台提供了两个**android.nfc** 和**android.nfc.tech**包,里面有API来实现NFC标签的操作。

## android.nfc
**android.nfc** 包中主要有四个类：
**NfcManager类**：可以用来管理Android设备中指出的所有NFC Adapter，但由于大部分Android设备只支持一个NFC
Adapter，可以直接使用getDefaultAapater方法来获取系统支持的Adapter。
**NfcAdapter类**：本设备的NFC adapter,可以定义Intent来请求将系统检测到tags的提醒发送到你的Activity，并提供方
法去注册前台tag提醒发布和前台NDEF推送。
**NdefMessage类**：NDEF是NFC论坛定义的数据结构，用来有效的存数据到标签中，如文本，URL，和其他MIME类
型。一个NdefMessage扮演一个容器，这个容器存哪些发送和读到的数据。一个NdefMessage对象包含0或多个
NdefRecord，每个NDEF record有一个类型，比如文本，URL，智慧型海报/广告，或其他MIME数据。在
NDEFMessage里的第一个NfcRecord的类型用来发送tag到一个android设备上的activity。
**Tag类**：标示一个被动的NFC目标，比如tag，card，钥匙挂扣，甚至是一个电话模拟的的NFC卡。可提供对标签的各
种操作方法。

## android.nfc.tech
**android.nfc.tech包**包含对 Tag 查询属性 和 I/O 操作的类。
这些类分别标示一个tag支持的不同的NFC技术标准。
TagTechnology： 这个接口是下面所有tag technology类必须实现的。
NfcA： 支持ISO 14443-3A 标准的属性和I/O操作。
NfcB：NFC-B (ISO 14443-3B)的属性和I/O操作。
NfcF：NFC-F (JIS 6319-4)的属性和I/O操作。
NfcV： NFC-V (ISO 15693)的属性和I/O操作。
IsoDep：ISO-DEP (ISO 14443-4)的属性和I/O操作。
Ndef：对支持NDEF格式的标签进行读写操作。
NdefFormatable： 对那些可以被格式化成NDEF格式的tag提供一个格式化的操作。
MifareClassic： 如果android设备支持MIFARE，提供对MIFARE Classic目标的属性和I/O操作。
MifareUltralight： 如果android设备支持MIFARE，提供对MIFARE Ultralight目标的属性和I/O操作。


## NFC编程基本步骤
### 权限
```xml
<uses-permission android:name="android.permission.NFC" />
```
### 限制版本号
```xml
<uses-sdk
        android:minSdkVersion="19"
        android:targetSdkVersion="19" />
```
### 限制安装的设备
```xml
<uses-feature
        android:name="android.hardware.nfc"
        android:required="true" />
```
### 定义可接受 Tag 的 Activity
### 处理业务逻辑
根据便签的具体业务

### NFC 标签过滤系统
![](http://ww3.sinaimg.cn/large/ba061518gw1f5556j9ytbj20lf0awjse.jpg)

### NfcManager 类详解
Use getSystemService(java.lang.String) with NFC_SERVICE to create an NfcManager, then call getDefaultAdapter() to obtain the NfcAdapter.
Alternately, you can just call the static helper getDefaultAdapter(android.content.Context).

public static NfcAdapter getDefaultAdapter (Context context)：获取手机中默认的NFC设备，一般一部手机就只有一个NFC模块，所有调用此方法即可。

### NfcAdapter 类详解
#### **重要的常量**
用于从Intent中获取获取信息，这个Intent是NFC检测到Tag后由系统发起的，由 getIntent().getParcelableExtra(NfcAdapter.常量名); 方法获取相应对象）：
**EXTRA_TAG**(必须的)：它是一个代表了被扫描到的标签的Tag对象；可通过 getParcelableExtra(NfcAdapter.EXTRA_TAG) 获得标签对象。
**EXTRA_NDEF_MESSAGES**(可选)：它是一个解析来自标签中的NDEF消息的数组。这个附加信息是强制在 Intent 对象上的；可通过 getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES）获得 NDEF 消息。
**EXTRA_ID**(可选)：标签的低级ID。
以下三个常量用于对获取的Intent中的Tag类型进行判断：
**ACTION_NDEF_DISCOVERED**：NfcAdapter.ACTION_NDEF_DISCOVERED.equals(getIntent().getAction())
**ACTION_TAG_DISCOVERED**：NfcAdapter.ACTION_TAG_DISCOVERED.equals(getIntent().getAction())
**ACTION_TECH_DISCOVERED**：NfcAdapter.ACTION_TECH_DISCOVERED.equals(getIntent().getAction())
#### **重要方法：**
```java
public boolean isEnabled ()  //用于判断当前NFC是否处于可用状态
public void enableForegroundDispatch (Activity activity, PendingIntent intent, IntentFilter[] filters, String[][]
techLists) //Enable foreground dispatch to the given Activity.用于打开前台调度（拥有最高的权限），当这个Activity 位于前台（前台进程），即可调用这个方法开启前台调度，一般位于onResume()回调方法中
public void disableForegroundDispatch (Activity activity) //关闭前台调度，一般位于onPause()回调方法中
```

### NdefMessage 类详解
以下三个方法用于构造一个NDEF数据 结构的的Tag数据（用于在Activity与标签之间的数据传递，读取与写入都要用该对象进行封装）
```java
public NdefMessage (byte[] data)
public NdefMessage (NdefRecord record, NdefRecord... records)
public NdefMessage (NdefRecord[] records)
public byte[] toByteArray ()
public int getByteArrayLength ()
public NdefRecord[] getRecords () //Get the NDEF Records inside this NDEF Message.
```

### NdefRecord 类详解
以下两个为构造方法：
```java
public NdefRecord (short tnf, byte[] type, byte[] id, byte[] payload)
public NdefRecord (byte[] data)
```
以下四个方法获取NdefRecord对象对应字段的类型：
```java
public byte[] getType ()
public short getTnf ()
public byte[] getPayload ()
public byte[] getId ()
```
Tag类详解：
```java
public String[] getTechList ()
// Get the technologies available in this tag, as fully qualified class names.
```
Ndef类详解：
该类用于对NDEF格式的Tag进行读写操作的封装，不同的Tag用不同的类封装，都在android.nfc.tech包中
```java
public static Ndef get (Tag tag)  
//Get an instance of Ndef for the given tag.构建对象
public void connect ()
//Enable I/O operations to the tag from this TagTechnology object.，打开I/O操作
public boolean isWritable ()
//Determine if the tag is writable.判断是否可写
public int getMaxSize ()
//Get the maximum NDEF message size in bytes.
public void writeNdefMessage (NdefMessage msg)
//Overwrite the NdefMessage on this tag.向这个Tag写入数据
public String getType ()
//Get the NDEF tag type.
public boolean makeReadOnly ()
//Make a tag read-only.
```
NdefFormatable类详解：
用于将其他类型的格式格式化成Ndef格式
```java
public static NdefFormatable get (Tag tag)
//Get an instance of NdefFormatable for the given tag.Returns null if NdefFormatable was not enumerated in getTechList(). This indicates the tag is not NDEF formatable by this Android device.
public void connect ()
//Enable I/O operations to the tag from this TagTechnology object.
public void format (NdefMessage firstMessage)
//Format a tag as NDEF, and write a NdefMessage.
```
### NFC 前台调度
将处理NFC标签的权利交给某个窗口（优先级最高）
1、在onCreate（）中获得NfcAdapter对象；
2、创建与该Activity关联的PendingIntent；
3、指定一个用于处理NFC标签的窗口；通常会在onResume（）方法中采用nfcAdapter.enableForegroundDispatch()
来实现；
4、禁止窗口处理NFC标签。采用 nfcAdapter.disableForegroundDispatch()来实现。
### 前台调度中onNewIntent方法的使用
如果IntentActivity处于任务栈的顶端，也就是说之前打开过的Activity，现在处于onPause、onStop状态的话，其他应用再发送Intent的话，执行顺序为：
onNewIntent，onRestart，onStart，onResume。
launchMode为singleTask的时候，通过Intent启到一个Activity,如果系统已经存在一个实例，系统就会将请求发送到这个实例上，但这个时候，系统就不会再调用通常情况下我们处理请求数据的onCreate方法，而是调用onNewIntent方法。
系统可能会随时杀掉后台运行的Activity，如果这一切发生，那么系统就会调用onCreate方法，而不调用onNewIntent方法，一个好的解决方法就是在onCreate和onNewIntent方法中调用同一个处理数据的方法。
onNewIntent()中的setIntent()和getIntent()，如果没有调用setIntent(intent)，则getIntent()获取的数据将不是你所期望的。所以最好是调用setIntent(intent)，这样在使用getIntent()的时候就不会有问题了。

  [1]: https://developer.android.com/reference/android/nfc/package-summary.html
