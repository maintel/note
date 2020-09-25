参考这一篇博客 https://www.jianshu.com/p/4d5e712594b4

https://www.didierboelens.com/2018/08/reactive-programming-streams-bloc/

关于 bloc 上面的博客讲的很清楚，基本原理就是基于 stream 来实现数据响应式的架构，实现组件之间的隔离。

关于 stream 这里有一篇博客讲的也比较清楚 https://www.jianshu.com/p/b7cca3a89618?utm_source=desktop&utm_medium=timeline

实际上 stream 并不是 flutter 中特有的，而是 dart 中自带的逻辑。基于事件流驱动设计代码，然后监听订阅事件，并针对事件变换处理响应

接下来分析一下，flutter 推荐的 bloc 框架是到底是如何通过 stream 来实现数据的更新的。

# 业务中使用

其实关于 bloc 的代码设计上面的博客已经有一些说明了，下面是实际项目中用到的一个 bloc 的设计。

有两个关键的类 `BlocProvider`,`BaseBloc`

BaseBloc 是业务中用到的 bloc 的基类，内部用 PublishSubject 来实现对流的控制，

```dart

abstract class BlocLife {
  void dispose();
}

abstract class BaseBloc<T> implements BlocLife {

  T data;

  StreamController<T> _controller;
  // 结合 rxDart 来实现更便捷的数据更新监听
  // 发送数据更新
  StreamSink<T> get inputStream => _controller.sink;

  // 通知数据更新
  Stream<T> get resultData => _controller.stream;

  T createData();

  BaseBloc() {
    data = createData();
    // 类似于rxJava 的事件队列，PublishSubject 是 StreamController 的扩展
    _controller = PublishSubject<T>();
  }

  void dispose() {
    _controller?.close();
  }

}
```


BlocProvider, 作用用来管理状态的根布局，可以通过 of 函数来获取业务中实际用到的 bloc 对象。其实这里不是最好的实现，因为 findAncestorWidgetOfExactType 的时间复杂度是 O(N) 效率不够高。

```dart
class BlocProvider<T extends BlocLife> extends StatefulWidget {
  BlocProvider({
    Key key,
    @required this.child,
    @required this.bloc,
  }): super(key: key);

  final T bloc;
  final Widget child;

  @override
  _BlocProviderState<T> createState() => _BlocProviderState<T>();

  static T of<T extends BlocLife>(BuildContext context){
    BlocProvider<T> provider = context.findAncestorWidgetOfExactType();
    return provider.bloc;
  }
}

class _BlocProviderState<T> extends State<BlocProvider<BlocLife>>{
  @override
  void dispose(){
    widget.bloc.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context){
    return widget.child;
  }
}
```

使用的时候：

```dart
  XXXXListBloc _bloc;


  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    init(context);
  }

  void init(BuildContext context) {
    _bloc = BlocProvider.of<XXXXListBloc>(context);
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<XXXXListData>(
        stream: _bloc?.resultData,
        initialData: _bloc?.data,
        builder:
            (BuildContext context, AsyncSnapshot<XXXXListData> snapshot) {
                // 布局
          return _buildWidget(context, snapshot.data);
        });
  }
```

```dart
class XXXXListBloc extends BaseBloc<XXXXListData> {
    fun getData(){
        // 更新数据
        inputStream?.add(data);
    }
}
```

上面使用 StreamBuilder 构建布局，建议均使用这种方法来构建，因为 StreamBuilder 内部会管理订阅以及取消订阅事件。

# StreamBuilder

StreamBuilder 是 flutter 官方提供的用来结合 stream 构建布局的小部件，它集成自 StreamBuilderBase，实际的一些逻辑也都在 StreamBuilderBase 中。源码也很简单，即是使用 builder 做了一层包裹，然后再内部实现了 stream 的订阅，更新，取消订阅等管理。

```dart
abstract class StreamBuilderBase<T, S> extends StatefulWidget {
    const StreamBuilderBase({ Key key, this.stream }) : super(key: key);
    final Stream<T> stream;
      @override
  State<StreamBuilderBase<T, S>> createState() => _StreamBuilderBaseState<T, S>();
}

class _StreamBuilderBaseState<T, S> extends State<StreamBuilderBase<T, S>> {
  StreamSubscription<T> _subscription;
  S _summary;

  @override
  void initState() {
    super.initState();
    _summary = widget.initial();
    _subscribe();
  }

  @override
  void didUpdateWidget(StreamBuilderBase<T, S> oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.stream != widget.stream) {
      if (_subscription != null) {
        _unsubscribe();
        _summary = widget.afterDisconnected(_summary);
      }
      _subscribe();
    }
  }

  @override
  Widget build(BuildContext context) => widget.build(context, _summary);

  @override
  void dispose() {
    _unsubscribe();
    super.dispose();
  }

// 订阅事件，接收广播，然后通过 setState 来更新
  void _subscribe() {
    if (widget.stream != null) {
      _subscription = widget.stream.listen((T data) {
        setState(() {
          _summary = widget.afterData(_summary, data);
        });
      }, onError: (Object error) {
        setState(() {
          _summary = widget.afterError(_summary, error);
        });
      }, onDone: () {
        setState(() {
          _summary = widget.afterDone(_summary);
        });
      });
      _summary = widget.afterConnected(_summary);
    }
  }

// 取消订阅
  void _unsubscribe() {
    if (_subscription != null) {
      _subscription.cancel();
      _subscription = null;
    }
  }
}
```

