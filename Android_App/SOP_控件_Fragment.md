---
title: SOP_控件_Fragment
tags: android
grammar_cjkRuby: true
---

## Fragment 实例

```
    protected void onCreate(Bundle savedInstanceState) {
        ...
        // 1. 创建待添加 fragment 实例
        replaceFragment(fragment1);
        ...
    }

    private void replaceFragment(Fragment fragment) {
        // 2. 获取 FragmentManager
        FragmentManager fragmentManager = getSupportFragmentManager();
        // 3. 开启一个 事务 transaction
        FragmentTransaction transaction = fragmentManager.beginTransaction();
        // 4. 向容器内添加或者替换 fragment
        // 参数1 容器id     参数2 待添加fragment实例
        transaction.replace(R.id.right_layout, fragment);

        // 添加到返回栈
        // 参数为名字,用来描述返回栈的状态
        transaction.addToBackStack(null);

        // 5. 提交 事务 transaction
        transaction.commit();
    }

```

### 在 onClick 中使用
```
	RightFragment fragment1 = new RightFragment();
    AnotherRightFragment fragment2 = new AnotherRightFragment();

    @Override
    public void onClick(View v) {
        switch (v.getId()){
            case R.id.button1:
                replaceFragment(fragment1);
                break;
            case R.id.button2:
                replaceFragment(fragment2);
            default:
                break;
        }
    }
```

## Fragment 和 Activity 通信

### 在 Activity 中调用 fragment 的方法 findFragmentById
```
RightFragment rightFragment = (RightFragment) getFragmentManager().findFragmentById(R.id.right_fragment);
```

### 在  Fragment 中调用 Activity 的方法
```
MainActivity activity = (MainActivity)getActivity();
```


## Fragment 的生命周期

![Fragment 生命周期](https://ws1.sinaimg.cn/large/ba061518ly1ftf9x1v0grj208t0nj0ui.jpg)

