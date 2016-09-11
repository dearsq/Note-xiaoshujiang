---
title: NFC 程序设计（NDEF 格式介绍）
tags: NFC
grammar_cjkRuby: true
---
**NDEF 文本格式**
第一个字节  描述数据状态
若干个字节  描述文本语言编码
剩余字节      表述文本数据
这些数据格式由 [NFC Forum 相关规范][1] 定义

  [1]: http://www.nfc-forum.org/specs/spec_dashboard
  
  ## NDEF 文本数据格式
   **NDEF 文本数据格式**

  |偏移量bytes|长度bytes|描述|
  | --- | --- | --- |
  |0|1|状态字节|
  |1|\<n\>|ISO/IANA语言编码,格式是 USASCII，由状态字节后6位决定|
  |\<n+1\>| \<m\>|文本数据，编码格式是 UTF-8,编码格式由状态字节的前三位决定|
  
  **状态字节码编码格式**
  |字节位（0是最低位）|含义|
  |--|--|
  |7|0：文本格式是UTF-8 <br> 1：文本格式是UTF-16|
  |6|必须设为0|
  |\<5:0\>|语言编码长度（占用的字节个数）|

获取标签数据用 NdefRecord.getPayload 方法完成。
在处理这些数据之前，判断一下 NdefRecord 对象中存储的是不是 NDEF 文本格式数据。
标准有两个：
1. TNF（类型名格式，Type Name Format）必须是 NdefRecord.TNF_WELL_KNOWN
2. 可变的长度类型必须是 NdefRecord.RTD_TEXT













