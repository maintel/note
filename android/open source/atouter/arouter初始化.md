
> 本篇主要介绍 ARouter 的初始化过程。

# 初始化

一般建议在应用打开时的初始化过程即在 application 中进行初始化工作。同时如果是在开发的情况下最好打开 log 和 debug 开关。

```kotlin
        if (BuildConfig.DEBUG) {
            ARouter.openLog()
            ARouter.openDebug()
        }
        ARouter.init(this)
```

ARouter.init(this) 是一个单例。它把初始化以及初始化后的工作都交给了 `_ARouter` 来做。

```java
    // class ARouter
    public static void init(Application application) {
        if (!hasInit) {
            logger = _ARouter.logger;
            hasInit = _ARouter.init(application);
            if (hasInit) {
                _ARouter.afterInit();
            }
        }
    }
    // class _ARouter
    protected static synchronized boolean init(Application application) {
        mContext = application;
        LogisticsCenter.init(mContext, executor);
        hasInit = true;
        mHandler = new Handler(Looper.getMainLooper());
        return true;
    }
```

在 `_ARouter.init` 把初始化工作交给了 `LogisticsCenter.init` 来做，同时自己初始化了一个 handler。

# LogisticsCenter.init

在 ARouter 中 `LogisticsCenter` 是一个很关键的类，几乎所有的工作最终都是由它来做。

其中 `init` 方法是扫描所有路由的映射关系，并将它们保存到内存中来。下面是它的部分关键代码：

```java
    public synchronized static void init(Context context, ThreadPoolExecutor tpe) throws HandlerException {
        try {
            ...
            if (registerByPlugin) { // 一般这里就是 false ，除非是使用 ARouter 提供的插件自动设置路由的。
                logger.info(TAG, "Load router map by arouter-auto-register plugin.");
            } else {
                Set<String> routerMap;

                // 如果是 debug 或者升级了新版本，则扫描路由
                // 这也是为什么我们要在开发状态下打开 debug 开关的原因
                if (ARouter.debuggable() || PackageUtils.isNewVersion(context)) {
                    // 1、扫描 dex 包，找出所有路由
                    routerMap = ClassUtils.getFileNameByPackageName(mContext, ROUTE_ROOT_PAKCAGE);
                    if (!routerMap.isEmpty()) {
                        // 缓存路由
                        context.getSharedPreferences(AROUTER_SP_CACHE_KEY, Context.MODE_PRIVATE).edit().putStringSet(AROUTER_SP_KEY_MAP, routerMap).apply();
                    }
                    // 保存版本
                    PackageUtils.updateVersion(context);  
                } else {
                    // 从缓存中读取
                    routerMap = new HashSet<>(context.getSharedPreferences(AROUTER_SP_CACHE_KEY, Context.MODE_PRIVATE).getStringSet(AROUTER_SP_KEY_MAP, new HashSet<String>()));
                }

                    //2、循环遍历加载路由或者拦截器以及 provider 信息
                for (String className : routerMap) {
            
                    if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_ROOT)) {
                        //com.alibaba.android.arouter.routes.ARouter.$$Root
                        // 将路由信息保存到内存中，
                        ((IRouteRoot) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.groupsIndex);
                    } else if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_INTERCEPTORS)) {
                        //com.alibaba.android.arouter.routes.ARouter.$$Interceptors
                        // 将拦截器保存到内存中
                        ((IInterceptorGroup) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.interceptorsIndex);
                    } else if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_PROVIDERS)) {
                        //com.alibaba.android.arouter.routes.ARouter.$$Providers
                        // 将 provider 保存到内存中
                        ((IProviderGroup) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.providersIndex);
                    }
                }
            }
        } catch (Exception e) {
            throw new HandlerException(TAG + "ARouter init logistics center exception! [" + e.getMessage() + "]");
        }
    }
```


上面代码可以看到主要有两个关键步骤：

- 扫描所有的路由
- 通过循环遍历加载路由或者拦截器以及 provider 信息

## 扫描理由表

ARouter 通过 `ClassUtils.getFileNameByPackageName(mContext, ROUTE_ROOT_PAKCAGE);` 方法来扫描路由信息，进入这个方法看一下：

