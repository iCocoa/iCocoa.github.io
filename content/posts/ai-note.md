---
title: AI 笔记
date: 2024-01-09 20:10:22+10:00
tags:
- AI
- ChatGPT
categories:
- AI
- Tech
description: Example article description
sidebar: left
hiddenFromHomePage: false
---

### 如何找落地场景

1. **从最熟悉的领域入手**
2. **让 AI 学习最厉害员工的能力，再让 ta 辅助其他员工，实现降本增效**
3. **找 【文本进，文本出】的场景**
4. **别求大而全。将任务拆解，先解决小任务、小场景（小切口、大纵深）**

### 通俗原理

通过上文，猜测下一个词出现的概率。

1. **大模型阅读了大量人类说过的所有话（训练），就是机器学习**
2. **把一串 token 后面跟着的不同 token 的概率存入神经网络，保存的数据就是参数，也叫权重**
3. **当我们给它若干 token，大模型就能算出概率最高的下一个 token 是什么。这就是生成，也叫推理**
4. **用生成的 token，再加上上文，就能继续生成下一个 token。以此类推，生成更多文字**

### 如何用好 AI？

数字神经网络和人脑的生物神经网络，在数学原理上是一样的。 ——OpenAI 首席科学家 Ilya Sutskever

所以，把 AI 当人看！！！和人怎么相处就和 AI 怎么相处。

### 使用 AI 的几种模式

- **Embedding AI**（少）
- **AI Copilot**（协助）
- **AI Agent**（代理）

从上往下，AI 参与处理的任务越多。

### AI 相关的编程基本是 Python 语言。

#### 安装 OpenAI

```bash
pip3 install --upgrade openai
```

### 大模型里面的角色

- **System Role**：主要是定义系统的行为规范和全局设置。
- **Assistant Role**：主要负责与用户的交互，根据用户的输入生成响应。

这两种角色在构建对话系统时是互补的，共同决定了系统的整体行为和用户体验。

### LangChain 里面的 LLM 模块和 ChatModel

- **LLM**：通常用于生成单个文本输出，适合一次性提示和响应的场景。
- **ChatModel**：专门用于处理对话，能够记住对话历史并生成连贯的回复，适合构建多轮对话系统。

### 框架对比

- **Llamaindex**：主要用于构建和管理向量数据库，特别适合文档检索和知识库管理。
- **Semantic Kernel**：专注于构建对话系统，支持多轮对话和上下文管理，适合构建复杂的对话应用。
- **LangChain**：全面的框架，支持链式处理和多种模型，适合构建多样化的语言模型应用。

### Replicate

Replicate 是一个云端 AI 模型运行平台，它允许用户通过云端 API 直接运行机器学习模型，非专业人士也能上手。

### AI Agent

AI Agent 是一个自主的实体，能够感知环境、作出决策并执行任务。AI Agent 通常会使用 Function Calling 来执行任务或操作（发送邮件、查询数据库、控制硬件设备等），函数调用是 AI Agent 实现其功能的重要手段、工具。


