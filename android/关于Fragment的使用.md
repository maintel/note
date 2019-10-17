# 使用 newInstance 的好处

Google 推荐如下写法：

```java
public static WeatherFragment newInstance(String cityName) {
    Bundle args = new Bundle();
    args.putString(cityName,"cityName");
    WeatherFragment fragment = new WeatherFragment();
    fragment.setArguments(args);
    return fragment;
}
```

这样写的好处是避免了在创建Fragment的时候无法在类外部知道所需参数的问题，在合作开发的时候特别有用。

还有就是Fragment推荐使用setArguments来传递参数，避免在横竖屏切换的时候Fragment自动调用自己的无参构造函数，导致数据丢失。即当Fragment自动创建的时候 这个 bundle 依然是可用的。

可以在后面通过 getArguments().getString("cityName"); 来获取bundle中的内容
