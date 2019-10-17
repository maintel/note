<!-- TOC -->

- [监控加载过程](#监控加载过程)
  - [从源生层面分析](#从源生层面分析)
  - [从 H5 端进行监控](#从-h5-端进行监控)
    - [通过源生代码](#通过源生代码)
    - [通过 chrome 浏览器的调试功能](#通过-chrome-浏览器的调试功能)

<!-- /TOC -->

# 监控加载过程

> 获取 webView 加载过程中的各个阶段的耗时情况

由于页面打开的过程中白屏情况严重，要解决问题，首先要分析问题出在哪。

## 从源生层面分析

分别在加载 webView 的 activity 的 onCreate 、onResume 方法中记录时间

```java
LogUtils.e("onResume::" + System.currentTimeMillis());
```

对 webView 设置自定义 WebViewClient,并记录 html 的加载时间

```java
    webView.setWebViewClient(new MyWebViewClient());

    private class MyWebViewClient extends WebViewClient {
        @Override
        public void onPageFinished(WebView view, String url) {
            super.onPageFinished(view, url);
            LogUtils.e("onPageFinished::" + System.currentTimeMillis());
        }

        @Override
        public void onPageStarted(WebView webView, String s, Bitmap bitmap) {
            super.onPageStarted(webView, s, bitmap);
            LogUtils.e("onPageStarted::" + System.currentTimeMillis());
        }
    }
```

**原生监控结果**

> E/tag: onCreate::1519980761086

> E/tag: onResume::1519980761202

> E/tag: onPageStarted::1519980761246

> E/tag: onPageFinished::1519980762874

> ...

可以看到主要耗时是在 Html 的加载过程中。

## 从 H5 端进行监控

这里主要是通过 performance.timing 来分析 H5 加载过程中各个节点的耗时情况

有两个方法

### 通过源生代码

增加以下代码

```java
webView.setWebChromeClient(new WebChromeClient());
```

然后在 WebViewClient.onPageFinished 结束后，延迟几秒钟执行 

```java
webview.loadUrl("javascript:alert(JSON.stringify(window.performance.timing))");
```
这样就可以看到各个节点的耗时，但是这样不便于记录和观察，可以通过一个写一个 js 方法来把数据获取过来进行输出。

不过一般采用第二种方法比较方便。

### 通过 chrome 浏览器的调试功能

**注意：** Android 的版本要在 4.0 以上

在 chrome 中输入 chrome://inspect 如下：

![chromeinspect](http://blogqn.maintel.cn/QQ20180302-170347@2x.png?e=3096781460&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:hdfqLl0D8y77urO_I44XYU1E2mg=)

然后点击 inspect，在控制台输入window.performance

![performance](http://blogqn.maintel.cn/QQ20180302-170814@2x.png?e=3096781717&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:MyWvKHEazHhT6u3GzIT95kaLViI=)

---
各参数的解读可以参考[这里](../../前端/optimize/window.performance分析html加载.md)

然后就可以通过上面拿到的内容分析出具体是哪里太过耗时然后针对性的进行优化。
