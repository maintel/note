> 本篇内容主要分析一下 ARouter 的跳转过程——本篇只分析 Activity 的跳转过程。


# 跳转

ARouter 的简单跳转比如这样子 `ARouter.getInstance().build("/main/mainActivityTest").navigation()` 就实现了一个简单跳转，那么它的具体是怎么运作的呢，下面就一步一步来分析。

# 生成跳转信息

# build

在简单跳转的调用过程中，进入 build 方法:

```java
    public Postcard build(String path) {
        return _ARouter.getInstance().build(path);
    }
```
会发现，它实际上是把 build 操作给了 _ARouter 最终返回了一个 `Postcard`，`Postcard` 这个类是包含了本次跳转中所有的路由映射信息的类。

下面看一下它具体的 build 方法的实现：

```java
    protected Postcard build(String path) {
            ...
            return build(path, extractGroup(path));
    }

    protected Postcard build(String path, String group) {
        if (TextUtils.isEmpty(path) || TextUtils.isEmpty(group)) {
            throw new HandlerException(Consts.TAG + "Parameter is invalid!");
        } else {
            // 这里我们可以先忽略掉 ARouter 会查找我们是否实现了 URL 重写。这里可以先看做没有。
            PathReplaceService pService = ARouter.getInstance().navigation(PathReplaceService.class);
            if (null != pService) {
                path = pService.forString(path);
            }
            return new Postcard(path, group);
        }
    }
    // 如果是URI 略有不同
    protected Postcard build(Uri uri) {
            return new Postcard(uri.getPath(), extractGroup(uri.getPath()), uri, null);
    }
```

`extractGroup` 方法会自动从路径当中提取出组名。如果是 URI 的形式跳转的话，会把 Uri 一块传递进去。然后我们看一下 Postcard 具体内容：

## Postcard

```java
public final class Postcard extends RouteMeta {
    public Postcard(String path, String group) {
        this(path, group, null, null);
    }

    public Postcard(String path, String group, Uri uri, Bundle bundle) {
        setPath(path);
        setGroup(group);
        setUri(uri);
        this.mBundle = (null == bundle ? new Bundle() : bundle);
    }
}
```

可以看到它内容很简单，就是初始化了路径以及组 URI 信息，同时生成了一个  bundle 实例。

## 设置参数

我们知道 ARouter 的 api 提供了一系列的 `withxxx` 方法来供跳转时传递参数使用。而这些方法都是由 Postcard 提供的：

```java
    public Postcard withString(@Nullable String key, @Nullable String value) {
        mBundle.putString(key, value);
        return this;
    }

    ...

    public Postcard withObject(@Nullable String key, @Nullable Object value) {
        serializationService = ARouter.getInstance().navigation(SerializationService.class);
        mBundle.putString(key, serializationService.object2Json(value));
        return this;
    }
```

