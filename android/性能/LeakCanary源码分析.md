基于 leakCanary 1.6.1 版本。

程序入口 LeakCanary.install(this);

```java
  public static RefWatcher install(Application application) {
    return refWatcher(application).listenerServiceClass(DisplayLeakService.class)
        .excludedRefs(AndroidExcludedRefs.createAppDefaults().build())
        .buildAndInstall();
  }
```

首先创建了一个 AndroidRefWatcherBuilder 对象，然后设置了接受解析结果的监听 DisplayLeakService，设置白名单以排除 android sdk 底层的一些内存泄漏，然后调用 buildAndInstall 方法初始化并安装监视器。

# buildAndInstall

```java
  public RefWatcher buildAndInstall() {
    if (LeakCanaryInternals.installedRefWatcher != null) {
      throw new UnsupportedOperationException("buildAndInstall() should only be called once.");
    }
    RefWatcher refWatcher = build();  // 创建 refwathcer 对象
    if (refWatcher != DISABLED) { //如果不是在主进程中 就不进行接下来的操作。
      if (watchActivities) {
        ActivityRefWatcher.install(context, refWatcher); // 设置 activity 内存泄漏监听
      }
      if (watchFragments) {
        FragmentRefWatcher.Helper.install(context, refWatcher);
      }
    }
    LeakCanaryInternals.installedRefWatcher = refWatcher;
    return refWatcher;
  }
```
##　build

```java
/** Creates a {@link RefWatcher}. */
  public final RefWatcher build() {
    if (isDisabled()) {  // 判断进程
      return RefWatcher.DISABLED;
    }

    if (heapDumpBuilder.excludedRefs == null) {  // 白名单
      heapDumpBuilder.excludedRefs(defaultExcludedRefs());
    }

    HeapDump.Listener heapDumpListener = this.heapDumpListener; // 堆内存收集完成后的监听器 ServiceHeapDumpListener
    if (heapDumpListener == null) {
      heapDumpListener = defaultHeapDumpListener();
    }

    DebuggerControl debuggerControl = this.debuggerControl; // debug 控制中心
    if (debuggerControl == null) {
      debuggerControl = defaultDebuggerControl();
    }

    HeapDumper heapDumper = this.heapDumper; // 用于创建 .hprof 文件，存储 heap 堆快照
    if (heapDumper == null) {
      heapDumper = defaultHeapDumper();
    }

    // AndroidWatchExecutor，确保分析任务是在主线程执行的，同时默认延迟5秒执行分析任务，留时间给系统GC
    WatchExecutor watchExecutor = this.watchExecutor;
    if (watchExecutor == null) {
      watchExecutor = defaultWatchExecutor();
    }

    GcTrigger gcTrigger = this.gcTrigger;  //内部调用Runtime.getRuntime().gc()，手动触发系统GC
    if (gcTrigger == null) {
      gcTrigger = defaultGcTrigger();
    }

    if (heapDumpBuilder.reachabilityInspectorClasses == null) {
        //用于要进行可达性检测的类的列表  androidRefWatcherBuilder 对他进行了重写。
        //具体看AndroidRefWatcherBuilder.defaultReachabilityInspectorClasses
      heapDumpBuilder.reachabilityInspectorClasses(defaultReachabilityInspectorClasses());
    }

    return new RefWatcher(watchExecutor, debuggerControl, gcTrigger, heapDumper, heapDumpListener,
        heapDumpBuilder);
  }
```

refWatcherBuilder.build 方法，先检测了当前的进程是否和 HeapAnalyzerService 在同一个进程，如果是就直接返回。

然后判断是否设置了白名单，这一步已经在初始化的时候设置过了。

然后设置堆内存收集的监听器，这一步也在初始化的时候设置了。（ServiceHeapDumpListener）用来当发生内存泄漏后回调并启动新的进程执行内存分析。

然后设置 debug 控制器。主要是用来后续分析时如果是debug就不进行内存分析。

设置 堆内存收集器 ，（AndroidHeapDumper）生成堆内存快照。

然后设置 监视执行器，AndroidWatchExecutor，它确保GC，及收集内存是在主线程执行的，同时默认延迟5秒执行分析任务，留时间给系统GC。

设置 GcTrigger，使用默认的设置，内部调用Runtime.getRuntime().gc()，手动触发系统GC。