```java
//packageName ===> com.alibaba.android.arouter.routes
//通过指定包名，扫描包下面包含的所有的ClassName
public static Set<String> getFileNameByPackageName(Context context, final String packageName) throws PackageManager.NameNotFoundException, IOException, InterruptedException {
        final Set<String> classNames = new HashSet<>();
        // 扫描所有 dex 包，获取所有包的路径
        List<String> paths = getSourcePaths(context);
        // 通过 CountDownLatch 来完成线程同步工作。
        //CountDownLatch 类似于计数器，在它结束之前会一直等待所有程序执行完
        final CountDownLatch parserCtl = new CountDownLatch(paths.size());

        for (final String path : paths) {
            // 通过线程池把扫描的工作放在子线程中执行
            DefaultPoolExecutor.getInstance().execute(new Runnable() {
                @Override
                public void run() {
                    DexFile dexfile = null;
                    try {
                        // 获取 dex 文件
                        if (path.endsWith(EXTRACTED_SUFFIX)) {
                            dexfile = DexFile.loadDex(path, path + ".tmp", 0);
                        } else {
                            dexfile = new DexFile(path);
                        }

                        Enumeration<String> dexEntries = dexfile.entries();
                        while (dexEntries.hasMoreElements()) {
                            String className = dexEntries.nextElement();
                            // 取到所有符合包名的类，并存放到一个集合中
                            if (className.startsWith(packageName)) {
                                classNames.add(className);
                            }
                        }
                    }
                    ...
                }
            });
        }
        ...
        return classNames;
    }
```

根据以上代码可以知道，它做的工作就是找到所有 dex 包，并从 dex 包中扫描出符合 arouter 包名的类，添加到集合当中并返回。

## 将扫描出来的路由信息保存到内存中

根据上面把所有 ARouter 的类扫描出来以后，就遍历这些类，并将必要的信息保存到内存中：

```java
    for (String className : routerMap) {     
        if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_ROOT)) {
            //com.alibaba.android.arouter.routes.ARouter.$$Root
            // 将路由信息保存到内存中，
            ((IRouteRoot) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.groupsIndex);
        } else if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_INTERCEPTORS)) {
            //com.alibaba.android.arouter.routes.ARouter.$$Interceptors
            // 将拦截器保存到内存中
            ((IInterceptorGroup) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.interceptorsIndex);
        } else if (className.startsWith(ROUTE_ROOT_PAKCAGE + DOT + SDK_NAME + SEPARATOR + SUFFIX_PROVIDERS)) {
            //com.alibaba.android.arouter.routes.ARouter.$$Providers
            // 将 provider 保存到内存中
            ((IProviderGroup) (Class.forName(className).getConstructor().newInstance())).loadInto(Warehouse.providersIndex);
        }
    }
```

根据上面的代码可以得知，通过循环便利找到了一些类，然后通过反射的方式调用了他们的 `loadInto` 方法，这些类分别是：

- com.alibaba.android.arouter.routes.ARouter.$$Root.xxx
- com.alibaba.android.arouter.routes.ARouter.$$Interceptors.xxx
- com.alibaba.android.arouter.routes.ARouter.$$Providers.xxx

以上那些类都是通过注解在编译过程中自动生成的，其中 xxx 是在 gradle 中配置的 module 名。这些类在工程编译完以后能在 `build/generated/source/apt 或 kapt/debug/包名/routes` 下找到。而他们的信息都保存到了 `Warehouse` 中，这个类里面都是一些静态的map，用以全局的维持路由信息。以主工程为例：

### ARouter.$$Root.xxx

`ARouter.$$Root` 的作用是将 组名—当前组路由表 保存到一个 map 中。

```java
public class ARouter$$Root$$app implements IRouteRoot {
  @Override
  public void loadInto(Map<String, Class<? extends IRouteGroup>> routes) {
    routes.put("test", ARouter$$Group$$test.class);
    routes.put("yourservicegroupname", ARouter$$Group$$yourservicegroupname.class);
  }
}
```
其中 `ARouter$$Group$$test` 等类的结构如下，他们保存了一组(test组)的所有路由映射信息：

```java
public class ARouter$$Group$$test implements IRouteGroup {
  @Override
  public void loadInto(Map<String, RouteMeta> atlas) {
    atlas.put("/test/activity1", RouteMeta.build(RouteType.ACTIVITY, Test1Activity.class, "/test/activity1", "test", new java.util.HashMap<String, Integer>(){{put("ser", 9); put("ch", 5); put("fl", 6); put("dou", 7); put("boy", 0); put("url", 8); put("pac", 10); put("obj", 11); put("name", 8); put("objList", 11); put("map", 11); put("age", 3); put("height", 3); }}, -1, -2147483648));
    atlas.put("/test/activity2", RouteMeta.build(RouteType.ACTIVITY, Test2Activity.class, "/test/activity2", "test", new java.util.HashMap<String, Integer>(){{put("key1", 8); }}, -1, -2147483648));
  }
}
```

