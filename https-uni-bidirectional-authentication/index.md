# HTTPS 单向/双向认证


## HTTPS

![http&https](https://github.com/iCocoa/blog-diagram/raw/main/http.drawio.svg)

HyperText Transfer Protocol，超文本传输协议，是互联网上使用最广泛的一种协议。HTTP协议传输的数据都是未加密的，也就是明文的，不适合用来传输隐私信息。默认 80 端口。

Hyper Text Transfer Protocol over Secure Socket Layer，安全的超文本传输协议，网景公式设计了 SSL(Secure Sockets Layer) 协议用于对 Http 协议传输的数据进行加密，保证会话过程中的安全性。默认 443 端口。

SSL 包含对称加密和非对称加密，在建立传输链路时，SSL 首先使用非对称加密的方式对对称加密密钥进行加密，建立链路后，使用对称加密的方式对传输内容进行加密。非对称加密有更高的安全性，在这个基础上使用对称加密可以获得更快的速度，提高传输效率。

![asymmetric-encryption](https://images.ctfassets.net/slt3lc6tev37/34iiS7GovwS9tVEBisLVWb/65b0f7a31632a52ba6047c9d38daff0e/asymmetric-encryption.svg)

## 单向认证

客户端校验服务端证书

![unidirectional-authentication](https://github.com/iCocoa/blog-diagram/raw/main/unidirectional-authentication.drawio.svg)

1. **client hello** 
客户端发起一条到服务端的连接，包含客户端支持的 TLS 版本、支持的加密套件(即加密算法)以及客户端随机数。

2. **server hello**
服务端回应，包含服务端 SSL 证书、选择的加密套件以及服务端随机数。

3. **authentication**
客户端向颁发证书的 CA 验证服务端的 SSL 证书，以确认服务端是它声称的那个身份，从而保证客户端与域名真正的所有者通信。

4. **send premaster key**
客户端发送另一个随机数 “premaster key”，并对它使用服务端的公钥（从服务端 SSL 证书中获取得到）进行加密。

5. **decrypt premaster key**
服务端解密 premaster key

6. **create session key**
客户端和服务端各自使用客户端随机数、服务端随机数以及 premaster key 来计算 “session key”，即对称加密密钥，两边计算得出同样的结果并各自保留。

7. **client send finished**
客户端使用 session key 加密一条 finished 消息并发送给服务端。

8. **server send finished**
服务端使用 session key 加密一条 finished 消息并发送给客户端。

9. **symmetric encrypt communication**
使用对称加密来进行通信。

## 双向认证

客户端校验服务端证书 + 服务端校验客户端证书

![bidirectional-authentication](https://github.com/iCocoa/blog-diagram/raw/main/bidirectional-authentication.drawio.svg)

8. **verify certificate(digital signature)**
客户端发送一个 CertificateVerify 消息，这是使用客户端证书的私钥对前一个握手消息的签名。这个签名可以通过使用客户端证书的公钥进行验证。这样服务端就知道客户端可以访问证书的私钥，亦即拥有该证书。

## 证书校验什么

1. 验数字签名

客户端发送一个“Certificate Verify”消息，其中包含前一个握手消息的数字签名副本。此消息使用客户端证书的私钥进行签名。服务器可以使用客户端的公钥(在客户端证书中找到)来验证数字签名的消息摘要。一旦验证了数字签名，服务器就知道属于客户端的公钥与用于创建签名的私钥相匹配。

2. 验证书链

服务端维护一个受信任的ca列表，该列表决定服务端将接受哪些证书。服务端将使用来自CA证书的公钥(在其可信CA列表中)来验证CA对所提供证书的数字签名。如果消息摘要已经更改，或者公钥与用于签名证书的CA私钥不对应，则验证失败，握手终止。

3. 验有效期

服务端将当前日期与证书中列出的有效期进行比较。如果过期日期没有通过，当前日期在期限内，那么一切都好。如果不是，则验证失败，握手终止。

4. 验证书撤销状态

服务端将客户端证书与系统中已撤销的证书列表进行比较。如果客户端证书在列表中，则验证失败，握手终止。

## nginx 配置双向认证

```
listen       443;
server_name  localhost;
ssl on;
ssl_certificate      /usr/local/opt/nginx/certificates/server.cer;
ssl_certificate_key  /usr/local/opt/nginx/certificates/server.key.pem;
ssl_client_certificate /usr/local/opt/nginx/certificates/ca.cer;
ssl_verify_client    on;
```

开启 ssl
ssl_certificate 是服务端证书的路径，ssl_certificate_key是服务端私钥的路径
ssl_verify_client 是配置双向认证（client certificate）
ssl_client_certificate 是签发客户端证书的根证书

> 为什么是根证书，因为可以签发很多客户端证书，只要是由该根证书签发的，服务端都视为认证通过

配置完成以后，一般需要把80端口的http请求跳转到443端口，否则用户可以通过80端口以http方式访问，就失去了安全保护的意义

## iOS 客户端

1. 使用 NSURLSession 发出一个 https 请求

```
NSURLSessionConfiguration *configuration = [NSURLSessionConfiguration defaultSessionConfiguration];
    
NSURLSession *session = [NSURLSession sessionWithConfiguration:configuration delegate:self delegateQueue:nil];
    
NSURL *url = [NSURL URLWithString:@"https://localhost/test"];

NSMutableURLRequest *request = [[NSMutableURLRequest alloc] initWithURL:url];
[request setCachePolicy:NSURLRequestReloadIgnoringLocalCacheData];
[request setHTTPShouldHandleCookies:NO];
[request setTimeoutInterval:30];
[request setHTTPMethod:@"GET"];
    
NSURLSessionDataTask *task = [session dataTaskWithURL:url completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
    NSString *message = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    NSLog(@"%@", message);
}];
    
[task resume];
```

2. 认证处理

握手阶段回调方法两次，一次是 server 认证，一次是 client 认证。

```
- (void)URLSession:(NSURLSession *)session didReceiveChallenge:(NSURLAuthenticationChallenge *)challenge completionHandler:(void (^)(NSURLSessionAuthChallengeDisposition disposition, NSURLCredential *credential))completionHandler
{
    NSString *method = challenge.protectionSpace.authenticationMethod;
    NSLog(@"%@", method);
    
    // 服务端证书认证
    if([method isEqualToString:NSURLAuthenticationMethodServerTrust]){
        
        NSString *host = challenge.protectionSpace.host;
        NSLog(@"%@", host);
        
        NSURLCredential *credential = [NSURLCredential credentialForTrust:challenge.protectionSpace.serverTrust];
        completionHandler(NSURLSessionAuthChallengeUseCredential, credential);
        return;
    }

    // 客户端证书
    NSString *thePath = [[NSBundle mainBundle] pathForResource:@"client" ofType:@"p12"];
    NSData *PKCS12Data = [[NSData alloc] initWithContentsOfFile:thePath];
    CFDataRef inPKCS12Data = (CFDataRef)CFBridgingRetain(PKCS12Data);
    SecIdentityRef identity;
    
    // 读取p12证书中的内容
    OSStatus result = [self extractP12Data:inPKCS12Data toIdentity:&identity];
    if(result != errSecSuccess){
        completionHandler(NSURLSessionAuthChallengeCancelAuthenticationChallenge, nil);
        return;
    }
    
    SecCertificateRef certificate = NULL;
    SecIdentityCopyCertificate (identity, &certificate);
    
    const void *certs[] = {certificate};
    CFArrayRef certArray = CFArrayCreate(kCFAllocatorDefault, certs, 1, NULL);
    
    NSURLCredential *credential = [NSURLCredential credentialWithIdentity:identity certificates:(NSArray*)CFBridgingRelease(certArray) persistence:NSURLCredentialPersistencePermanent];
    
    completionHandler(NSURLSessionAuthChallengeUseCredential, credential);
}

- (OSStatus)extractP12Data:(CFDataRef)inP12Data toIdentity:(SecIdentityRef*)identity {
    
    OSStatus securityError = errSecSuccess;
    
    CFStringRef password = CFSTR("the_password");
    const void *keys[] = { kSecImportExportPassphrase };
    const void *values[] = { password };
    
    CFDictionaryRef options = CFDictionaryCreate(NULL, keys, values, 1, NULL, NULL);
    
    CFArrayRef items = CFArrayCreate(NULL, 0, 0, NULL);
    securityError = SecPKCS12Import(inP12Data, options, &items);
    
    if (securityError == 0) {
        CFDictionaryRef ident = CFArrayGetValueAtIndex(items,0);
        const void *tempIdentity = NULL;
        tempIdentity = CFDictionaryGetValue(ident, kSecImportItemIdentity);
        *identity = (SecIdentityRef)tempIdentity;
    }
    
    if (options) {
        CFRelease(options);
    }
    
    return securityError;
}
```

## Postman 客户端

配置路径：偏好设置 》 证书 》 添加客户端证书

## HTTPS 办不到的事情

* 隐藏要访问的站点名称

这是因为网站的名称(又名“域名”)是通过DNS(域名服务)发送的，而DNS(域名服务)不在HTTPS隧道内。它在建立安全连接之前发送。中间的窃听者可以看到你要访问的网站的名称(例如 google.com)，只是不能读取任何来回传输的实际内容。除非采用 [DNSSEC](https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en) 。

* 防止访问恶意网站

HTTPS并不能确保网站本身是安全的。仅仅因为连接安全并不意味着你不会连接到一个由不法分子运营的网站。

* 提供匿名性（IP、物理位置）

HTTPS 不会隐藏物理位置或个人身份。个人 IP 地址不能加密，因为如果 IP 地址也被加密了，互联网就不知道该把它发送到哪里。而且它也不会在你访问的网站上掩盖你的身份，你访问的网站仍然知道你的一切。

* 防止感染病毒

HTTPS 不是过滤器，所以会有可能在 HTTPS 连接中收到病毒或木马。如果网络服务器被感染，病毒就会像其他报文一样被发送到 HTTPS 流中。然而，HTTPS确实阻止了中间人向流量中注入木马。

* 防止电脑被黑

HTTPS 仅在数据在客户端和服务端之间传输时提供安全保证，如果有恶意软件在监控连接的一端的流量，它仍然可以读取加密之前和之后的 HTTPS 流。


参考链接

* [Wikipedia, Transport Layer Security](https://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake)
* [first-few-milliseconds-of-https](http://www.moserware.com/2009/06/first-few-milliseconds-of-https.html)
