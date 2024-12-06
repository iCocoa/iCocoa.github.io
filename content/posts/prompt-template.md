---
title: "Prompt 框架模版"
date: 2023-7-09T21:30:32+10:00
tags: ["Prompt","ChatGPT"]
categories: ["AI"]
---

### Crispe

[Matt Nigh](https://link.juejin.cn/?target=https%3A%2F%2Fgithub.com%2Fmattnigh%2FChatGPT3-Free-Prompt-List) 的 CRISPE Framework，比较适合用于编写 prompt 模板。CRISPE 分别代表以下含义：

CR: Capacity and Role（能力与角色）。你希望 ChatGPT 扮演怎样的角色。

I:Insight（洞察力），背景信息和上下文（坦率的说我觉得用Context 更好）。

S： Statement（指令），你希望 ChatGPT 做什么。

P：Personality（个性），你希望 ChatGPT 以什么风格或方式回答你。

E：Experiment（尝试），要求 ChatGPT 为你提供多个答案。

 以下是这几个参数的例子：

 | Step          | Example |       
|---------------|--------------|
| Capacity and Role | Act as an expert on software development on the topic of machine learning frameworks, and an expert blog writer. 把你想象成机器学习框架主题的软件开发专家，以及专业博客作者。 |
| Insight       | The audience for this blog is technical professionals who are interested in learning about the latest advancements in machine learning. 这个博客的读者主要是有兴趣了解机器学习最新进展技术的专业人士。 |
| Statement     | Provide a comprehensive overview of the most popular machine learning frameworks, including their strengths and weaknesses. Include real-life examples and case studies to illustrate how these frameworks have been successfully used in various industries. 提供最流行的机器学习框架的全面概述，包括它们的优点和缺点。包括现实生活中的例子，和研究案例，以说明这些框架如何在各个行业中成功地被使用。 |
| Personality   | When responding, use a mix of the writing styles of Andrej Karpathy, Francois Chollet, Jeremy Howard, and Yann LeCun. 在回应时，混合使用 Andrej Karpathy、Francois Chollet、Jeremy Howard 和 Yann LeCun 的写作风格。 |
| Experiment    | Give me multiple different examples. 给我多个不同的例子。|
 
 将所有的元素都组合在一起，就变成了这样的 prompt，对比基础 prompt 生成的结果会非常不一样。
 
### 图灵机式

Input: 给出执行指令需要上下文或其他信息。
Instruction: 指令。指示模型完成的任务， 处理方法或步骤。
Output： 输出。指示模型按你想要的格式输出。
filter: 过滤，可选项。




