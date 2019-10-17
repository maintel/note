版本 0.4.10

不支持 kotlin
不支持 aar 内的方法插桩
不支持 jar 包内的方法插桩

查看是否插桩成功可以在 build/matrix_output 中查看。

编译后生成的 class 文件在 build/matrix_output/classes/MatrixTraceTransform/classes/包名 下

kotlin 的是在 build/matrix_output/classes/MatrixTraceTransform/debug 下（然而并没有什么卵用）

目前集成进以后慢方法未能收集，原因未知 正在解决

EvilMethodTracer 用来对方法执行耗时的收集

- 首先解决第一个问题 EvilMethodTracer 的 hasEntered 为 false 的问题，

经过 debug 发现在初始化的时候未执行 onActivityEntered 方法，onActivityEntered 是将 hasEntered 设置为 true 的关键，他是 IMethodBeatListener 中的方法，会在 MethodBeat.at 方法中被调用。

经过 debug 发现初始化的时候 MethodBeat.at 方法会在 onWindowFocusChanged 方法中被调用————这里是在代码编译器被加入到这个方法中的，现在**问题**是为什么在编译过程中未自动生成此方法。（）

通过手动重写 onWindowFocusChanged 方法，然后手动调用 at 方法解决此问题。

# 原理

通过监控 Choreographer 模块，实现 FrameCallback 回调，最终调用了 EvilMethodTracer.doFrame 方法，在此方法中会判断是否超过了阈值，如果超过就调用 handleBuffer 方法，然后通过一个 AnalyseTask 来组装异常信息，最终调用 sendReport 方法来触发 Plugin.onDetectIssue 方法，这个方法会调用 pluginListener.onReportIssue(issue) 方法，pluginListener 就是在初始化的时候给设置的监听。

不知道为什么解决了上面的问题后此方法不能被回调。 doFrame 方法其实是由系统的回调来触发的。


阈值可以通过 实现 IDynamicConfig 接口，然后实现 get(String key, long defLong) 方法，重写

```java
        if (MatrixEnum.clicfg_matrix_trace_evil_method_threshold.name().equals(key)) {
            return 100L;
        }
```

来实现，注意单位是 毫秒值。（如果设置的太低了好像不可以，此处存疑）


# 堆栈信息的解析??