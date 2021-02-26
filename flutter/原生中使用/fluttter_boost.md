flutter_boost 复用了 flutterEngine

在 boostFlutterActivity 初始化的时候会先创建 FlutterActivityAndFragmentDelegate 然后调用 setupFlutterEngine 从而从 FlutterBoost 中获取引擎， FlutterBoost 是一个单例类。


# flutter 打开 native 页面

```dart
              FlutterBoost.singleton
                  .open("select_area");
```

open 方法

```dart
  Future<Map<dynamic, dynamic>> open(String url,
      {Map<dynamic, dynamic> urlParams, Map<dynamic, dynamic> exts}) {
    Map<dynamic, dynamic> properties = new Map<dynamic, dynamic>();
    properties["url"] = url;
    properties["urlParams"] = urlParams;
    properties["exts"] = exts;
    return channel.invokeMethod<Map<dynamic, dynamic>>('openPage', properties);
  }
```

其实内部也是使用了一个 channel 来和 native 进行通讯。这个 channel 就是 

```dart
MethodChannel _methodChannel = MethodChannel("flutter_boost");
```

flutter_boost 在 FlutterBoostPlugin 中注册了这个 channel，在 BoostMethodHandler 中处理了它自己注册的回调

```java
    public void onMethodCall(MethodCall methodCall, final Result result) {
            FlutterViewContainerManager mManager = (FlutterViewContainerManager)FlutterBoost.instance().containerManager();
            String var4 = methodCall.method;
            byte var5 = -1;
            switch(var4.hashCode()) {
           
            case -504772615:
                if (var4.equals("openPage")) {
                    var5 = 1;
                }
                break;
            }

            String newId;
            Map resultData;
            switch(var5) {
            case 1:
                try {
                    Map<String, Object> params = (Map)methodCall.argument("urlParams");
                    resultData = (Map)methodCall.argument("exts");
                    String url = (String)methodCall.argument("url");
                    mManager.openContainer(url, params, resultData, new OnResult() {
                        public void onResult(Map<String, Object> rlt) {
                            if (result != null) {
                                result.success(rlt);
                            }

                        }
                    });
                } catch (Throwable var11) {
                    result.error("open page error", var11.getMessage(), Log.getStackTraceString(var11));
                }
                break;
            default:
                result.notImplemented();
            }

        }
    }
```

接着它是调用了 FlutterVieContainerManager.openContainer 方法

```java
    void openContainer(String url, Map<String, Object> urlParams, Map<String, Object> exts, FlutterViewContainerManager.OnResult onResult) {
        Context context = FlutterBoost.instance().currentActivity();
        if (context == null) {
            context = FlutterBoost.instance().platform().getApplication();
        }

        if (urlParams == null) {
            urlParams = new HashMap();
        }

        int requestCode = 0;
        Object v = ((Map)urlParams).remove("requestCode");
        if (v != null) {
            requestCode = Integer.valueOf(String.valueOf(v));
        }

        String uniqueId = ContainerRecord.genUniqueId(url);
        ((Map)urlParams).put("__container_uniqueId_key__", uniqueId);
        IContainerRecord currentTopRecord = this.getCurrentTopRecord();
        if (onResult != null && currentTopRecord != null) {
            this.mOnResults.put(currentTopRecord.uniqueId(), onResult);
        }

        FlutterBoost.instance().platform().openContainer((Context)context, url, (Map)urlParams, requestCode, exts);
    }
```

这个方法先获取了context，然后添加了一些参数，最终调用了  FlutterBoost.instance().platform().openContainer，而这个 Platform 就是一开始初始化的时候添加的，

```kotlin
        val router = INativeRouter { context, url, urlParams, requestCode, exts ->
            // 自定义相关逻辑。
        }

        val platform = FlutterBoost
                .ConfigBuilder(MyApplication.getApplication(), router)  // 这里添加了 router
                .isDebug(true)
                .whenEngineStart(FlutterBoost.ConfigBuilder.FLUTTER_ACTIVITY_CREATED)
                .renderMode(FlutterView.RenderMode.texture)
                .lifecycleListener(boostLifecycleListener)
                .build()
        FlutterBoost.instance().init(platform)
```

```java
        public Platform build() {
            Platform platform = new Platform() {

                public void openContainer(Context context, String url, Map<String, Object> urlParams, int requestCode, Map<String, Object> exts) {
                    ConfigBuilder.this.router.openContainer(context, url, urlParams, requestCode, exts);
                }
            };
            platform.lifecycleListener = this.lifecycleListener;
            return platform;
        }
```

可以看到 platform.openContainer 方法最终调用的就是我们上面添加的 router，接下来的逻辑就可以交给我们自己处理了。

## 从 Android 端拿到 onActivityResult 数据

需要**注意**的是flutter_boost 的回调只支持 map 样式的。

```dart
              FlutterBoost.singleton
                  .open("select_area")
                  .then((Map<dynamic, dynamic> value) {
                    print(value);  // 直接在这里面拿到回调。
                  });
```