这些方法都很简单，就是把参数放在了构造时生成的 bundle 中，唯一不同的就是 withObject 方法，这个方法通过了一个序列化服务类来将传入的 object 进行序列化，所以在使用它的时候一定要实现这个服务。使用方法[参看这里](https://blog.csdn.net/u011494285/article/details/84570358#_URL__225)

# navigation 发起跳转

上面的步骤把跳转所需的信息都准备好了，然后就可以调用 navigation 方法进行跳转，

```java
    public Object navigation() {
        return navigation(null);
    }

    ...

    public Object navigation(Context mContext, Postcard postcard, int requestCode, NavigationCallback callback) {
        return _ARouter.getInstance().navigation(mContext, postcard, requestCode, callback);
    }

```

navigation 有一系列的重载:

- navigation()
- navigation(Context context)
- navigation(Context context, NavigationCallback callback)
- navigation(Activity mContext, int requestCode)
- navigation(Activity mContext, int requestCode, NavigationCallback callback)

这一系列的重载最终都调用了 `_ARouter.getInstance().navigation` 方法:

```java
    protected Object navigation(final Context context, final Postcard postcard, final int requestCode, final NavigationCallback callback) {
        try {
            // 核心方法 通过路由信息完善 Postcard
            LogisticsCenter.completion(postcard);
        } catch (NoRouteFoundException ex) {
            logger.warning(Consts.TAG, ex.getMessage());
            ...
            if (null != callback) {
                // 如果设置了跳转回调 则调用 onLost 方法
                callback.onLost(postcard);
            } else {
                // 如果没有设置回调，则查看是否有全局处理服务
                DegradeService degradeService = ARouter.getInstance().navigation(DegradeService.class);
                if (null != degradeService) {
                    degradeService.onLost(context, postcard);
                }
            }
            return null;
        }
        if (null != callback) {
            callback.onFound(postcard);// 回调 onFound
        }
        // 如果没有设置绿色通道则执行拦截器
        if (!postcard.isGreenChannel()) {  
            interceptorService.doInterceptions(postcard, new InterceptorCallback() {

                @Override
                public void onContinue(Postcard postcard) {
                    // 未被拦截 进行跳转
                    _navigation(context, postcard, requestCode, callback);
                }

                @Override
                public void onInterrupt(Throwable exception) {
                    if (null != callback) {
                        // 被拦截了，进行回调
                        callback.onInterrupt(postcard);
                    }
                }
            });
        } else {
            // 进行下一步的跳转
            return _navigation(context, postcard, requestCode, callback);
        }
        return null;
    }
```

上面的代码也很简单

- 首先完善了需要跳转的信息
- 进行一系列的回调
- 检查拦截器
- 进行下一步的跳转

## LogisticsCenter.completion(postcard)

LogisticsCenter 是 ARouter 的核心类，completion 方法通过缓存在内存中的路由信息来完善 postcard，因为在我们之前 build 方法只是给 postcard 设置了路径以及一些跳转携带的参数，这个时候我们还不知道这个路径具体映射到哪个 activity 或者其他什么类，所以需要在这里进行完善才能继续进行跳转。下面看一下它的代码：

```java
    public synchronized static void completion(Postcard postcard) {
        // 从路由缓存中根据路径来获取路由信息
        RouteMeta routeMeta = Warehouse.routes.get(postcard.getPath());
        if (null == routeMeta) {   
            // 如果没有获取到，则开始加载它
            // 先获取到它所在的组信息
            Class<? extends IRouteGroup> groupMeta = Warehouse.groupsIndex.get(postcard.getGroup());  // Load route meta.
            if (null == groupMeta) {
                throw new NoRouteFoundException(TAG + "There is no route match the path [" + postcard.getPath() + "], in group [" + postcard.getGroup() + "]");
            } else {
                try {
                    // 将一组路由信息缓存到内存——Warehouse.routes中，
                    //并将当前组信息从 Warehouse.groupsIndex 删除
                    // 这里体现了分组加载机制  —— ARouter$$Group$$xxx
                    IRouteGroup iGroupInstance = groupMeta.getConstructor().newInstance();
                    iGroupInstance.loadInto(Warehouse.routes);
                    Warehouse.groupsIndex.remove(postcard.getGroup());
                } catch (Exception e) {
                    throw new HandlerException(TAG + "Fatal exception when loading group meta. [" + e.getMessage() + "]");
                }
                // 重新调用，此时缓存中的路由信息已经不为空了
                completion(postcard);   
            }
        } else {
            // 如果找到了 则设置信息
            postcard.setDestination(routeMeta.getDestination());
            postcard.setType(routeMeta.getType());
            postcard.setPriority(routeMeta.getPriority());
            postcard.setExtra(routeMeta.getExtra());

            Uri rawUri = postcard.getUri();
            if (null != rawUri) {
                /*
                这一部分代码很好的解释了，为什么说在使用 URI 跳转时，即使不需要依赖注入
                也需要加入 @Autowired 注解的原因。
                */
                Map<String, String> resultMap = TextUtils.splitQueryParameters(rawUri);
                // 获取需要依赖注入的字段
                Map<String, Integer> paramsType = routeMeta.getParamsType();

                if (MapUtils.isNotEmpty(paramsType)) {
                    //如果是 uri的形式，则解析 uri 中的参数，并重新设置参数
                    for (Map.Entry<String, Integer> params : paramsType.entrySet()) {
                        setValue(postcard,
                                params.getValue(),
                                params.getKey(),
                                resultMap.get(params.getKey()));
                    }
                    // 将需要自动注入的参数名保存下来
                    postcard.getExtras().putStringArray(ARouter.AUTO_INJECT, paramsType.keySet().toArray(new String[]{}));
                }
                postcard.withString(ARouter.RAW_URI, rawUri.toString());
            }

            switch (routeMeta.getType()) {
                case PROVIDER:
                    ...
                    postcard.greenChannel();    // 如果是 provider 则设置绿色通道
                    break;
                case FRAGMENT:
                    postcard.greenChannel();    // 如果是 fragment 则设置绿色通道
                default:
                    break;
            }
        }
    }
```

上面的代码注释已经写得很清楚，不过 activity 跳转，任何 ARouter 中通过路径来 navigation 方法的功能都需要经由此方法。主要有三个：

- 将一组路由信息缓存到 Warehouse.routes 中
- 完善 postcard 的信息
- 如果是URI跳转，则设置参数

## 执行拦截器

在完善完路由信息以后，ARouter 会检测是否设置了绿色通道，如果没有设置绿色通道则会触发拦截器。`interceptorService` 在[初始化过程分析](https://blog.csdn.net/u011494285/article/details/84592885)中有提到过，在初始化完成以后会执行拦截器的初始化。这里就触发了拦截器：

```java
    @Override
    public void doInterceptions(final Postcard postcard, final InterceptorCallback callback) {
        // 首先检查是否设置了自定义的拦截器
        if (null != Warehouse.interceptors && Warehouse.interceptors.size() > 0) {
            // 检查拦截器是否初始化成功
            checkInterceptorsInitStatus();
            // 如果不成功则拦截掉
            if (!interceptorHasInit) {
                callback.onInterrupt(new HandlerException("Interceptors initialization takes too much time."));
                return;
            }
            // 将拦截的工作放在子线程中执行
            LogisticsCenter.executor.execute(new Runnable() {
                @Override
                public void run() {
                    CancelableCountDownLatch interceptorCounter = new CancelableCountDownLatch(Warehouse.interceptors.size());
                    try {
                        // 循环遍历拦截器来处理本次跳转
                        _excute(0, interceptorCounter, postcard);
                        interceptorCounter.await(postcard.getTimeout(), TimeUnit.SECONDS);
                        if (interceptorCounter.getCount() > 0) {  
                            // 如果超时 则把这次跳转拦截掉
                            callback.onInterrupt(new HandlerException("The interceptor processing timed out."));
                        } else if (null != postcard.getTag()) {
                            // 如果 tag 不为空也拦截掉
                            callback.onInterrupt(new HandlerException(postcard.getTag().toString()));
                        } else {
                            // 不拦截
                            callback.onContinue(postcard);
                        }
                    } catch (Exception e) {
                        callback.onInterrupt(e);
                    }
                }
            });
        } else {
            callback.onContinue(postcard);// 不拦截
        }
    }
```

`interceptorService` 主要就是检测了是否设置了拦截器，如果没有设置拦截器则直接执行了 `onContinue` 方法，如果设置了拦截器，则在一个线程池中调用 `_excute` 方法来循环触发拦截器，这个方法如下，它根据优先级来进行了一次递归循环调用了设置的拦截器：

```java
    private static void _excute(final int index, final CancelableCountDownLatch counter, final Postcard postcard) {
        if (index < Warehouse.interceptors.size()) {
            IInterceptor iInterceptor = Warehouse.interceptors.get(index);
            iInterceptor.process(postcard, new InterceptorCallback() {
                @Override
                public void onContinue(Postcard postcard) {
                    counter.countDown();
                    // 递归调用
                    _excute(index + 1, counter, postcard);  // When counter is down, it will be 
                }

                @Override
                public void onInterrupt(Throwable exception) {
                    // 给它设置一个拦截掉的tag
                    postcard.setTag(null == exception ? new HandlerException("No message.") : exception.getMessage());    // save the exception message for backup.
                    // 停止计数
                    counter.cancel();
                }
            });
        }
    }
```

# 执行跳转

经过拦截器的过滤，那么就要进行真正的跳转了，上面分析可以看到它最终调用了 `_navigation` 方法。

```java
   private Object _navigation(final Context context, final Postcard postcard, final int requestCode, final NavigationCallback callback) {
        final Context currentContext = null == context ? mContext : context;
        switch (postcard.getType()) {
            case ACTIVITY:
                // 创建 intent
                final Intent intent = new Intent(currentContext, postcard.getDestination());
                intent.putExtras(postcard.getExtras());
                // 设置 flag
                // 设置 action
                ...
                // 放在主线程中执行
                runInMainThread(new Runnable() {
                    @Override
                    public void run() {
                        startActivity(requestCode, currentContext, intent, postcard, callback);
                    }
                });

                break;
            case BOARDCAST:
            case CONTENT_PROVIDER:
            case FRAGMENT:
            // 创建了 fragment 等的实例并返回
                Class fragmentMeta = postcard.getDestination();
                try {
                    Object instance = fragmentMeta.getConstructor().newInstance();
                    if (instance instanceof Fragment) {
                        ((Fragment) instance).setArguments(postcard.getExtras());
                    } else if (instance instanceof android.support.v4.app.Fragment) {
                        ((android.support.v4.app.Fragment) instance).setArguments(postcard.getExtras());
                    }

                    return instance;
                } catch (Exception ex) {
                    logger.error(Consts.TAG, "Fetch fragment instance error, " + TextUtils.formatStackTrace(ex.getStackTrace()));
                }
        }

        return null;
    }
```
`_navigation` 方法对各种类型进行了判断，如果是 activity 的话就组装了 intent，并在调用了 startActivity 方法。
```java
    private void startActivity(int requestCode, Context currentContext, Intent intent, Postcard postcard, NavigationCallback callback) {
        // 调用 startActivity
        if (requestCode >= 0) {  // 根据是否设置了 requestCode 来判断需要调用的方法
            if (currentContext instanceof Activity) {
                ActivityCompat.startActivityForResult((Activity) currentContext, intent, requestCode, postcard.getOptionsBundle());
            } else {
                logger.warning(Consts.TAG, "Must use [navigation(activity, ...)] to support [startActivityForResult]");
            }
        } else {
            ActivityCompat.startActivity(currentContext, intent, postcard.getOptionsBundle());
        }

        // 设置动画
        if ((-1 != postcard.getEnterAnim() && -1 != postcard.getExitAnim()) && currentContext instanceof Activity) {    // Old version.
            ((Activity) currentContext).overridePendingTransition(postcard.getEnterAnim(), postcard.getExitAnim());
        }
        // 回调
        if (null != callback) { // Navigation over.
            callback.onArrival(postcard);
        }
    }
```

在这里我们终于看到了熟悉的 `startActivity` 方法，至此一次完整的 activity 跳转完成。

# 总结

经过上面的分析，一次 activity 跳转的过程已经很清晰了，总结一下可以分为下面几步：

- 通过 build 生成跳转信息
- LogisticsCenter.completion(postcard) 方法对跳转信息进行完善，找到最终要跳转的目标
- 检查拦截器，并判断是否需要进行拦截
- 完成跳转

其实分析过程中不难发现，一些其他的功能比如服务的生成，fragment，广播等的生成的过程和 activity 的跳转几乎是一样的。

以上就是本篇的全部内容，希望对你有帮助。

---
*版权声明：本文为博主原创文章，转载请声明出处，请尊重别人的劳动成果，谢谢！*