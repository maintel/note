# window.performance 分析 Html 加载过程

window.performance是HTML5 的一个新API。[详细文档](https://developer.mozilla.org/en-US/docs/Web/API/Window/performance)

## 浏览器一般加载顺序

如下图：

![浏览器加载顺序](http://blogqn.maintel.cn/011624558421157.png?e=3096780128&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:3ErJgje_bBt1umNYY6w5UUKVSgM=)

## 字段含义

- navigationStart

  当访问一个新页面时，当前页面卸载完成所返回的时间点，如果没有当前页面，则返回 fetchStart 时间点。
- redirectStart

  如果是HTTP重定向，如果跳转都是同源的，则返回开始获取发起重定向的时间点，否则返回0
- redirectEnd

  如果是同源重定向，返回重定向请求接收完最后一字节的时间点，否则返回0
- fetchStart

  如果请求是用http get发起的，返回浏览器查缓存之前的时间点，否则返回发起获取资源的时间点
- domainLookupStart

  返回浏览器发起DNS查询的时间点，如果是长连接或者请求文件来自缓存等本地存储则返回fetchStart时间点
- domainLookupEnd

  返回结束DNS查询的时间点，如果是长连接或者请求文件来自缓存等本地存储则返回fetchStart时间点
- connectStart

  返回浏览器向服务器发起建立获取当前文档的连接请求的时间点，如果是长连接或者请求文件来自缓存等本地存储则返回domainLookupEnd时间点
- connectEnd
  
  返回与服务器建立完成连接的时间点，如果是长连接或者请求文件来自缓存等本地存储则返回domainLookupEnd时间点
- requestStart

  返回浏览器发起请求的时间，不管是向server还是本地缓存或存储
- responseStart

  返回浏览器拿到第一个响应字节的时间点，包括从服务器、缓存或者其他本地存储
- responseEnd

  返回浏览器拿到最后一个响应字节或者传输连接关闭的时间点，包括从服务器、缓存或者其他本地存储
- unloadEventStart

  为 unload 事件被触发之时的 Unix毫秒时间戳。如果没有上一个文档，或者上一个文档或需要重定向的页面之一不同源，则该值返回 0。
- unloadEventEnd

  如果要打开的页面和当前的页面同源，则返回用户unload事件执行完成后的时间点，如果当前文档不存在或者不同源，则返回0
- domLoading

  返回浏览器将当前文档状态设置成loading的时间点
- domInteractive

  返回浏览器将当前文档状态设置成interactive的时间点
- domContentLoadedEventStart

  返回浏览器触发DOMContentLoaded事件执行之前的时间点
- domContentLoadedEventEnd

  返回浏览器触发DOMContentLoaded事件执行完成的时间点
- domComplete
  
  返回浏览器将当前文档状态设置成complete的时间点
- loadEventStart

  返回浏览器触发load事件执行之前的时间点，否则为0
- loadEventEnd

  返回浏览器触发load事件执行完成的时间点

然后就可以根据各个节点的时间来计算出各个阶段的耗时，比如渲染阶段为 domComplete - domLoading

---
参考资料

[使用window.performance对应用性能监测](http://www.cnblogs.com/joyho/articles/4384306.html)