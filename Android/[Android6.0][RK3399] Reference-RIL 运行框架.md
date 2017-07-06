---
title: [Android6.0][RK3399] Reference-RIL 运行框架
tags: rockchip,ril,rild,android,telephony
grammar_cjkRuby: true
---

Reference-RIL 
1. 负责将 Solicited Request 请求转换成 AT 命令交给 Modem 执行。
2. 将执行结果以 Solicited Response 消息方式反馈给 LibRIL。
3. 负责接受 Modem 主动上报的消息。

## Reference-RIL 运行机制
### 1. RIL_init 初始化
RIL_init 包括三个步骤：
1. 记录 LibRIL 提供的 RIL_Env 指针，通过它可以调用 LibRIL 提供的相应函数。
2. 启动基于 mainLoop 函数运行的子进程，mainLoop 主要负责监听和接受 Modem 主动上报的 UnSolicited 消息。
3. 返回 Reference-RIL 提供的指向 RIL_RadioFunctions 的指针 s_callbacks。

### 2. onRequest 接受 LibRIL 请求调用
通过查找 Reference-RIL 提供的 onRequest 函数 仅在 LibRIL 中被调用。
LibRIL 接收到了 RILJ 发起的 RIL 请求后，通过 onRequest 函数调用，向 Reference-RIL 发起对应的 RIL 请求。
它完成了两件事：
1. 将 RIL 请求转化成 AT 命令，并发送给 Modem
2. 调用 LibRIL 的 RIL_onRequestComplete 函数，完成 RIL 请求处理结果的返回。

## AT 命令
不同厂家的 AT 命令集不尽相同，我们这个案子采用的是 移远的 EC20。
这个另开一帖单独介绍。

## RIL 层运行框架和机制小结
RIL 层分为三个部分，RILJ、LibRIL 、Reference-RIL：
**RILJ** 以 RIL.java 代码为中心，负责接受 Telephony Frameworks 发起的 Telephony 相关查询或控制请求，转化成 RIL 请求发送给 LibRIL 进行处理。
负责接受 LibRIL 发出的 Solicited Response 和 UnSolicited Response 消息，并将消息分发给 Telephony Frameworks。
**LibRIL** 以 ril.cpp、ril_event.cpp 代码为中心，提供了 RILC 的 Runtime。
负责接受 RILJ 发起的 RIL 请求，将 RIL 请求转化为 Reference-RIL 提供的 onRequest 函数调用，并将 RIL 请求结果反馈给 RILJ。
同时，接受 Reference-RIL 发起的 Unsolicited 消息相关函数调用，并将 UnSolicited Response 消息发给 RILJ。
Reference-RIL 以 reference-ril.cpp 代码为中心，负责 Modem 进行 AT 命令的交互。
接受 LibRIL 的 onRequest 函数调用，根据 RIL 请求类型组合成 AT 命令，交给 Modem 执行; Modem 状态有任何变化发出 AT 命令，Reference-RIL 接受并执行，并且将 AT 命令转化为 UnSolicited 消息，发送给 LibRIL。