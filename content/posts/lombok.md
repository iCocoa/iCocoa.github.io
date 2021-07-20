---
title: "Lombok"
date: 2020-04-30T19:10:32+01:00
tags: ["Java","Tool","Plugin"]
categories: ["Java"]
---

## 介绍
`Lombok` 是提升 Java 编码效率常用的工具，借助它开发人员可以使用注解来自动生成一些模版代码。比如 `getter`、`setter`、`equals`、`toString` 等方法。

## 安装

### 在 maven 中添加依赖
```
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.4</version>
    <scope>provided</scope>
</dependency>
```

### 在编辑器中添加插件

如：Intellij Idea，在 setting 的 plugin 里搜索lombok plugin，安装插件

## 使用

**常用的几个注解**

@Data ：注在类上，自动生成类的 get、set、equals、hashCode、canEqual、toString 方法

@AllArgsConstructor ：注在类上，自动生成类的全参构造方法

@NoArgsConstructor ：注在类上，自动生成类的无参构造

@Setter ：注在属性上，自动生成 set 方法

@Getter ：注在属性上，自动生成 get 方法

@EqualsAndHashCode ：注在类上，自动生成对应的 equals 和 hashCode 方法

@Log4j/@Slf4j ：注在类上，自动生成对应的 Logger 对象，变量名为 log

@Cleanup("close")：注在本地变量上，自动释放资源（如：关闭 InputStream）

@Synchronized：注在方法上，自动生成一个私有锁变量

@SneakyThrows：自动生成异常处理语句

> **注意继承关系中使用 Lombok** `@EqualsAndHashCode` 与 `@ToString` 注解默认情况下忽略父类的成员变量。譬如打印时 `toString` 返回的结果中缺少父类的成员变量，解决办法是在注解中设置 `callSuper` 属性为 `true`， `@ToString(callSuper = true)` 、`@EqualsAndHashCode(callsuper = true)`。

## 实现原理
jdk 6 中提出并通过了 JSR-269 提案，该提案设计了一组被称为“插入式注解处理器”的标准 API，可以提前至编译期对代码中的特定注解进行处理，从而影响到前端编译器的工作过程（jdk 6 之前，注解只会在运行期发挥作用）。插入式注解处理器工作时，允许读取、修改、添加抽象语法树中的任意元素。如果在处理注解期间修改了语法树，编译器将回到解析及填充符号表的过程重新处理，直到所有插入式注解处理器都没有再对语法树进行修改为止。Lombok 正是依赖插入式注解处理器来实现的，通过修改注解所在类的语法树来增加节点，引发编译器重新处理，完成修改。

## 总结

通过使用 Lombok 可以让代码更简洁，减少了修改属性所需的维护工作量，提升了开发效率，但却降低了可读性和完整性。笔者觉得可以放心在项目使用 Lombok，因为当你后悔作出这个决策时，使用 delombok 这个工具可以帮你还原。

参考：

[lombok](https://projectlombok.org)

[bealdumg introduction to lombok](https://www.baeldung.com/intro-to-project-lombok)

《深入理解 Java 虚拟机》