---
title: [Android6.0][RK3399] 去掉顶部Google搜索栏
tags: QuickSearchBox,Android
grammar_cjkRuby: true
---

OS： Android6.0 
Hardware：RK3399
 
 
 ## 修改方法
 搜索资料了解到，其为 QuickSearchBox。
 代码在 packages/apps 中
 
测试了很多网上的修改 launcher3 源码的方式，都是不行的。

正确改法： 
在` build/target/product/core.mk` 去掉 QuickSearchBox 

 ![](http://ww1.sinaimg.cn/large/ba061518ly1fni9w416sjj20gi08jq54.jpg)
 
 