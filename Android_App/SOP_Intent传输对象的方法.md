---
title: SOP_Intent传输对象的方法
tags: android
grammar_cjkRuby: true
---

## 正常的 Intent 传值的方法

```
Intent intent = new Intent(FirstActivity.this, SecondActivity.class);
intent.putExtra("string_data","hello");
intent.putExtra("int_data",100);
startActivity(intent);
```
在 SecondActivity 众通过 getIntent 获取值
```
getIntent().getStringExtra("string_data");
getIntent().getIntExtra("int_data",0);
```

## 传输对象的方法

### Serializable
比如有这样一个 class person
```
public class Person implements Serializable {
	private String name;
    private int age;
    public String getName() { return name; }
    public void setName() { this.name = name; }
    public int getAge() { return age; }
    public void setAge() { this.age = age; }
}
```
Serializable 用法
```
Person person = new Person();
... //初始化赋值
Intent intent = new Intent(FirstActivity.this, SecondActivity.class);
intent.putExtra("person_data", person);
startActivity(intent);
```
在 SecondActivity 众通过 getIntent 获取值
```
Person person = (Person) getIntent().getSerializableExtra("person_data");
```

### Parcelable
需要修改 class Person:
```java
//1. 首先实现 Parcelable 接口
public class Person implements Parcelable {
	private String name;
    private int age;
    public String getName() { return name; }
    public void setName() { this.name = name; }
    public int getAge() { return age; }
    public void setAge() { this.age = age; }
    
    //2.1 重写 describeContents 方法
    public int describeContents() { return 0;}
    //2.2 重写 writeToParcel 方法, 将 Person 中的字段一一写出
    public void writeToParcel(Parcel dest, int flags) {
    	dest.writeString(name); // 写出name
        dest.writeInt(age);		// 写出age
	}
    //3. 提供 CREATOR 常量
    // 创建 Parcelable.Creator 接口的一个实现, 并将泛型指定为 Person.
    public static final Parcelable.Creator<Person> CREATOR = new Parcelable.Creator<Person>(){
    	//4.1 重写 createFromParcel , 读取刚才写出的 name 和 age 字段
        // 注意! 顺序必须和写出顺序完全相同
    	public Person createFromParcel(Parcel source) {
        	Person person = new Person();
            person.name = source.readString(); //读取 name
            person.age = source.readInt();		//读取 age
            return person;
        }
        //4.2 重写 newArray
        public Person[] newArray(int size) {
        	return new Person[size];
        }
    };
```
Parcelable 用法完全一样:
```
Person person = new Person();
... //初始化赋值
Intent intent = new Intent(FirstActivity.this, SecondActivity.class);
intent.putExtra("person_data", person);
startActivity(intent);
```
在 SecondActivity 众通过 getIntent 获取值 , 有少许差别
```
Person person = (Person) getIntent().getParcelableExtra("person_data");
```
