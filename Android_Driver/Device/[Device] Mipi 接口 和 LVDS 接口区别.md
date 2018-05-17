---
title: [Device] Mipi 接口 和 LVDS 接口区别
tags: MIPI,LVDS,DSI
grammar_cjkRuby: true
---
http://bbs.elecfans.com/jishu_887561_1_1.html

主要区别：
1. LVDS接口只用于传输视频数据，MIPI DSI不仅能够传输视频数据，还能传输控制指令；
2. LVDS接口主要是将RGB TTL信号按照SPWG/JEIDA格式转换成LVDS信号进行传输，MIPI DSI接口则按照特定的握手顺序和指令规则传输屏幕控制所需的视频数据和控制数据。

液晶屏有RGB TTL、LVDS、MIPI DSI接口，这些接口区别于信号的类型（种类），也区别于信号内容。
RGB TTL接口信号类型是TTL电平，信号的内容是RGB666或者RGB888还有行场同步和时钟；
LVDS接口信号类型是LVDS信号（低电压差分对），信号的内容是RGB数据还有行场同步和时钟；
MIPI DSI接口信号类型是LVDS信号，信号的内容是视频流数据和控制指令。
