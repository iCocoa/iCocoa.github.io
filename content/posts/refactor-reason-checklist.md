---
title: 重构的理由核对表
date: 2016-12-31 20:15:32+10:00
tags:
- Refactor
categories:
- Tech
- Refactor
description: Example article description
sidebar: left
hiddenFromHomePage: false
---
### 核对表：重构的理由
```
口 代码重复。
口 子程序太长。
口 循环太长或者嵌套太深。
口 类的内聚性太差。
口 类的接口的抽象层次不一致。
口 参数表中参数太多。
口 类的内部修改往往局限于某个部分。
口 需要对多个类进行并行修改。
口 对继承体系的并行修改。
口 需要对多个 case 语句进行并行修改。
口 相关的数据项只是被放在一起，没有组织到类中。
口 成员函数更多地使用了其他类的功能，而非自身类的。
口 过于依赖基本数据类型。
口 一个类不做什么事。
口 一连串传递流浪数据的子程序。
口 中间人对象什么也不干。
口 某个类同其他类关系过于密切。
口 子程序的命名太差。
口 数据成员被设置为公用。
口 派生类仅仅使用了基类的一小部分成员函数。
口 用注释来掩饰拙劣的代码。
口 使用了全局变量。
口 在子程序调用前使用设置代码，调用后使用收尾代码。
口 程序包含的某些代码似乎在将来某个时候才会被用到。
```