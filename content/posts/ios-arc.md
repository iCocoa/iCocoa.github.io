---
title: ARC
date: 2014-09-22 21:22:25+10:00
tags:
- iOS
- ARC
categories:
- iOS
- Tech
description: Example article description
sidebar: left
hiddenFromHomePage: false
---





## 什么是自动引用计数
自动引用计数（ARC，Automatic Reference Counting）是指内存管理中对引用采取自动计数的技术。要使用 ARC，需要满足以下条件：

* 使用 Xcode4.2 或以上版本
* 使用 LLVM 编译器 3.0 或以上版本
* 编译器选项中设置 ARC 有效
	
生活例子：办公室开关灯
	
1. 最早进入办公室的人开灯。 count = 1
2. 之后进入办公室的人，需要照明。 count = 2
3. 下班离开办公室的人，不需要照明。 count = 1
4. 最后离开办公室的人关灯。（此时已无人需要照明） count = 0
	 
## 内存管理
思考方式：

* 自己生成的对象，自己持有
* 非自己生成的对象，自己也能持有
* 不再需要自己持有的对象时释放
* 非自己持有的对象无法释放

表 1- 2 对象操作与 Objective-C 方法的对应

| 对象操作        | Objective-C方法| 
| ------------- | :-------------:| 
| 生成并持有对象  | alloc/new/copy/mutableCopy方法 | 
| 持有对象     	| retain方法      | 
| 释放对象 		| release方法     |
| 废弃对象 	 	| dealloc方法	  |


**区域(zone)**

`NSDefaultMallocZone`、`NSZoneMalloc` 等名称中包含的`NSZone`是什么呢？它是为防止内存碎片化而引入的结构。对内存分配的区域本身进行多重化管理，根据使用对象的目的、对象的大小分配内存，从而提高了内存管理的效率。但是，如同苹果官方文档 Programming With ARC Release Notes 中所说，现在的运行时系统只是简单地忽略了区域的概念。运行时系统中的内存管理本身已极具效率，使用区域来管理内存反而会引起内存使用效率低下以及源代码复杂化问题。

**修饰符**

* \_\_strong 修饰符
* \_\_weak 修饰符
* \_\_unsafe\_unretained 修饰符
* \_\_autoreleasing 修饰符

\_\_unsafe\_unretained 修饰符正如其名 unsafe 所示，是不安全的所有权修饰符。尽管 ARC 式的内存管理是编译器的工作，但附有 \_\_unsafe\_unretained 修饰符的变量不属于编译器的内存管理对象。同附有 \_\_weak 修饰符的变量一样，因为自己生成并持有的对象不能继续为自己所有，所以生成的对象会立即被释放。
		
为什么需要使用附有 \_\_unsafe\_unretained 修饰符？

在 iOS4 以及 OS X Snow Leopard 的应用程序中，必须使用 `__unsafe_unretained` 修饰符来替代 `__weak` 修饰符。赋值给附有 \_\_unsafe\_unretained 修饰符的对象在通过该变量使用时，如果没有确保其确实存在（可能已经被废弃，悬垂指针），那么应用程序可能会崩溃。
		
## ARC规则：
	
* 不能使用 retain/release/retainCount/autorelease
* 不能使用 NSAllocateObject/NSDeallocateObject
* 须遵守内存管理的方法命名规则
* 不要显式调用 dealloc
* 使用 @autoreleasepool 块替代 NSAutoreleasePool
* 不能使用区域（NSZone）
* 对象型变量不能作为 C 语言结构体（struct/union）的成员
* 显示转换“id”和“void *”

**对象型变量不能作为C语言结构体的成员**

`struct Data {
    NSMutableArray *array; 
}`
会引发编译错误。

虽然是 LLVM 编译器 3.0，但 C 语言的规约上没有方法来管理结构体成员的生存周期。因为 ARC 把内存管理的工作分配给编译器，所以编译器必须能够知道并管理对象的生存周期。例如 C 语言的自动变量（局部变量）是使用该变量的作用域管理对象。但是对于 C 语言的结构体成员来说，这在标准上就是不可实现的。要把对象型变量加入到结构体成员中时，可强制转换为 `void *` 或者是附加`__unsafe_unretained` 修饰符。
		
**显示转换“id”和“void \*”**

```
/* ARC无效 */
id obj = [[NSObject alloc] init];
void *p = obj;
id q = p;
	
/* ARC有效 */
id obj = [[NSObject alloc] init];
void *p = (__bridge void *)obj;
id q = (__bridge id)p;
```
		
ARC 有效时，通过 `__bridge` 转换，id 和 void \* 就能够相互转换。但是转换为 void \* 的 \_\_bridge 转换，其安全性与赋值给 \_\_unsafe\_unretained 修饰符相近，甚至会更低。如果管理时不注意赋值对象的所有者，就会因悬垂指针而导致程序崩溃。

\_\_bridge 转换中还有两种，分别是`__bridge_retained` 和`__bridge_transfer`。
\_\_bridge\_retained 转换可使要转换赋值的变量也持有所赋值的对象。
\_\_bridge\_transfer 转换提供相反的动作，被转换的变量所持有的对象在该变量被赋值给转换目标变量后随之释放。

这些转换多数发生在 Objective-C 对象与 Core Foundation 对象之间的相互变换中。 
		
## Objective-C 对象与 Core Foundation 对象 
		
Core Foundation 对象主要使用在用 C 语言编写的 Core Foundation 框架中，并使用引用计数的对象。在 ARC 无效时，Core Foundation 框架中的 retain/release 分别是 CFRetain/CFRelease。
		
Core Foundation 对象与 Objective-C 对象的区别很小，不同之处只在于是由哪一个框架（Core Foundation或者Foundation）所生成的。无论是由哪种框架生成的对象，一旦生成之后，便能在不同的框架中使用。Foundation 框架的 API 生成并持有的对象可以用 Core Foundation 框架的 API 释放。反之亦然。

因为二者区别不大，所以，在 ARC 无效时，只用简单的C语言的转换也能实现互换。另外这种转换不需要使用额外的 CPU 资源，因此也被称为“免费桥”（[Toll-free Bridge][Bridge]）。
		
[Bridge]:https://developer.apple.com/library/ios/documentation/CoreFoundation/Conceptual/CFDesignConcepts/Articles/tollFreeBridgedTypes.html