# PublishSubject

关于 stream 的原理 [这里](https://www.jianshu.com/p/b7cca3a89618?utm_source=desktop&utm_medium=timeline) 讲的比较清楚。



inputStream?.add(data);

_controller.sink.add(data)

PublishSubject.sink.add(data)

_StreamSinkWrapper.sink.add(data)

Subject.add(data)

Subject.controller.add(data)

_AsyncBroadcastStreamController.add(data) ==> _BroadcastStreamController.add(data)

_AsyncBroadcastStreamController._sendData(data)

```dart
  void _sendData(T data) {
    for (_BroadcastSubscription<T> subscription = _firstSubscription;
        subscription != null;
        subscription = subscription._next) {
      subscription._addPending(new _DelayedData<T>(data));
    }
  }
```

_BroadcastSubscription._addPending(new _DelayedData<T>(data))

(_BroadcastSubscription 是 _BufferingStreamSubscription 的子类最终调用 _BufferingStreamSubscription._addPending)

```dart
  void _addPending(_DelayedEvent event) {
    _StreamImplEvents<T> pending = _pending;
    if (_pending == null) {
      pending = _pending = new _StreamImplEvents<T>();
    }
    //这里调用了 _StreamImplEvents.add
    pending.add(event);
    if (!_hasPending) {
      _state |= _STATE_HAS_PENDING;
      if (!_isPaused) {
        _pending.schedule(this);
      }
    }
  }
```

_StreamImplEvents.schedule(this);  this ==> _BufferingStreamSubscription/_BroadcastSubscription
(_StreamImplEvents 是 _PendingEvents 的子类，最终调用 _PendingEvents.schedule)

```dart

  void schedule(_EventDispatch<T> dispatch) {
    if (isScheduled) return;
    assert(!isEmpty);
    if (_eventScheduled) {
      assert(_state == _STATE_CANCELED);
      _state = _STATE_SCHEDULED;
      return;
    }
    /// 这就需要说到 Dart 中的异步实现逻辑了，因为 Dart 是 单线程应用 ，和大多数单线程应用一样，
    /// Dart 是以 消息循环机制 来运行的，而这里面主要包含两个任务队列，
    /// 一个是 microtask 内部队列，一个是 event 外部队列，而 microtask 的优先级又高于 event 。
    scheduleMicrotask(() {
      int oldState = _state;
      _state = _STATE_UNSCHEDULED;
      if (oldState == _STATE_CANCELED) return;
      handleNext(dispatch);
    });
    _state = _STATE_SCHEDULED;
  }
```

_StreamImplEvents.handleNext(_EventDispatch<T> dispatch)

```dart

// _BroadcastSubscription._addPending 时添加了一个 event（_DelayedData）
  void add(_DelayedEvent event) {
    if (lastPendingEvent == null) {
      firstPendingEvent = lastPendingEvent = event;
    } else {
      lastPendingEvent = lastPendingEvent.next = event;
    }
  }

  void handleNext(_EventDispatch<T> dispatch) {
    assert(!isScheduled);
    _DelayedEvent event = firstPendingEvent;
    firstPendingEvent = event.next;
    if (firstPendingEvent == null) {
      lastPendingEvent = null;
    }
    event.perform(dispatch);
  }
```

_DelayedData.perform(_EventDispatch<T> dispatch)

```dart
// 可以看出这里 value 一开始就传过来了
  final T value;
  _DelayedData(this.value);
  void perform(_EventDispatch<T> dispatch) {
    dispatch._sendData(value);
  }
```

这个 dispatch 即是  _BufferingStreamSubscription/_BroadcastSubscription ，之前 _StreamImplEvents.schedule(this);  传递过来的，所以最终调用的是 _BufferingStreamSubscription._sendData(value)

```dart
  void _sendData(T data) {
    assert(!_isCanceled);
    assert(!_isPaused);
    assert(!_inCallback);
    bool wasInputPaused = _isInputPaused;
    _state |= _STATE_IN_CALLBACK;
    _zone.runUnaryGuarded(_onData, data);
    _state &= ~_STATE_IN_CALLBACK;
    _checkState(wasInputPaused);
  }
```

这里就触发了 _zone.runUnaryGuarded(_onData, data); 回调方法，






















