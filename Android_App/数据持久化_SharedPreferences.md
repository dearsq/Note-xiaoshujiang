---
title: 数据持久化_SharedPreferences
tags: android
grammar_cjkRuby: true
---

## 简介
通过键值对的方式进行存储. 保存为 xml 文件
value - key

## 存储
1. 获取 SharedPreferences 对象
  SharedPreferences.Editor editor = getSharedPreferences("data", MODE_PRIVATE).edit();
2. editor.putString("name", "Tom");
3. editor.apply();
```
// 通过 getSharedPreferences() 方法指定 SharedPreferences 文件名为 data
SharedPreferences.Editor editor = getSharedPreferences("data", MODE_PRIVATE).edit();
editor.putString("name", "Tom");
editor.putInt("age", 28);
editor.putBoolean("married",false);
editor.apply();
```

### 获取 SharedPreferences 对象的三种方法
1. Context 类的 getSharedPreferences():  getSharedPreferences("data", MODE_PRIVATE);
2. Activity 类的 getPreferences():  getPreferences(MODE_PRIVATE);
3. PreferenceManager 类的 getDefaultSharedPreferences(): PreferenceManager.getDefaultSharedPreferences(Context);

## 读取
```
SharedPreferences pref = getSharedPreferences("data", MODE_PRIVATE);
//SharedPreferences pref2 = getPreferences(MODE_PRIVATE);
//SharedPreferences pref3 = new PreferenceManager.getDefaultSharedPreferences(Context);
String name = pref.getString("name", "NOBODY");
int age = pref.getInt("age",0);
boolean married = pref.getBoolean("married", false);
```