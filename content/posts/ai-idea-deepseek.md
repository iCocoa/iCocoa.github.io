---
title: IntelliJ IDEA 集成 DeepSeek 辅助编程
date: 2025-02-05 21:53:32+10:00
tags:
- Tool
categories:
- Tech
- AI
description: Example article description
sidebar: left
hiddenFromHomePage: false
---

在人工智能辅助编程工具日益普及的今天，DeepSeek 以其卓越的性能和实惠的价格在开发者社区中迅速走红。作为一名从 DeepSeek v1 就开始使用的资深用户，我见证了它在代码生成、问题解答和开发建议等方面的持续进步。当时为什么选择用它？一方面，与 ChatGPT 相比，DeepSeek 不仅提供了更具竞争力的 API 定价策略，其网页版对话应用更是完全免费。另一方面，经过与国内其他同类产品的深入对比测试，我发现 DeepSeek 的回复更加简洁精准，特别适合技术场景下的使用需求。

随着 DeepSeek-R1 版本的发布，其性能指标在多个基准测试中均表现出显著优势。本文将详细介绍如何将这一强大的 AI 模型集成到 IntelliJ IDEA 中，为您的开发工作流程注入新的活力。

### 环境准备
在开始集成之前，请确保您的开发环境满足以下要求：
- IntelliJ IDEA 2023 或更高版本
（注：较早版本的 IDEA 可能无法完全支持 codeGPT 插件的 UI 显示）

下载地址：[IntelliJ IDEA 官方下载页面](https://www.jetbrains.com/idea/download/?section=mac)

### 安装 codeGPT 插件
codeGPT 是一个功能强大的插件，它充当了 IDE 与 AI 模型之间的桥梁。通过它，开发者可以直接在 IDE 中调用 DeepSeek 的服务。

安装步骤：
1. 打开 IntelliJ IDEA
2. 进入插件市场（File -> Settings -> Plugins）
3. 搜索 "codeGPT" 并安装
4. 重启 IDE 完成安装

![codeGPT 安装示意图](/images/ai-idea-deepseek/install-codegpt.png)

### 获取 DeepSeek API 密钥
1. 访问 DeepSeek 开发者平台：[https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 注册/登录您的账户
3. 在控制台生成新的 API 密钥
（注意：请妥善保管您的 API 密钥，避免泄露）

![API 密钥获取示意图](/images/ai-idea-deepseek/deepseek-api-key.png)

### 配置 codeGPT 使用 DeepSeek
1. 在 IDEA 中打开 codeGPT 设置面板（File -> Settings -> Tools -> codeGPT）
2. 输入您获取的 DeepSeek API 密钥
![API 密钥配置示意图](/images/ai-idea-deepseek/config-api-key.png)
4. 配置对话模型参数
![模型配置示意图](/images/ai-idea-deepseek/config-chat-model.png)
5. 设置推理模型参数
![推理模型配置示意图](/images/ai-idea-deepseek/config-reasoning-model.png)
6. 保存配置


### 使用指南
1. 在 IDEA 工具栏中定位 codeGPT 图标
2. 点击图标打开交互面板
3. 在模型选择器中指定 "Custom:OpenAI"
4. 输入您的技术问题或代码片段
5. 点击 "Send" 获取 AI 建议

![使用示例示意图](/images/ai-idea-deepseek/use-case.png)

（注意：使用过程中产生的 API 调用将会产生相应费用，建议定期在 DeepSeek 控制台查看使用情况和费用明细）

通过以上步骤，您已经成功将 DeepSeek 集成到 IntelliJ IDEA 中。这一集成不仅能够帮助您快速解决编码难题，还能在代码优化、错误调试等方面提供专业建议。随着 AI 辅助编程工具的不断发展，我们期待看到更多开发者能够利用这些先进技术提升工作效率，创造更多价值。