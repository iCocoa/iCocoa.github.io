---
title: 数据库的动态列
date: 2023-07-25 20:17:32+10:00
tags:
- DB
- Dynamic
- Mariadb
- MySQL
categories:
- DB
- Tech
description: Example article description
sidebar: left
hiddenFromHomePage: false
---




# 动态列的几种设计思路

在需求开发过程中，我们有时会遇到一种场景：某个具体业务中的属性是动态的。在理想情况下，我们可以使用穷举法对所有可能的属性进行分析，然后进行分类，最终形成一套解决方案。然而，现实往往是骨感的，Leader和客户通常不会给我们这个时间。因此，我们需要探讨一些更为实际的解决方案。

## 一、使用数据库DDL进行动态创建

**优点：**
1. 操作简单，只需通过SQL管理即可实现。

**缺点：**
1. 不同情况下的动态字段增加会导致表结构膨胀。
2. 在已有数据的表中修改字段容易导致锁表，影响性能。

## 二、使用数据库预留字段

**优点：**
1. 与数据库无关，对业务侵入性小。

**缺点：**
1. 扩展性差，超出预留字段范围后如何处理新字段？
2. 可读性差，预留字段通常为`attr1`、`attr2`等，影响字段的可读性。
3. 性能较低，为兼容多种数据类型，预留字段通常采用较长的文本数据类型存储，影响数据库性能。

## 三、使用数据库中的JSON数据类型

**优点：**
1. 使用简单，绝大多数编程语言都支持JSON操作，方便快捷。
2. 对于MySQL或PostgreSQL等数据库，已原生支持JSON字段，可基于JSON进行扩展查询。
3. JSON采用`key:value`形式存储数据，可避免字段可读性差的问题，通过规范命名提高可读性。
4. 扩展性高，增加或删除字段实现简单，直接移除`key`即可，不影响表性能。

**缺点：**
1. JSON字段查询操作与普通字段稍有差异，有一定复杂度。
2. JSON字段的索引性能有待提高。

## 四、使用NoSQL数据库

**优点：**
1. 采用MongoDB等JSON数据库，可以快速扩展。
2. 专业数据存储，查询等性能可针对优化，性能高。

**缺点：**
1. 需要一定的学习成本。

综上所述，第一种和第二种方案若非必要，不建议采用。第三种方案在中小项目中能应对绝大多数需求。如果存储的数据较多且性能要求较高，可以考虑采用第四种方案或第三、四种方案相结合。

---

# 支持动态列的数据库

## MariaDB

通过创建BLOB列（最大64k？），可以使用`mariadb-dynamic-columns`实现动态列。

### 示例：

```sql
CREATE TABLE items
(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name varchar(100) NOT NULL,
    attributes BLOB
);
```

1. **插入数据时使用特定函数（`COLUMN_CREATE`）指定动态列的数据结构，`key/value`形式：**

```sql
INSERT INTO items (name, attributes) VALUES
('MariaDB t-shirt', COLUMN_CREATE('colour','blue', 'size','XXL')),
('MariaDB t-shirt', COLUMN_CREATE('colour','blue', 'size','XL')),
('Samsung Galaxy S5', COLUMN_CREATE('colour','white', 'OS', 'Android', 'type', 'phone')),
('Samsung Galaxy Pro 3', COLUMN_CREATE('colour','white', 'size',8, 'OS', 'Android', 'resolution','1920x1200', 'type','tablet'));
```

2. **查询时使用`COLUMN_JSON`函数，返回JSON格式的数据：**

```sql
SELECT name AS Item,
COLUMN_JSON(attributes) AS 'Dynamic Columns'
FROM items LIMIT 1;
```

3. **使用`COLUMN_LIST`函数列举列中包含的属性，如`colour`、`size`：**

```sql
SELECT name AS Item,
COLUMN_LIST(attributes) AS 'Attribute Names'
FROM items;
```

4. **查询动态列中具体的某个属性，如`colour`：**

```sql
SELECT name AS Item,
COLUMN_GET(attributes, 'colour' AS CHAR) AS Colour
FROM items;
```

## PostgreSQL

支持JSON数据类型，相比普通`text`文本字段类型，JSON数据类型强制要求列中每个存储的值都符合JSON格式规则。

PostgreSQL提供了两种存储JSON数据的类型：`json`和`jsonb`。为了实现对这些数据类型的高效查询机制，PostgreSQL还提供了`jsonpath`数据类型（详见第8.14.7节）。

`json`和`jsonb`数据类型接受的输入值几乎相同，主要区别在于效率。`json`数据类型存储输入文本的精确副本，处理函数每次执行时都必须重新解析；而`jsonb`数据以分解的二进制格式存储，输入时由于转换开销稍慢，但处理速度显著更快，因为无需重新解析。此外，`jsonb`还支持索引，这是一个显著优势。

由于`json`类型存储输入文本的精确副本，它会保留语义上不重要的空白字符和JSON对象中键的顺序。如果JSON对象中的键重复，所有键值对都会被保留（处理函数认为最后一个值是有效的）。相比之下，`jsonb`不保留空白字符，不保留对象键的顺序，也不保留重复的对象键。如果输入中指定了重复键，只有最后一个值会被保留。