设置 可达性检测器。AndroidReachabilityInspectors，它主要是根据以往的开发经验，然后确定一些类的可达性的预期。比如 activity 的mDestroyed 如果为 true，则预期应当是不可达的。

最后返回一个 RefWatcher 对象。

## ActivityRefWatcher.install

然后安装 监视器，主要是给 application 添加一个activity生命周期的监听，然后在 onactivityDestroyed 方法中触发 refwatcher.watch。

```java
application.registerActivityLifecycleCallbacks(activityRefWatcher.lifecycleCallbacks);

  private final Application.ActivityLifecycleCallbacks lifecycleCallbacks =
      new ActivityLifecycleCallbacksAdapter() {
        @Override public void onActivityDestroyed(Activity activity) {
          //当 activity destroyed 的时候 被回调
          refWatcher.watch(activity);
        }
      };
```


# refWatcher


## watch

```java
    public void watch(Object watchedReference, String referenceName) {
        if (this == DISABLED) {
            return;
        }
        checkNotNull(watchedReference, "watchedReference");
        checkNotNull(referenceName, "referenceName");
        final long watchStartNanoTime = System.nanoTime();
        String key = UUID.randomUUID().toString();
        // 声明一个弱引用 随机数作为key，name=“”， 观测的对象就是 应该被销毁的 activity
        retainedKeys.add(key);
        final KeyedWeakReference reference =
                new KeyedWeakReference(watchedReference, key, referenceName, queue);

        ensureGoneAsync(watchStartNanoTime, reference);
    }
```

声明一个弱引用 随机数作为key，name=“”， 观测的对象就是 应该被销毁的 activity，并且把当前的key 放在 retainedKeys 列表中。然后调用 ensureGoneAsync 方法，

## ensureGoneAsync

ensureGoneAsync 方法经过一系列的回调，最终调用了 ensureGone 方法。

```java
Retryable.Result ensureGone(final KeyedWeakReference reference, final long watchStartNanoTime) {
        long gcStartNanoTime = System.nanoTime();
        long watchDurationMs = NANOSECONDS.toMillis(gcStartNanoTime - watchStartNanoTime); //监视持续时间 当前时间 - 等待开始的时间

        removeWeaklyReachableReferences(); // 先过滤一遍弱引用队列

//        if (debuggerControl.isDebuggerAttached()) {  // 如果是调试过程中，就等待
//            // The debugger can create false leaks.
//            return RETRY;
//        }
        if (gone(reference)) {  // 确定是否被回收
            return DONE;
        }
        gcTrigger.runGc(); //如果还是没有被回收 手动执行 gc
        removeWeaklyReachableReferences(); // 再过滤一遍弱引用队列
        if (!gone(reference)) { // 再确定一下是否被回收
            long startDumpHeap = System.nanoTime();
            long gcDurationMs = NANOSECONDS.toMillis(startDumpHeap - gcStartNanoTime);

            File heapDumpFile = heapDumper.dumpHeap();  // 生成 .hprof 文件
            if (heapDumpFile == RETRY_LATER) {
                // Could not dump the heap.
                return RETRY;
            }
            long heapDumpDurationMs = NANOSECONDS.toMillis(System.nanoTime() - startDumpHeap); // 生成堆内存文件使用的时间

            HeapDump heapDump = heapDumpBuilder
                    .heapDumpFile(heapDumpFile)   // 堆内存文件
                    .referenceKey(reference.key)  //弱引用的 key
                    .referenceName(reference.name)  // 弱引用对象名称
                    .watchDurationMs(watchDurationMs)  // 监视持续时间
                    .gcDurationMs(gcDurationMs)   // 主动GC使用的时间
                    .heapDumpDurationMs(heapDumpDurationMs) //生成堆内存文件使用的时间
                    .build();
            // 分析 heap 快照 ===>ServiceHeapDumpListener
            // 最终是在 HeapAnalyzerService 服务中完成，它在一个新的进程中
            heapdumpListener.analyze(heapDump);
        }
        return DONE;
    }
```

它先调用了 removeWeaklyReachableReferences 方法来过滤一遍弱引用队列，

```java
    private void removeWeaklyReachableReferences() {
        KeyedWeakReference ref;
        // 根据 java 垃圾回收器的原理，在被弱引用的对象被回收后 会把弱引用的对象放到队列中，所以，这里可以通过判断
        // 弱引用对象是否为空来确定被弱引用对象是否被回收
        // 如果被若应用的对象已经被回收，就从待检测的队列中把 key 移除掉
        while ((ref = (KeyedWeakReference) queue.poll()) != null) {
            retainedKeys.remove(ref.key);
        }
    }
```

