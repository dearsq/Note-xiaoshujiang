---
title: [Linux] likely() 和 unlikely()
tags: Linux
grammar_cjkRuby: true
---
[TOC]

Version: linux-2.6.32

## 定义
/include/linux/compiler.h
```
#define likely(x) __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)
```

```
//gcc 中提供的预处理命令，利于代码优化。
long __builtin_expect (long exp, long c) [Built-in Function]
```

## 注解
You may use \_\_builtin_expect to provide the compiler with branch prediction information. In general, you should prefer to use actual profile feedback for this (‘-fprofile-arcs’), as programmers are notoriously bad at predicting how their programs actually perform. However, there are applications in which this data is hard to collect.The return value is the value of exp, which should be an integral expression. The semantics of the built-in are that it is expected that exp == c.

**likely(exp, c)  表示  exp == c  是很可能发生的。
unlikely(exp, c) 表示 exp == c 是很可能不会发生的。**



## 用法
用在 if 后。
使用likely ，执行if后面语句的可能性大些，编译器将if{}是的内容编译到前面。
使用unlikely ，执行else后面语句的可能性大些,编译器将else{}里的内容编译到前面。
这样有利于cpu预取,提高预取指令的正确率,因而可提高效率。

## 实例
linux-2.6.32.67/arch/arm/lib/uaccess_with_memcpy.c
```
	pgd = pgd_offset(current->mm, addr);
	if (unlikely(pgd_none(*pgd) || pgd_bad(*pgd)))
		return 0;

```
编译过程中，会将if后面{}里的内容编译到前面。
若将likely换成unlikely 则正好相反。

总之,likely与unlikely互换或不用都不会影响程序的正确性。但可能会影响程序的效率。
```
if(likely(foo))  //认为foo通常为1
if(unlikely(foo)) //认为foo通常为0
```
