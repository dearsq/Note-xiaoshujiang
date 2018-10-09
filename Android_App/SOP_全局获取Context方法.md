---
title: SOP_全局获取Context方法
tags: android
grammar_cjkRuby: true
---


利用 Application 类.
当应用程序启动时 , 系统会自动对 Applicaiton 类进行初始化.
我们可以定制自己的一个 Application 类, 以便于管理程序内的 **全局状态信息**.

### 自定义 WholeApplication 类
```
public class WholeApplication extends Application {
	private static Context context;
    
    public void onCreate() {
    	context = getApplicationContext();
    }
    
    public static Context getContext() {
    	return context;
    }
}
```

### 告知系统,程序启动时应该初始化 WholeApplication 而不是 Application
```xml
<application 
	android:name="com.iyounix.practice.wholeapplication" >
	
</application>
```

### 使用方法
任何想要用到 context 的地方 , 使用 WholeApplication.getContext() , 比如:
```
Toast.makeText(WholeApplication.getContext(), "test" , Toast.LENGTH_SHORT).show();
```

### 问题
比如为了让 litepal 正常工作 , 需要声明 : 
```xml
<application 
	android:name="org.litepal.LitePalApplication" 
    ...>
</application>
```
并且在 WholeApplication 的 onCreate() 中初始化:
```
public void onCreate() {
	context = getApplicationContext();
    LitePalApplication.initialize(context);
}
```
