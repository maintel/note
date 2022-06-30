最近在做一个 vpn 的工具需要用到  root 权限，调研了几种[提权方案](./mac%E6%8F%90%E6%9D%83%E6%96%B9%E6%A1%88%E7%A0%94%E7%A9%B6.md)最终决定使用 SMJobBless 的方式。

网上有不少资料，可以参考下面两个

https://www.jianshu.com/p/7ee356bcedf8

https://github.com/davidleee/HexoBlogSource/blob/3a66d392c0938500c213bbeddf163d93c983b595/source/_posts/ipc-for-macOS.md


坑：

对于第一篇的签名的地方不要和博客的写的一样。certificate leaf 和 and certificate [field.xxxxx] 都需要替换。可以设置过签名以后使用 codesign -d -r - xxx 来查看 app 和 helper 的签名。

code 2 文件没有被正确复制到指定的目录
code 4 或者 8 签名问题，app 和 helper 工具的签名不匹配导致的。参考上面。

SMJobBless 对应错误码的源文件在 SMErrors.h 中。

```
enum {
    kSMErrorInternalFailure = 2,
    kSMErrorInvalidSignature,
    kSMErrorAuthorizationFailure,
    kSMErrorToolNotValid,
    kSMErrorJobNotFound,
    kSMErrorServiceUnavailable,
    kSMErrorJobPlistNotFound,
    kSMErrorJobMustBeEnabled,
    kSMErrorInvalidPlist,
};
```