---
title: 组件_ContentProvider.md
tags: android
grammar_cjkRuby: true
---


## 基本概念
用法两种:
1. 使用现有的ContentProvider来读取和操作相应程序中的数据
2. 创建自己的内容提供器给我们的程序的数据提供外部访问接口

## ContentResolver 使用方法 

ContentResolver resolver = Context.getContentResolver();
resolver.insert //增
resolver.delete //删
resolver.update //改
resolver.query  //查

参数为 内容URI :
`content://com.example.app.provider/table1`
不过得先解析为 URI 对象:
`Uri uri = Uri.parse("content://com.example.app.provider/table1")`

使用 内容URI 查询 table1 的内容:
```
Cursor cursor = getContentResolver().query(
	uri,
    projection,		//指定列名
    selection,		//Where约束
    selectionArgs,	//Where占位符提供具体的值
    sortOrder		//指定查询结果的排序方式
);
```

通过移动游标位置,遍历 Cursor:
```
if (cursor != null){
	while (cursor.moveToNext()) {
    	String column1 = cursor.getString(cursor.getColumnIndex("column1"));
        int column2 = cursor.getInt(cursor.getColumnIndex("column2"));
    }
    cursor.close();
}
```

## 操作实例
//增
```
ContentValues values = new ContentValues();
values.put("column1", "text");
values.put("column2", 1);
getContentResolver().insert(uri,values); // 增
```
//改
```
ContentValues values = new ContentValues();
values.put("column1", "");
getContentResolver().update(uri. values, "column1 = ? and column2 = ?" , new String[] {"text" , "1"}); //改
```
//删
```
getContentResolver().delete(uri, "column2 = ?", new String[] {"1"});
```


