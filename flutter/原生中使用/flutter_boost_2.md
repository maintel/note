# flutter boost 解决打开flutter 黑屏问题

在原生层先用一个 FlutterSplashView 来过渡，

flutter 层 监听第一帧被加载的时候使用 一个 overE view 然后通过路由来加载具体的 widgetPage