首先我们打开 flutter 页面的基础是 boostFlutterActivity，所以相关的逻辑入口肯定也在 BoostFlutterActivity.onActivityResult 中，

```java
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        this.delegate.onActivityResult(requestCode, resultCode, data);
    }
```

代码很简单，直接调用了 FlutterActivityAndFragmentDelegate.onActivityResult。

```java
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        this.mSyncer.onActivityResult(requestCode, resultCode, data);
        Map<String, Object> result = null;
        if (data != null) {
            Serializable rlt = data.getSerializableExtra("_flutter_result_");
            if (rlt instanceof Map) {
                result = (Map)rlt;
            }
        }

        this.mSyncer.onContainerResult(requestCode, resultCode, result);
        this.ensureAlive();
        if (this.flutterEngine != null) {
            Log.v("FlutterActivityAndFragmentDelegate", "Forwarding onActivityResult() to FlutterEngine:\nrequestCode: " + requestCode + "\nresultCode: " + resultCode + "\ndata: " + data);
            this.flutterEngine.getActivityControlSurface().onActivityResult(requestCode, resultCode, data);
        } else {
            Log.w("FlutterActivityAndFragmentDelegate", "onActivityResult() invoked before NewFlutterFragment was attached to an Activity.");
        }

    }
```

上面的一部分代码可以看到先后调用了 mSyncer.onActivityResult  和 mSyncer.onContainerResult，以及 flutterEngine.getActivityControlSurface().onActivityResult，最后一个不用管是由 flutterEngine 实现的内容，前面两个则是由 flutterBoost 实现的。而且从上面代码可以看到如果想要通过这种方式来返回值，则内容必须是 Map 形式的，而且放在 data 中的key 必须是 _flutter_result_。

mSyncer 的实现类是 ContainerRecord。

```java

this.mSyncer = FlutterBoost.instance().containerManager().generateSyncer(this);

public class FlutterViewContainerManager implements IContainerManager {

    FlutterViewContainerManager() {
    }

    public IOperateSyncer generateSyncer(IFlutterViewContainer container) {
        ContainerRecord record = new ContainerRecord(this, container);

        return record;
    }
}

// ContainerRecord
public class ContainerRecord implements IContainerRecord {

    ContainerRecord(FlutterViewContainerManager manager, IFlutterViewContainer container) {
        this.mManager = manager;
    }

    public void onActivityResult(int requestCode, int resultCode, Intent data) {
    }

    public void onContainerResult(int requestCode, int resultCode, Map<String, Object> result) {
        this.mManager.setContainerResult(this, requestCode, resultCode, result);
    }    
}

```

可以看到 mSyncer.onActivityResult 是一个空实现，而 mSyncer.onContainerResult 则最终又调用了 FlutterViewContainerManager.setContainerResult 方法。

```java
    void setContainerResult(IContainerRecord record, int requestCode, int resultCode, Map<String, Object> result) {

        if (result == null) {
            result = new HashMap();
        }

        ((Map)result).put("_requestCode__", requestCode);
        ((Map)result).put("_resultCode__", resultCode);
        FlutterViewContainerManager.OnResult onResult = (FlutterViewContainerManager.OnResult)this.mOnResults.remove(record.uniqueId());
        if (onResult != null) {
            onResult.onResult((Map)result);
        }
    }
```

最终通过从 mOnResults 获取到对应的 OnResult 并移除之（因为上一个页面已经关闭了），然后执行了onResult 方法。而这个 OnResult 就是之前打开页面的时候添加的。可以回头看一下上面 BoostMethodHandler.onMehodCall 方法 和FlutterViewContainerManager.openContainer 方法发现，在 openContainer 的时候把 onMehodCall 的一个匿名类 OnResult 给传了过来，并且添加到了 mOnResults 中，key 则是当前时间加当前类的 hash 值以确保唯一（当打开的时候添加，返回的时候移除）。这样以来通过 result.success(rlt) 就可以把结果回调给 flutter 层了。

```java
///BoostMethodHandler.onMethodCall 方法
    public void onMethodCall(MethodCall methodCall, final Result result) {
            FlutterViewContainerManager mManager = (FlutterViewContainerManager)FlutterBoost.instance().containerManager();
                    mManager.openContainer(url, params, resultData, new OnResult() {
                        public void onResult(Map<String, Object> rlt) {
                            if (result != null) {
                                result.success(rlt);  // 最终就是 回调的这里
                            }
                        }
                    });
                break;
            }
        }
    }

///FlutterViewContainerManager.openContainer 方法，
    void openContainer(String url, Map<String, Object> urlParams, Map<String, Object> exts, FlutterViewContainerManager.OnResult onResult) {

        IContainerRecord currentTopRecord = this.getCurrentTopRecord();
        if (onResult != null && currentTopRecord != null) {
            this.mOnResults.put(currentTopRecord.uniqueId(), onResult);
        }
    }
```