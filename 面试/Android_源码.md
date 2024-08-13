<!-- TOC -->

- [Android动画框架实现原理](#android动画框架实现原理)
- [Android各个版本API的区别](#android各个版本api的区别)
- [Requestlayout，onlayout，onDraw，DrawChild区别与联系](#requestlayoutonlayoutondrawdrawchild区别与联系)
- [invalidate和postInvalidate的区别及使用](#invalidate和postinvalidate的区别及使用)
- [Activity-Window-View三者的差别](#activity-window-view三者的差别)
- [谈谈对 Volley 的理解](#谈谈对-volley-的理解)
- [如何优化自定义 View](#如何优化自定义-view)
- [低版本SDK如何实现高版本api？](#低版本sdk如何实现高版本api)
- [描述一次网络请求的流程](#描述一次网络请求的流程)
- [HttpUrlConnection 和 okhttp关系](#httpurlconnection-和-okhttp关系)
- [Bitmap 对象的理解](#bitmap-对象的理解)
- [ActivityThread，AMS，WMS的工作原理](#activitythreadamswms的工作原理)
- [自定义 View 如何考虑机型适配](#自定义-view-如何考虑机型适配)
- [自定义View的事件](#自定义view的事件)
- [AsyncTask + HttpClient 与 AsyncHttpClient 有什么区别？](#asynctask--httpclient-与-asynchttpclient-有什么区别)
- [LaunchMode 应用场景](#launchmode-应用场景)
- [AsyncTask 如何使用](#asynctask-如何使用)
- [SpareArray 原理](#sparearray-原理)
- [请介绍下 ContentProvider 是如何实现数据共享的](#请介绍下-contentprovider-是如何实现数据共享的)
- [Android Service 与 Activity 之间通信的几种方式](#android-service-与-activity-之间通信的几种方式)
- [IntentService 原理及作用是什么？](#intentservice-原理及作用是什么)
- [说说 Activity、Intent、Service 是什么关系](#说说-activityintentservice-是什么关系)
- [ApplicationContext 和 ActivityContext 的区别](#applicationcontext-和-activitycontext-的区别)
- [SP 是进程同步的吗?有什么方法做到同步？](#sp-是进程同步的吗有什么方法做到同步)
- [谈谈多线程在Android中的使用](#谈谈多线程在android中的使用)
- [进程和 Application 的生命周期](#进程和-application-的生命周期)
- [封装 View 的时候怎么知道 view 的大小](#封装-view-的时候怎么知道-view-的大小)
- [RecycleView 原理](#recycleview-原理)
- [AndroidManifest 的作用与理解](#androidmanifest-的作用与理解)
- [scrollView 的原理](#scrollview-的原理)

<!-- /TOC -->

# Android动画框架实现原理

Animation 框架定义了透明度，旋转，缩放和位移几种常见的动画，而且控制的是整个 View，实现原理是每次绘制视图时在 `View.draw(Canvas canvas, ViewGroup parent, long drawingTime)`方法中获取该 View 的 Animation 的 Transformation 值，然后调用 canvas.concat(transformToApply.getMatrix())，通过矩阵运算完成动画帧，如果动画没有完成，继续调用 invalidate() 函数，启动下次绘制来驱动动画，动画过程中的帧之间间隙时间是绘制函数所消耗的时间，可能会导致动画消耗比较多的 CPU 资源，最重要的是，动画改变的只是显示，并不能相应事件。

# Android各个版本API的区别

只说些主要的:
- 4.4

  - 添加了新的全屏沉浸模式
  - 存储访问框架
  - 透明系统 UI 样式
  - 基于 Chromium 的 WebView 的全新实现
  [官网](https://developer.android.com/about/versions/kitkat.html?hl=zh-cn)
  

- 5.0

  - 把ART模式作为默认的运行模式
  - 引入了Material Design并提供了UI工具包
  - 引入了全新的 Camera API
  - 引入了 Android 扩展包 (AEP)，支持 OpenGL ES 3.1
  - 允许应用利用蓝牙低能耗 (BLE) 执行并发操作的 API，可同时实现扫描（中心模式）和广播（外设模式）
  [官网](https://developer.android.com/about/versions/lollipop.html?hl=zh-cn)

- 6.0

  - 引入了一种新的权限模式 运行时权限检查
  - 取消支持 Apache HTTP 客户端
  - 新的通知构建方法
  - 增加了更强的蓝牙以及 WIFI 保护权限
  [官网](https://developer.android.com/about/versions/marshmallow/android-6.0-changes.html?hl=zh-cn)

- 7.0

  - 系统权限更改，提高了私有文件的安全性
  > 传递软件包网域外的 file:// URI 可能给接收器留下无法访问的路径。因此，尝试传递 file:// URI 会触发 FileUriExposedException。分享私有文件内容的推荐方法是使用 FileProvider。
  - 移除了三项隐式广播

    - CONNECTIVITY_ACTION
    - ACTION_NEW_PICTURE
    - ACTION_NEW_VIDEO

  [官网](https://developer.android.com/about/versions/nougat/android-7.0-changes.html?hl=zh-cn)
- 8.0

  - 后台服务限制，位于后台的应用无法使用 `startService()` 
  - 应用无法使用其清单注册大部分隐式广播
  - 降低了后台应用接收位置更新的频率
  
  [官网](https://developer.android.com/about/versions/oreo/android-8.0-changes.html?hl=zh-cn)

# Requestlayout，onlayout，onDraw，DrawChild区别与联系

- RequestLayout()

  当 view 的大小、位置发生变化时调用 RequestLayout 请求重新布局，将变化后的 View 更新到屏幕上。如果子 View 调用了该方法，那么会从 View 树重新进行一次测量、布局、绘制这三个流程。所以会调用 onMeaue、 onLayout、onDraw，其中 onDraw 的调用可能会也可能不会

- DrawChild()

  DrawChild 会去回调没一个子视图的 draw 方法

# invalidate和postInvalidate的区别及使用

都是用来刷新界面的，不同的是 invalidate 不能在工作线程中使用，只能在主线程中使用， postInvalidate 可以在工作线程中使用。
# Activity-Window-View三者的差别

首先能知道的是 view 的添加删除等是通过 window 来实现的，所以 view 的呈现必须通过 window 来实现。window 通过 windowManager 来管理 view。

window 是一个抽象的概念，它的实现是 phoneWindow。通过 acitivity 的启动过程可以知道 window 的初始化是在 activity 的初始化过程中实现的。

所以 activity 是用来管理 window 的，而 window 则是用来呈现 view，同时 activity 还要用来管理 view 的一些回调。

# 谈谈对 Volley 的理解

Volley 是 Google 官方出的一套小而巧的异步请求库，该框架封装的扩展性很强，支持 HttpClient、HttpUrlConnection，甚至支持 OkHttp。而且 Volley 里面也封装了 ImageLoader ，所以如果你愿意你甚至不需要使用图片加载框架，不过这块功能没有一些专门的图片加载框架强大，对于简单的需求可以使用，对于稍复杂点的需求还是需要用到专门的图片加载框架。

Volley 也有缺陷，比如不支持 post 大数据，所以不适合上传文件。不过 Volley 设计的初衷本身也就是为频繁的、数据量小的网络请求而生！

# 如何优化自定义 View

[优化](http://hukai.me/android-training-course-in-chinese/ui/custom-view/optimize-view.html)

[优化2](http://ibigerbiger.me/2016/10/20/Android%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96%28%E4%BA%8C%29-%E8%87%AA%E5%AE%9A%E4%B9%89View%E4%BC%98%E5%8C%96/)

- 不要在 onDraw 中创建对象
- 尽可能的减少 onDraw 的调用次数
- 尽量减少 view 的层级

# 低版本SDK如何实现高版本api？

可以使用 @TargeApi($API_LEVEL) 

或者在运行时判断版本，只有符合版本时才进行调用，同时在低版本中提供相应的处理办法。比如将高版本的部分代码拷贝出来进行改造等。

# 描述一次网络请求的流程

域名解析、TCP的三次握手、建立TCP连接后发起HTTP请求、服务器响应HTTP请求

[参考](https://www.linux178.com/web/httprequest.html)

# HttpUrlConnection 和 okhttp关系

从层级关系上来讲，两者位于同一层级，都是用 socket 实现了网络连接。但是两者在 IO 的实现方面不同，HttpUrlConnection 使用的是 InputStream 和 OutputStream，okhttp 使用的是 sink 和 source，同时 OkHttp 又封装了线程池，封装了数据转换，封装了参数使用、错误处理等，api 使用起来更加方便。

# Bitmap 对象的理解

Bitmap 是 android 中经常使用的一个类，它代表了一个图片资源。
Bitmap 本身十分大严重消耗内存，具体大小可以参考[这里](https://github.com/maintel/notebook/blob/master/android/%E4%BD%A0%E7%9F%A5%E9%81%93%E4%BD%A0%E7%9A%84bitmap%E5%8D%A0%E5%A4%9A%E5%A4%A7%E4%B9%88.md)，所以在使用的时候要做好工作防止OOM，主要有以下方式：

- 合理利用 inSampleSize 和矩阵
- 合理选择 Bitmap 的像素格式
- 及时回收内存
- 合理的缓存
- 合理的压缩图片
- 捕获 OOM 异常

[优化参考](https://cloud.tencent.com/developer/article/1071001)

# ActivityThread，AMS，WMS的工作原理

# 自定义 View 如何考虑机型适配

# 自定义View的事件

- 事件分发原理: 责任链模式，事件层层传递，直到被消费。
- View 的 dispatchTouchEvent 主要用于调度自身的监听器和 onTouchEvent。
- View的事件的调度顺序是 onTouchListener > onTouchEvent > onLongClickListener > onClickListener 。
- 不论 View 自身是否注册点击事件，只要 View 是可点击的就会消费事件。
- 事件是否被消费由返回值决定，true 表示消费，false 表示不消费，与是否使用了事件无关。
- ViewGroup 中可能有多个 ChildView 时，将事件分配给包含点击位置的 ChildView。
- ViewGroup 和 ChildView 同时注册了事件监听器(onClick等)，由 ChildView 消费。
- 一次触摸流程中产生事件应被同一 View 消费，全部接收或者全部拒绝。
- 只要接受 ACTION_DOWN 就意味着接受所有的事件，拒绝 ACTION_DOWN 则不会收到后续内容。
- 如果当前正在处理的事件被上层 View 拦截，会收到一个 ACTION_CANCEL，后续事件不会再传递过来。

[参考](http://www.gcssloop.com/customview/dispatch-touchevent-source)

# AsyncTask + HttpClient 与 AsyncHttpClient 有什么区别？

- AsyncHttpClient

  是一个访问网络的库，封装了常用的网络访问请求，可以很方便的进行网络访问等，它的底层使用了 Netty。

- AsyncTask + HttpClient

  属于手动通过 AsyncTask 和 HttpClient 来实现网络访问，需要自己进行封装，使用麻烦。

# LaunchMode 应用场景

- singleTop 适合接收通知启动的内容显示页面，或者根据业务逻辑大量的重复性页面但一次性返回的。

  比如知乎的客户端一段时间内推送了很多问题的回答，一个一个点开看的页面就使用 singleTop 实现。

- singleTask  适合做为应用的入口点，防止被多次启动。

- singleInstance 适合需要与程序分离开的页面。

# AsyncTask 如何使用

继承 AsyncTask ，实现四个方法

- onPreExecute

  该方法在 main 线程执行。执行了execute()方法后就会在UI线程上执行onPreExecute()方法，该方法在task真正执行前运行。
- doInBackground

  该方法在子线程中运行，用来执行耗时任务。
- onProgressUpdate

  该方法在 main 线程执行，用来回调项目的进度，这个方法可以多次被回调，在 doInBackground 中调用 publishProgress 方法可以触发此方法的回调。
- onPostExecute

  该方法在 main 线程中执行，doInBackground 的返回值在这个方法中会被返回。表示任务已经执行完了。

然后调用 execute() 方法开始执行。

[参考](https://blog.csdn.net/iispring/article/details/50639090)

[工作原理](https://blog.csdn.net/iispring/article/details/50670388)

# SpareArray 原理

SpareArray 是纯属组的方式来存放数据。具有比 HashMap 更高的内存使用效率。
SpareArray 初始长度为 10。

SpareArray 内部有两个数组，一个数组用来存储KEY 一个用来存储 Values，key 都是 int 型的。

put 操作：

  - 存放 key 的数组是有序的（这也是为什么 key 是 int 型的原因）
  - 通过二分查找找到当前 key 应该所在的位置（索引）
  - 如果 key 冲突就直接覆盖 value
  - 如果 key 不冲突但是当前的值为 DELETE 则覆盖 key 和 value
  - 如果上面不能满足，则 gc 然后执行插入操作

remove 操作：

  - 根据 key 查找索引
  - 如果查找到了就把当前的 value 置为 DELETED

  不直接进行删除的原因，是为了减少频繁的数组压缩操作。


[参考](https://juejin.im/entry/57c3e8c48ac24700634bd3cf)

[参考](http://www.voidcn.com/article/p-zyywypiq-bnx.html)

# 请介绍下 ContentProvider 是如何实现数据共享的

程序通过实现 ContentProvider 的抽象接口把自己的数据暴露出去，外界通过 URI 来作为标志访问数据。底层通过 binder 来实现。

# Android Service 与 Activity 之间通信的几种方式

- 通过 binder
- 通过广播接收者
- 通过自定义回调

- 直接使用静态内部类
- 通过读写文件的方式

# IntentService 原理及作用是什么？

IntentService 继承自 service，但是内部通过将工作任务放在了子线程中执行，然后通过 handler 来实现数据回调。

在 onCreate 方法中创建了工作线程 HandlerThread，并通过它的 looper 来创建了一个 handler。
在 onStart 方法中分发消息，分发消息。

ServiceHandler 接收到消息后会调用 onHandleIntent 方法，并且在 onHandleIntent 执行结束后执行 stopSelf 来结束自己。

作用：执行耗时任务。

# 说说 Activity、Intent、Service 是什么关系

- activity 用来显示界面与用户交互
- intent 作为 activity 和 service 的通讯
- service 执行后台任务

# ApplicationContext 和 ActivityContext 的区别

- ApplicationContext 伴随着整个应用的生命周期，随着应用的开始而开始结束而结束
- ActivityContext 伴随着 activity 的生命周期。

# SP 是进程同步的吗?有什么方法做到同步？

SharedPreferences 不是进程同步的。

可以使用 MODE_MULTI_PROCESS 模式来保证同步，但是此模式已经废弃，而且官方说明中提到不能够保证此模式总是正确的。官方推荐使用 ContentProvier 来实现进程间的文件共享。

[参考](https://www.jianshu.com/p/875d13458538)


# 谈谈多线程在Android中的使用

Android 中多线程都是在执行一些耗时任务。Android 中开启多线程的方法一般是：
- new Thread
- 线程池
- AsnysTask
- IntentService 在内部也是使用了子线程

子线程与主线程之间的通讯主要通过 Handler 来实现，AsnysTask 内部也是封装了 handler。

Android 中频繁的创建和释放线程是一个比较消耗资源的事情，因此建议使用线程池来管理线程。

另外在使用过程中要注意线程安全问题。

# 进程和 Application 的生命周期

Application 的生命周期相当于整个应用的生命周期，但是进程略微不同，一般来说一个应用就是一个进程，这个时候两者的生命周期时一样的。

在多进程应用中，一些后台进程可能会被系统以外的结束掉，这个时候两者的生命周期就不同了。

# 封装 View 的时候怎么知道 view 的大小

重写 onMeasure() 方法，通过 MeasureSpec 的 getMode 和 getSize 来获取宽高的模式和值。MeasureSpec 的来源是父View，一级级向上最终可以跟踪到跟View。

# RecycleView 原理

- 绘制流程

  RecyclerView将它的measure与layout过程委托给了RecyclerView.LayoutManager来处理，并且，它对子控件的measure及layout过程是逐个处理的，也就是说，执行完成一个子控件的measure及layout过程再去执行下一个。

  在RecyclerView的measure及layout阶段，填充ItemView的算法为：向父容器增加子控件，测量子控件大小，布局子控件，布局锚点向当前布局方向平移子控件大小，重复上诉步骤至RecyclerView可绘制空间消耗完毕或子控件已全部填充。 可绘制控件的大小就是RecycleView 的父容器大小。

  RecyclerView的draw过程可以分为２部分来看：RecyclerView负责绘制所有decoration；ItemView的绘制由ViewGroup处理，这里的绘制是android常规绘制逻辑。
- 滑动流程

  RecyclerView的滑动过程可以分为2个阶段：手指在屏幕上移动，使RecyclerView滑动的过程，可以称为scroll；手指离开屏幕，RecyclerView继续滑动一段距离的过程，可以称为fling。

  scroll 相对简单，它先判断手指移动的距离与阈值之间的关系，然后调用方法使 RecyclerView 进行滑动。当接收到ACTION_UP事件时，会根据之前的滑动距离与时间计算出一个初速度yvel，再以此初速度调用 fling。最终他们都是通过LayoutManager.scrollBy()方法完成滑动。

- 重用 itemView

  Recycler的作用就是重用ItemView。在填充ItemView的时候，ItemView是从它获取的；滑出屏幕的ItemView是由它回收的。对于不同状态的ItemView存储在了不同的集合中，比如有scrapped、cached、exCached、recycled，当然这些集合并不是都定义在同一个类里。 

[Android RecyclerView工作原理分析（上）](https://blog.csdn.net/xyh269/article/details/53047855)

# AndroidManifest 的作用与理解

清单文件提供了一个应用程序运行的所需要的必要信息，即在该应用程序的任何代码运行之前系统所必须拥有的信息。

- 提供软件包名
- 描述各个应用组件
  - 主题
  - 键盘适配
  - activity 启动模式等
- 声明权限
- 指定版本号和版本名
- 指定应用所需要的设备，google paly 可以根据提供的内容过滤掉不符合需求的设备。
- 指定应用入口，图标，应用名等。
- 指定应用的主题

不过现在有些内容会被 gralde 中指定的替换掉，例如版本号、软件包名等。

# scrollView 的原理

