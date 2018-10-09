---
title: SOP_异步消息处理机制
tags: android
grammar_cjkRuby: true
---


## 基本概念
1. Message 
线程之间传递的载体
`.what` `.arg1` `.arg2`  字段可以携带整型数据

2. Handler
用于发送和处理 Message
Handler.sendMessage()
Handler.handleMessage()

3. MessageQueue
存放所有通过 Handler 发送的消息, 等待被处理
每个线程只会有一个 MessageQueue

4. Looper
Looper 是每个线程 MessageQueue 的管家.
Looper.loop() 后, 会进入循环, 当发现 MessageQueue 中存在消息, 就会取出, 并传递到 Handler.handleMessage 中.
每个线程也只会有一个 Looper 对象.

## 流程
1. 主线程创建 Handler 对象, 重写 handle Message() 方法
2. 子线程中要操作 UI 时, 创建 Message 对象, 并通过 Handler 发送 Message 即可
3. Message 会被添加到 MessageQueue 
4. Looper 会一直尝试从 MessageQueue 中取出 Msg, 最后分发到 handleMessage() 中


## AsyncTask 基本概念
AsyncTask 为抽象类, 需要继承 并 指定三个泛形参数
泛形参数:
1.`Params` 在执行 AsyncTask 传入的参数, 用于后台任务中使用
2.`Progress` 后台任务执行时, 如果需要在界面上显示当前进度, 这里的泛形为进度单位
3.`Result` 任务执行完毕后, 对结果进行返回, 这里的泛形为返回类型
```
class DownloadTask extends AsyncTask<Void, Integer, Boolean> {
	...
}
// Void 不需要参数给后台
// Integer 用整型作进度单位
// Boolean 作为返回值
```

重写 4 个方法:
1. onPreExecute()
在后台任务执行前开始调用,
完成界面初始化

2. doInBackground(Params...)
这里处理所有耗时内容, 将会运行在子线程中.
所以不可执行任何 UI 操作, 可以调用 publishProgress 方法进行 UI 更新

3. onProgressUpdate(Progress...)
当调用了 publishProgress 后, 调用本方法, 其中携带的参数就是后台任务中传递过来的
可以在此进行 UI 更新

4. onPostExecute(Result)
后台执行完毕 通过 return 返回时, 此方法被调用.
`Result` 作为参数传递到此方法, 一般用其进行 UI 操作.

## AsyncTask 实例
```
class DownloadTask extends AsyncTask<Void, Integer, Boolean> {
	
    protected void onPreExecute() {
    	progressDialog.show(); //显示进度对话框
    }
    
    protected Boolean doInBackground(Void... params) {
        while(true){
        	int downloadPercent = doDownload(); //虚构的方法 //有嗯与计算当前下载进度并返回
        	publishProgress(downloadPercent);
            if (downloadPercent >= 100) {
            	break;
            }
        }
        return true;
    }
    
    protected void onProgressUpdate(Integer... values) {
    	//更新下载进度
        progressDialog.setMessage("Downloaded" + values[0] + "%");
    }
    
    protected void onPostExecute(Boolean result) {
    	progressDialog.dismiss(); // 关闭进度对话框
        // 在这里提示下载结果
        if (result) {
        	Toast.makeText(context, "Download succeeded", Toast.LENGTH_SHORT).show();
        } else {
        	Toast.makeText(context, "Download Failed", Toast.LENGTH_SHORT).show();
        }
    }
}
```


## Handler 实例
### 子线程
```
    public static final int UPDATE_TEXT = 1;

    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.change_text:
                new Thread(new Runnable() {
                    @Override
                    public void run() {
//                        不能直接在子线程中操作 UI
//                        text.setText("Nice to meet you");
                        Message message = new Message();
                        message.what = UPDATE_TEXT;
                        handler.sendMessage(message);
                        Log.d(TAG, "onClick run() handler sendMessage");
                    }
                }).start();
                break;
            default:
                break;
        }
    }
```
### 主线程
```
    private Handler handler = new Handler() { //创建 Handler 对象

        // 重写父类 handleMessage 方法
        // 接收到子线程发送的 sendMessage 后调用 handleMessage 进行处理
        public void handleMessage(Message msg) {
            Log.d(TAG, "handlerMessage: Got Message");
            switch(msg.what) {
                case UPDATE_TEXT:
                    // 进行 UI 操作
                    text.setText("Nice To Meet You!");
                    Log.d(TAG, "handlerMessage: Got Message: UI Update");
                    break;
                default:
                    break;
            }
        }
    };
```