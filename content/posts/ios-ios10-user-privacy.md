---
title: iOS 10 需要在 info.plist 中添加权限设置
date: 2016-10-07 22:35:29+10:00
tags:
- iOS
- Privacy
categories:
- iOS
- Tech
description: Example article description
sidebar: left
hiddenFromHomePage: false
---




iOS 10 开始对隐私权限更加严格, 如需使用隐私权限需要在工程的 `info.plist` 文件中声明,如果不声明程序在调用隐私权限（如相机）时应用程序会崩溃。

![infoPlist](https://res.cloudinary.com/dtbpgyfsc/image/upload/v1625297000/iOS/ios10-privacy-info-plist_damui3.png)

key 可以从下拉列表选择，value 为弹框提示文字（类型 String）

|	  权限名称      	    | 	Key 值 |
| :-------------:  |   :-------------:   | 
|通讯录|	NSContactsUsageDescription|
|麦克风	|NSMicrophoneUsageDescription|
|相册	|NSPhotoLibraryUsageDescription|
|相机	|NSCameraUsageDescription|
|持续获取地理位置	|NSLocationAlwaysUsageDescription|
|使用时获取地理位置	|NSLocationWhenInUseUsageDescription|
|蓝牙	|NSBluetoothPeripheralUsageDescription|
|语音转文字	|NSSpeechRecognitionUsageDescription|
|日历	|NSCalendarsUsageDescription|