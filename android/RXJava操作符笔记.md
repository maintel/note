# RXJava 操作符使用笔记

[官方文档](http://reactivex.io/documentation/operators.html#)

## 创建Observables的操作符

这些操作符用来创建一个Observables

- `Create` 创建一个Observable;

```java
        Observable.create(new ObservableOnSubscribe<String>() {
            @Override
            public void subscribe(ObservableEmitter<String> e) throws Exception {
                e.onNext("this!!");
                e.onNext("is!!");
                e.onNext("create!!");
                e.onComplete();
            }
        }).subscribe(new Consumer<String>() {
            @Override
            public void accept(String s) throws Exception {
                System.out.print(s + " ");
            }
        });

        // 输出 this!! is!! create!! 
```

- `Defer` 不创建Observable直到它被订阅，并且为每个观察者创建一个新的Observalbe;

具体请看[这篇文章]();

```java
        Observable.defer(new Callable<ObservableSource<String>>() {
            @Override
            public ObservableSource<String> call() throws Exception {
                return Observable.just("this!", "is!", "defer!");
            }
        })
                .subscribe(new Consumer<String>() {
                    @Override
                    public void accept(String s) throws Exception {
                        System.out.print(s + " ");
                    }
                });
            // 输出 this! is! defer! 
```

- `empty` 创建一个空的Observable，被订阅然后结束;

- `never` 创建一个空的Observable，被订阅以后不会结束;

- `error` 创建一个Observable,参数是一个`Throwable`或`Callable`,被订阅然后执行异常结束;

- `from` 将其他的对象或者数据结构转换成一个Observable;

    - `fromArray` 将一个数组对象转换成Observable

    - `fromIterable` 将一个实现了迭代器接口的对象转换成Observalbe,例如一个List

    - `fromFuture` 将一个Future对象转换成Observable

    - `fromCallable` 将一个实现了Callable接口的对象转换成Observable

![rxJavaFrom](http://orzoelfvh.bkt.clouddn.com/rxjavaFrom.png?attname=&e=1500004944&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:E5wFdzCPZHuSXXh6Xp3cya6RMbI)

- `interval` 创建一个按照一定间隔发送一系列整数的Observable,再不取消的情况下，发送时间为无限长;

有以下重载：

![rxJavaInterval](http://orzoelfvh.bkt.clouddn.com/rxjavaInterval.png?attname=&e=1500007717&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:4S730sw9cC4Iir02Hu6nCbueQm8)

- `just` 将一个或者一组对象转换成Observable;

```java
        Observable.just("this", "is", "just")
                .subscribe(new Consumer<String>() {
                    @Override
                    public void accept(String s) throws Exception {
                        System.out.print(s + " "); //this is just 
                    }
                });
```
- `range` 创建一个发送特定范围序列整数的Observable;

```java
        Observable.range(1,5)
                .subscribe(new Consumer<Integer>() {
                    @Override
                    public void accept(Integer integer) throws Exception {
                        System.out.println(integer); // 1，2，3，4，5
                    }
                });
```

- `repeat` 创建一个重复发送的Observable;

不能直接调用，默认在调度器上执行，默认重复次数无限

![rxJavaRepeat](http://orzoelfvh.bkt.clouddn.com/rxJavaRepeat.png?attname=&e=1500018617&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:azGzvtjTqqtt794aSLZbLtSYsZM)

```java
        Observable.just("repeat")
                .repeat()
                .subscribe(new Consumer<String>() {
                    @Override
                    public void accept(String s) throws Exception {
                        System.out.println(s); //无限输出repeat
                    }
                });
```

- `startWith` 设置一个Observable的第一个值;

不能直接调用，默认在调度器上执行

![rxJavaStartWith](http://orzoelfvh.bkt.clouddn.com/rxJavaStartWith.png?attname=&e=1500019189&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:eqi1u2ONm6a4nOleF-W9sOfB1lk)

```java
        Observable.just("just")
                .startWith("start")
                .subscribe(new Consumer<String>() {
                    @Override
                    public void accept(String s) throws Exception {
                        System.out.println(s); // 输出 start just
                    }
                });
```

- `timer` 创建一个Observable在一定延迟后发送一条消息;

## 转换操作符

- `buffer` 它定期从Observable收集数据到一个集合，然后把这些数据集合打包发射，而不是一次发射一个;

```java
        Observable.just("this","is","buffer","test")
                .buffer(2)
                .subscribe(new Consumer<List<String>>() {
                    @Override
                    public void accept(List<String> strings) throws Exception {
                        System.out.println(strings); // 输出 [this, is]，[buffer, test]
                    }
                });
```

- `flatMap` 将Observable发射的数据变换为Observables集合，然后将这些Observable发射的数据平坦化的放进一个单独的Observable，内部采用merge合并;

```java
        Observable.just("flatMap")
                .flatMap(new Function<String, ObservableSource<String>>() {
                    @Override
                    public ObservableSource<String> apply(final String s) throws Exception {
                        return Observable.create(new ObservableOnSubscribe<String>() {
                            @Override
                            public void subscribe(ObservableEmitter<String> e) throws Exception {
                                e.onNext(s);
                                e.onNext(s + "test");
                            }
                        });
                    }
                })
                .subscribe(new Consumer<String>() {
                    @Override
                    public void accept(String s) throws Exception {
                        System.out.println(s); //flatMap flatMaptest
                    }
                });
```

- `groupBy` 将Observable分拆为Observable集合，将原始Observable发射的数据按Key分组，每一个Observable发射一组不同的数据;

```java

```