> 其实在这里就能大概知道为什么说 ARouter 加载路由的时候是按组加载的。

### ARouter.$$Interceptors.xxx

`ARouter.$$Interceptors` 是直接将具体的拦截器类按照优先级为 key 保存到了内存中。

```java
public class ARouter$$Interceptors$$app implements IInterceptorGroup {
  @Override
  public void loadInto(Map<Integer, Class<? extends IInterceptor>> interceptors) {
    interceptors.put(7, Test1Interceptor.class);
  }
}
```

### ARouter.$$Providers.xxx

`ARouter.$$Providers` 是将一些服务类按照 类名——路由信息 的形式保存到内存中。

```java
public class ARouter$$Providers$$app implements IProviderGroup {
  @Override
  public void loadInto(Map<String, RouteMeta> providers) {
    providers.put("com.alibaba.android.arouter.facade.service.SerializationService", RouteMeta.build(RouteType.PROVIDER, JsonServiceImpl.class, "/yourservicegroupname/json", "yourservicegroupname", null, -1, -2147483648));
    providers.put("com.alibaba.android.arouter.demo.testservice.SingleService", RouteMeta.build(RouteType.PROVIDER, SingleService.class, "/yourservicegroupname/single", "yourservicegroupname", null, -1, -2147483648));
  }
}
```

至此，所有的必要的路由信息已经被加载到内存中了。

# 加载拦截器

而在 `_ARouter.init` 方法中，初始化以后它还调用了 `afterInit`方法，来完成初始化以后的工作。

```java
    if (hasInit) {
        _ARouter.afterInit();
    }

    static void afterInit() {
        // 触发拦截器的初始化
        interceptorService = (InterceptorService) ARouter.getInstance().build("/arouter/service/interceptor").navigation();
    }
```

根据以上代码可以知道 ARouter 在初始化以后，紧跟着通过路由的方式初始化了一个路由为 `/arouter/service/interceptor` 的拦截器，其实这个拦截器是 ARouter 官方实现的 `com.alibaba.android.arouter.core.InterceptorServiceImpl`，它的结构和我们自己实现的拦截器并无不同，所以这里主要看一下它的 `init` 方法：

```java
public class InterceptorServiceImpl implements InterceptorService {
    private static boolean interceptorHasInit;
    private static final Object interceptorInitLock = new Object();

    @Override
    public void init(final Context context) {
        // 初始化的过程放在了子线程中
        LogisticsCenter.executor.execute(new Runnable() {
            @Override
            public void run() {
                if (MapUtils.isNotEmpty(Warehouse.interceptorsIndex)) {
                    for (Map.Entry<Integer, Class<? extends IInterceptor>> entry : Warehouse.interceptorsIndex.entrySet()) {
                        Class<? extends IInterceptor> interceptorClass = entry.getValue();
                        try {
                            // 这里就是将上一步保存到 Warehouse.interceptorsIndex 中的拦截器拿出来并初始化
                            IInterceptor iInterceptor = interceptorClass.getConstructor().newInstance();
                            iInterceptor.init(context);
                            // 将初始化后的拦截器保存到  Warehouse.interceptors 中
                            Warehouse.interceptors.add(iInterceptor);
                        } catch (Exception ex) {
                        }
                    }
                    interceptorHasInit = true;
                    synchronized (interceptorInitLock) {
                        // 线程同步
                        interceptorInitLock.notifyAll();
                    }
                }
            }
        });
    }
}
```

可以看到 InterceptorServiceImpl 的工作也很简单，

- 将在初始化时保存到 Warehouse.interceptorsIndex 中的拦截器一一初始化，并保存到 Warehouse.interceptors 中。
- 同步线程（这里主要是因为它拦截器初始化过程是在子线程中，如果这时候拦截器被使用，则可能造成拦截器未被初始化的问题）

根据这里也可以知道，拦截器是在最开始的时候就被初始化了，而服务（provider）不是。

# 总结

至此，Arouter 的初始化成功全部结束，总结一下就是三步：

- 扫描所有 Dex 包找到相关的类
- 将路由相关的信息保存到内存当中
- 初始化拦截器

以上就是本篇的全部内容，希望对你有帮助。

---
*版权声明：本文为博主原创文章，转载请声明出处，请尊重别人的劳动成果，谢谢！*