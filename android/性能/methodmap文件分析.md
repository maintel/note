#　map 文件

map 文件编译后生成 build/matrix_output/Debug.methodmap

```
8,17,com.yiqizuoye.jzt.activity.hkdynamic.adapter.ParentHwAdapter setMContext (Landroid.content.Context;)V
```
所以上面的那个方法就是

|:---|:---|
|-----|----
|编号|8
|(意义不明)|17
|类名|com.yiqizuoye.jzt.activity.hkdynamic.adapter.ParentHwAdapter
|方法名|setMContext
|参数|android.content.Context
|方法类型|void



# 输出堆栈

- type:类型，用于区分同一个tag不同类型的上报
- tag: 该上报对应的tag
- stack:该上报对应的堆栈
- process:该上报对应的进程名
- time:issue 发生的时间
- tag: Trace_EvilMethod
- detail:具体的耗时场景
    - NORMAL, 普通慢函数场景
    - ENTER, Activity进入场景
    - ANR, anr超时场景
    - FULL, 满buffer场景 e. STARTUP, 启动耗时场景
- cost: 耗时
- stack: 堆栈
- stackKey: 客户端提取的 key，用来标识 issue 的唯一性

## stack 堆栈分析

下面是一段输出

```
0,98,1,502\n1,329,1,502\n2,330,1,205\n3,331,1,103\n2,330,1,199\n3,331,1,97\n
```

每个换行中从左向右分别是 深度-方法编号-暂时意义未明-方法耗时

做成可视化大概是下面这这样子

```
    98 1 502
    .329 1 502
    ..330 1 205
    ...331 1 103
    ..330 1 199
    ...331 1 97
```


下面就可以写一个解析工具类解析这些堆栈


