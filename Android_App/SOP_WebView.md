---
title: SOP_WebView.md 
tags: android
grammar_cjkRuby: true
---


## WebView 使用 SOP
### activity.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/web_view"
        android:layout_width="match_parent"
        android:layout_height="match_parent"></WebView>

</LinearLayout>
```

### MainActivity.java
```java
        WebView mWebView = findViewById(R.id.web_view);
        // 支持 JS 脚本
        mWebView.getSettings().setJavaScriptEnabled(true);
        // 当跳转网页的时候, 我们希望还是在当前 WebView 中,而不是访问浏览器
        mWebView.setWebViewClient(new WebViewClient());
        // 默认展现的网页
        mWebView.loadUrl("http://www.baidu.com");
```

### AndroidManifest.xml
```
<uses-permission android:name="android.permission.INTERNET"/>
```


## 特殊注意事项
### 子线程中完成服务器结束响应后的回调
在获取到服务器响应数据后, 可以对其进行解析和处理. 
但是网络请求是耗时操作, 需要放在子线程中进行.



## WebView_Http 基本介绍
Client 向 Server 发一条请求 , 
Server 收到后返回一些数据给 Client ,
Client 对数据进行解析和处理

## HttpURLConnection SOP
1. 实例化对象
```
URL url = new URL("http://www.iyounix.com");
HttpURLConnection connection = (HttpURLConnection) url.openConnection();
```

2. 设置 Http 请求所使用的方法
GET 希望从服务器获取数据
POST 希望提交数据给服务器
```
connection.setRequestMethod("GET");
connection.setRequestMethod("POST");
// 设置连接超时
connection.setConnectTimeout(8000);
// 设置读取超时
connection.setReadTimeout(8000);
```

3. 获取服务器返回的输入流 getInputStream()
```
InputStream in = connection.getInputStream();
```
获取到的输入流可以拿来 进行 各种骚操作.

example:
```
	InputStream in = connection.getInputStream();
    reader = new BufferedReader(new InputStreamReader(in));
    StringBuilder response = new StringBuilder();
    String line; //读到读完为止
    while ((line = reader.readLine()) != null) {
        response.append(line);
    }
    // Android 的子线程中是无法进行 UI 界面的刷新的
    // 通过调用 runOnUiThread 回到主线程进行 UI 的刷新
    showResponse(response.toString());
```

4. 提交数据给服务器 getOutputStream()
```
	connection.setRequestMethod("POST");
    DataOutputStream out = new DataOutputStream(connection.getOutputStream());
    out.writeBytes("username=admin & password=123456");
```

5. 关闭
```
connection.disconnect();
```

## WebView_OKHttp 基本介绍

Square 公司开发.
https://github.com/square/okhttp

## OKHttp SOP

### build.gradle
添加依赖
```
dependencies{
	implementation 'com.squareup.okhttp3:okhttp:3.4.1'
}
```

### MainActivity.java
```
// 1. 创建 OkHttpClient 实例 
	OKHttpClient client = new OkHttpClient();

// 2. 创建 Request 对象用来发送请求
	Request request = new Request.Builder().build();    
    // 可以通过连缀其他方法丰富 Request 对象
    Request request = new Request.Builder()
    					.url("http://www.iyounix.com")
                        .build();
                        
// 3.1 获取服务器返回的数据 GET
	Response response = client.newCall(request).execute();
	// 如下获取返回的具体的内容
    String reponseData = response.body().string();

// 3.2 向服务器发送请求  POST
	// 构建 RequestBody 对象存放待提交的参数
	RequestBody requestBody = new FormBody.Builder()
    							.add("username",  "admin")
                                .add("password",  "123456")
                                .build();
	// post()
    Request request = new Request.Builder()
    						.url("http://www.iyounix.com")
                            .post(requestBody)
                            .build();
	
    // execute() 请求并获取返回的数据
	Response response = client.newCall(request).execute();

```
