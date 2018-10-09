---
title: 数据持久化_数据库_LitePal 和 SQLite.md
tags: android
grammar_cjkRuby: true
---

## LitePal 基本概念
LitePal 是开源的 Android 数据库框架, 采用了 对象关系映射 ORM 模式 .
封装了常用数据库功能

> ORM(对象关系映射) 指的是 面向对象语言 和 关系型数据库 之间建立一种映射关系.

## 使用方法
### 配置

```app/build.gradle
dependencies {
	compile 'org.litepal.android:core:2.0.0'
}
```

```AndroidManifest.xml
android:name="org.litepal.LitePalApplication"
```

### litepal.xml
<litepal>
  <dbname value="BookStore"></dbname>
  <version value="1"></version>
  <list>
    <mapping class="com.example.litepaltest.Book"></mapping>
  </list>
</litepal>

```
Connector.getDatabase()
```

## SQLite 简介
SQLiteOpenHelper 抽象类
{
  onCreate()
  onUpgrade()
  
  getReadableDatabase() //以只读的方式打开db
  getWritableDatabase() //以可读写的方式打开db,如果db只读,则返回异常
  
  SQLiteOpenHelper() //构造方法
  // 参数1 Context 参数2 数据库名 参数3 查询数据的时候返回自定义的cursor(null) 参数4 当前数据库的版本号
}

文件保存在 `/data/data/<package name>/databases/` 目录下


## SQL 基本操作
### 建表 Create
```
create table Book (
	id integer primary key autoincrement, // primary key 将 id 设置为主键 // autoincrement 自增长
    author text, // 文本类型
    price real, // 浮点型
    pages integer, // 整型
    name text)
```
```
public class MyDatabaseHelper extends SQLiteOpenHelper {

    public static final String CREATE_BOOK = "create table Book ("
            +"id integer primary key autoincrement,"
            +"author text,"
            +"price real,"
            +"pages integer,"
            +"name text)";

    private Context mContext;

    public MyDatabaseHelper(Context context, String name,
                            SQLiteDatabase.CursorFactory factory,
                            int version) {
        super(context, name, factory, version);
        mContext = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(CREATE_BOOK);
        Toast.makeText(mContext, "Create succeeded", Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {

    }
}
```
实例化抽象类 MyDatabaseHelper
```
private MyDatabaseHelper dbHelper;
dbHelper = new MyDatabaseHelper(this, "BookStore.db",
                null, 1);
        Button createDatabase = findViewById(R.id.create_database);
        createDatabase.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                dbHelper.getWritableDatabase();
            }
        });
```

### 删表 Drop
```
        db.execSQL("drop table if exists Book");
        db.execSQL("drop table if exists Category");
```

### 升级 Update
第四个参数, 比之前大.
```
dbHelper = new MyDatabaseHelper(this, "BookStore.db",
                null, 2);
```

### 查表 
.table  //查表
.schema //查看建表语句
.exit .quit //退出


## 数据库操作 CRUD

### 添加数据 insert() 
insert() 
参数1 表名
参数2 未指定添加数据的情况下,给可为空的列自动赋值NULL. 不用就填null
参数3 ContentValues 对象, 提供了 put()方法的重载, 用于添加数据
```
               SQLiteDatabase db = dbHelper.getWritableDatabase();
                ContentValues values = new ContentValues();
                // 开始组装第一条数据
                values.put("name", "The Da Vinci Code");
                values.put("author", "Dan Brown");
                values.put("pages", 454);
                values.put("price", 16.94);
                // 插入第一条数据
                db.insert("Book", null, values);
                values.clear();
```

### 修改数据 update()
update()
参数1 表名
参数2 ContentValues 对象, 提供了 put()方法的重载, 用于添加数据
参数3 4 约束更新某一行或几行 , 默认是更新全部 ; 参数3 对应 where 语句
```
                SQLiteDatabase db = dbHelper.getWritableDatabase();
                ContentValues values = new ContentValues();
                values.put("price", 10.99);
                db.update("Book", values,
                        "name = ?", new String[] {"The Da Vinci Code"});
```

### 删除数据 deleted()
delete()
参数 1 表名
参数 2 3 whereClause 查询语句 , 比如 pages > ? , new Sting[] {"500"}
```
              SQLiteDatabase db = dbHelper.getWritableDatabase();
              db.delete("Book", "pages > ?",
                      new String[] {"500"});
```

### 查询数据 query()
query()
参数 1 table 表名 , from table_name
参数 2 columns 查询哪几列 , select column1,column2
参数 3 selection 4 selectionArgs 约束条件  where column = value 
参数 5 groupBy 的列 , group by column 
参数 6 having , group by 的约束 , having column = value
参数 7 orderBy , 指定查询的排列方式 , order by column1 column2
返回 Cursor 对象
```
                SQLiteDatabase db = dbHelper.getWritableDatabase();
                Cursor cursor = db.query("Book", null,null,null,null,null,null);
                if(cursor.moveToFirst()){
                    do {
                        //遍历 Cursor 对象, 取出数据并打印
                        String name = cursor.getString(cursor.getColumnIndex("name"));
                        String author = cursor.getString(cursor.getColumnIndex("author"));
                        int pages = cursor.getInt(cursor.getColumnIndex("pages"));
                        double price = cursor.getDouble(cursor.getColumnIndex("price"));
                        Log.d(TAG,"book name is " + name);
                        Log.d(TAG,"book author is " + author);
                        Log.d(TAG,"book pages is " + pages);
                        Log.d(TAG,"book price is " + price);
                    } while(cursor.moveToNext());
                }
                cursor.close();
```
### 直接使用 SQL 操作数据
execSQL 和 rawQuery

```
# 增
db.execSQL("insert into Book (name, author, pages, price) values(?, ?, ?, ?)", 
			new String[] {"The Da Vinci Code", "Dan Brown", "454", "16.96"});
# 删
db.execSQL("delete from Book where pages > ?", new String[] {"500"});
# 改
db.execSQL("update Book set price = ? where name = ?", new String[] {"10.99", "The Da Vinci Code"});
# 查
db.rawQuery("select * from Book" , null);
```

