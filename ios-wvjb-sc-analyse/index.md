# WebViewJavascriptBridge 源码剖析


**WebViewJavascriptBridge** 是一个可以让 OC 与 JS 进行交互通信的第三方开源库。相比其他热门的第三方库，WebViewJavascriptBridge 代码量比较少，并且设计优雅巧妙，可以说是 “小而美”。

WebViewJavascriptBridge 库在 OC 端和 JS 端都有对等的逻辑实现，事先注册 handler，内部维护一个消息队列。透明的 `iframe` HTML 元素和 webview 的 `stringByEvaluatingJavaScriptFromString` 是通信的关键。OC 端发消息给 JS 端比较直观，调起 `stringByEvaluatingJavaScriptFromString` 执行脚本传入消息即可。JS 端发消息给 OC 端，需要事先把消息存到队列中，然后借助 iframe 发起一个伪请求，伪请求会被 webview 的代理方法拦截下来，OC 端因此得知 JS 端消息队列中有消息，最后调起 `stringByEvaluatingJavaScriptFromString` 方法解析 JS 方法拿到队列中的消息并处理。交互流程见下图：

![wbjb-sc-analyse-001](https://res.cloudinary.com/dtbpgyfsc/image/upload/v1625297150/web/webviewjsbridge_z8kdpc.jpg)

整个库只有以下几个文件：

```
WebViewJavascriptBridge.h
WebViewJavascriptBridge.m
WKWebViewJavascriptBridge.h 
WKWebViewJavascriptBridge.m
WebViewJavascriptBridgeBase.h
WebViewJavascriptBridgeBase.m
WebViewJavascriptBridge_JS.h
WebViewJavascriptBridge_JS.m
```

一般使用只需要关注 `WebViewJavascriptBridge` 类提供的接口，这个类的主要职责是用来做 Mac 和 iOS webview 的适配（包括 WKWebView，但是这部分代理出去给 WKWebViewJavaScriptBridge 类）并为客户端提供便利的使用接口。`WebViewJavascriptBridgeBase` 类负责有关数据加工、消息队列管理、消息派发及回调的处理工作。`WebViewJavascriptBridge_JS` 类包含 JS 端的实现代码，通过宏处理返回 JS 端实现代码的一个 OC 字符串，便于在适当时机将其注入到文档模型中完成 bridge 的初始化。

# WebViewJavascriptBridge 类

下面这个方法用来注册 handler，以响应 JS 的调用。handler 会被缓存到 \_base 的 map 中，以供后续调用。

```
- (void)registerHandler:(NSString*)handlerName handler:(WVJBHandler)handler;
```

下面这个方法用来调用 JS 对应的方法，responseCallback 会被缓存到 \_base 的 map 中，以供后续调用。

```
- (void)callHandler:(NSString*)handlerName data:(id)data responseCallback:(WVJBResponseCallback)responseCallback;
```

对 iframe 所发出的伪请求的拦截在此代理方法中进行

```
- (BOOL)webView:(UIWebView *)webView shouldStartLoadWithRequest:(NSURLRequest *)request navigationType:(UIWebViewNavigationType)navigationType {
    if (webView != _webView) { return YES; }
    
    NSURL *url = [request URL];
    __strong WVJB_WEBVIEW_DELEGATE_TYPE* strongDelegate = _webViewDelegate;
    if ([_base isWebViewJavascriptBridgeURL:url]) {
        if ([_base isBridgeLoadedURL:url]) {
            [_base injectJavascriptFile];
        } else if ([_base isQueueMessageURL:url]) {
            NSString *messageQueueString = [self _evaluateJavascript:[_base webViewJavascriptFetchQueyCommand]];
            [_base flushMessageQueue:messageQueueString];
        } else {
            [_base logUnkownMessage:url];
        }
        return NO;
    } else if (strongDelegate && [strongDelegate respondsToSelector:@selector(webView:shouldStartLoadWithRequest:navigationType:)]) {
        return [strongDelegate webView:webView shouldStartLoadWithRequest:request navigationType:navigationType];
    } else {
        return YES;
    }
}
```

`[_base isBridgeLoadedURL:url]` 结果为 true 时表示正在加载 bridge，此时可以注入 JS 端实现代码到文档模型中，判断依据为 *__bridge_loaded__* 主机名。由 iframe 发起的伪请求 `WVJBIframe.src = 'https://__bridge_loaded__';` 触发。

`[_base isQueueMessageURL:url]` 结果为 true 时表示 JS 消息队列中有消息需要处理，判断依据为 *__wvjb_queue_message__* 主机名。由 iframe 发起的伪请求 `messagingIframe.src = 'https://__wvjb_queue_message__';` 触发。

从这里也可以看出，很多 api 的请求都转发给`WebViewJavascriptBridgeBase` 类型的实例变量 `_base`。

# WebViewJavascriptBridgeBase 类

WebViewJavascriptBridgeBase 类中维护一个 handler map 和一个 callback map，用来响应 JS 的调用。内部有一些序列化以及反序列化的私有方法。

OC 端使用下面这个方法往 JS 端发消息。

```
- (void)_dispatchMessage:(WVJBMessage*)message {
    NSString *messageJSON = [self _serializeMessage:message pretty:NO];
    messageJSON = [messageJSON stringByReplacingOccurrencesOfString:@"\\" withString:@"\\\\"];
    ...
    NSString* javascriptCommand = [NSString stringWithFormat:@"WebViewJavascriptBridge._handleMessageFromObjC('%@');", messageJSON];
    if ([[NSThread currentThread] isMainThread]) {
        [self _evaluateJavascript:javascriptCommand];
    } else {
        dispatch_sync(dispatch_get_main_queue(), ^{
            [self _evaluateJavascript:javascriptCommand];
        });
    }
}
```

消息的结构为：

```
{	
	"data" : data,
	"callbackId" : objc_cb_xxx, //xxx 为数字，JS 端的 callbackId 会拼接上时间
	"handlerName" : handlerName,
	"responseId" : objc_cb_xxx 
}
```

在拦截中获知正在加载 bridge 后，下面这个方法把 JS 代码注入到文档模型中，初始化 bridge。在网页没加载之前，也就是 bridge 没建立之前，可能 OC 端会发送消息，这些消息需要缓存在 `startupMessageQueue` 中，在建立 bridge 之后，这个 queue 就没用了。

```
- (void)injectJavascriptFile {
    NSString *js = WebViewJavascriptBridge_js();
    [self _evaluateJavascript:js];
    if (self.startupMessageQueue) {
        NSArray* queue = self.startupMessageQueue;
        self.startupMessageQueue = nil;
        for (id queuedMessage in queue) {
            [self _dispatchMessage:queuedMessage];
        }
    }
}
```

在拦截中获知 JS 消息队列中有消息需要处理后，拉取消息会用到下面这个方法。方法中优先查看消息中是否含有 `responseId` 这个 key，若有，表明是来自 JS 端的消息响应，紧接着使用这个 id 取出 reponseCallback map 中的 block 并执行。反之，是来自 JS 正常的方法调用，则使用消息中的 `handlerName ` key 取出 handler map 中的 block 并执行。

```
- (void)flushMessageQueue:(NSString *)messageQueueString {
    if (messageQueueString == nil || messageQueueString.length == 0) {
        NSLog(@"WebViewJavascriptBridge: WARNING: ObjC got nil while fetching the message queue JSON from webview. This can happen if the WebViewJavascriptBridge JS is not currently present in the webview, e.g if the webview just loaded a new page.");
        return;
    }

    id messages = [self _deserializeMessageJSON:messageQueueString];
    for (WVJBMessage* message in messages) {
        if (![message isKindOfClass:[WVJBMessage class]]) {
            NSLog(@"WebViewJavascriptBridge: WARNING: Invalid %@ received: %@", [message class], message);
            continue;
        }
        [self _log:@"RCVD" json:message];
        
        NSString* responseId = message[@"responseId"];
        if (responseId) {
            WVJBResponseCallback responseCallback = _responseCallbacks[responseId];
            responseCallback(message[@"responseData"]);
            [self.responseCallbacks removeObjectForKey:responseId];
        } else {
            WVJBResponseCallback responseCallback = NULL;
            NSString* callbackId = message[@"callbackId"];
            if (callbackId) {
                responseCallback = ^(id responseData) {
                    if (responseData == nil) {
                        responseData = [NSNull null];
                    }
                    
                    WVJBMessage* msg = @{ @"responseId":callbackId, @"responseData":responseData };
                    [self _queueMessage:msg];
                };
            } else {
                responseCallback = ^(id ignoreResponseData) {
                    // Do nothing
                };
            }
            
            WVJBHandler handler = self.messageHandlers[message[@"handlerName"]];
            
            if (!handler) {
                NSLog(@"WVJBNoHandlerException, No handler for message from JS: %@", message);
                continue;
            }
            
            handler(message[@"data"], responseCallback);
        }
    }
}
```

# WebViewJavascriptBridge_JS 文件

这个文件包含 JS 端的实现代码，实现代码被赋值给一个 OC 的字符串，以便运行时注入。JS 端实现逻辑基本与 OC 端对应，唯一值得注意的是发送消息通过 iframe 间接发送。

```
function _doSend(message, responseCallback) {
	if (responseCallback) {
		var callbackId = 'cb_'+(uniqueId++)+'_'+new Date().getTime();
		responseCallbacks[callbackId] = responseCallback;
		message['callbackId'] = callbackId;
	}
	sendMessageQueue.push(message);
	messagingIframe.src = CUSTOM_PROTOCOL_SCHEME + '://' + QUEUE_HAS_MESSAGE;
}

messagingIframe = document.createElement('iframe');
messagingIframe.style.display = 'none';
document.documentElement.appendChild(messagingIframe);

```

> 又一年过去了。
