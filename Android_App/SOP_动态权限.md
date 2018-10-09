---
title: SOP_动态权限
tags: android
grammar_cjkRuby: true
---

在程序运行的过程中由用户去授权执行某些可能是危险的的操作.

## 实现步骤
1. 检查权限
ContextCompat.checkSelfPermission
参数 1 Context
参数 2 具体的权限名字
```
ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CALL_PHONE)

判断有无权限:
ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CALL_PHONE) 
 		!= PackageManager.PERMISSION_GRANTED
```

2. 申请权限
ActivityCompat.requestPermissions
参数 1 Context
参数 2 权限名
参数 3 自定义权限码
```
ActivityCompat.requestPermissions(MainActivity.this, new String[]{ Manifest.permission.CALL_PHONE }, 1)
```
之后系统会弹出权限申请对话框, 再调用 onRequestPermissionResult .
授权结果会封装在 grantResults 参数中

3. 回调 
onRequestPermissionResult
```
    public void onRequestPermissionsResult ( int requestCode, String[] permissions , int[] grantResults) {
        switch (requestCode) {
            case 1:
                if(grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    call();
                } else {
                    Toast.makeText(this, "You denied the permission" , Toast.LENGTH_SHORT).show();
                }
                break;
            default:
        }
    }
```