然后确定是否被回收，如果还没有被回收，就手动 gc，然后再过滤一遍弱引用，然后再确定是否被回收，如果还没有被回收，则表示存在内存泄漏。

这个时候调用 AndroidHeapDumper.dumpHeap 方法来生成堆内存镜像文件。（它主要是通过 Debug.dumpHprofData(heapDumpFile.getAbsolutePath()); 方法来完成的）

然后生成了一个 heapDump 对象，接着调用 ServiceHeapDumpListener.analyze ,经过一系列的调用最终调用了 HeapAnalyzerService.runAnalysis 方法。

## HeapAnalyzerService

```java
  @Override protected void onHandleIntentInForeground(@Nullable Intent intent) {
    if (intent == null) {
      CanaryLog.d("HeapAnalyzerService received a null intent, ignoring.");
      return;
    }
    String listenerClassName = intent.getStringExtra(LISTENER_CLASS_EXTRA);
    HeapDump heapDump = (HeapDump) intent.getSerializableExtra(HEAPDUMP_EXTRA);

    // 声明一个堆内存分析器
    HeapAnalyzer heapAnalyzer =
        new HeapAnalyzer(heapDump.excludedRefs, this, heapDump.reachabilityInspectorClasses);
    // 分析内存泄漏
    AnalysisResult result = heapAnalyzer.checkForLeak(heapDump.heapDumpFile, heapDump.referenceKey,
        heapDump.computeRetainedHeapSize);
    //    // 回调分析的结果
    AbstractAnalysisResultService.sendResultToListener(this, listenerClassName, heapDump, result);
  }
```
HeapAnalyzerService 的 runAnalysis 启动了 HeapAnalyzerService，然后在他的onHandleIntentInForeground 方法中生成了一个 HeapAnalyzer 对象，然后调用它的 checkForLeak 方法来分析内存并返回一个 AnalysisResult 对象，然后通过 AbstractAnalysisResultService.sendResultToListener 来发送内存分析的结果，在 sendResultToListener 方法中通过反射启动了最初设置的 DisplayLeakService 服务,并调用了 onHeapAnalyzed 方法，这个方法发送了一个通知，并根据需求存储堆内存镜像文件。

##　HeapAnalyzer．checkForLeak

```java
  public AnalysisResult checkForLeak(File heapDumpFile, String referenceKey,
      boolean computeRetainedSize) {
    long analysisStartNanoTime = System.nanoTime();

    if (!heapDumpFile.exists()) {
      Exception exception = new IllegalArgumentException("File does not exist: " + heapDumpFile);
      return failure(exception, since(analysisStartNanoTime));
    }

    try {
      listener.onProgressUpdate(READING_HEAP_DUMP_FILE);
      // 下面的步骤使用了 haha 库中的功能
      //1.构建内存映射的 HprofBuffer，针对大文件的一种快速的读取方式，
      // 其原理是将文件流的通道与  ByteBuffer 建立起关联，并只在真正发生读取时才从磁盘读取内容出来。
      HprofBuffer buffer = new MemoryMappedFileBuffer(heapDumpFile);
      //2.构造 Hprof 解析器
      HprofParser parser = new HprofParser(buffer);
      listener.onProgressUpdate(PARSING_HEAP_DUMP);
      //3.获取快照
      Snapshot snapshot = parser.parse();
      listener.onProgressUpdate(DEDUPLICATING_GC_ROOTS);
      //4.去重 gcRoots
      deduplicateGcRoots(snapshot);
      listener.onProgressUpdate(FINDING_LEAKING_REF);
      //5.找出导致内存泄露的对象
      Instance leakingRef = findLeakingReference(referenceKey, snapshot);

      // False alarm, weak reference was cleared in between key check and heap dump.
      if (leakingRef == null) {
        return noLeak(since(analysisStartNanoTime));
      }
      //6.找到最强引用，并作为结果返回
      return findLeakTrace(analysisStartNanoTime, snapshot, leakingRef, computeRetainedSize);
    } catch (Throwable e) {
      return failure(e, since(analysisStartNanoTime));
    }
  }
```







