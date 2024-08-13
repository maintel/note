# 复杂类型

对于如 Map<String,Bean> 类型的json 字符串转 Map 的时候可以如下这样操作

```
jsonStr['examUnitMap'].cast<String, Bean>()
```

因为 dart 会自动猜类型，然后使用 Map 的 cast 方法映射到对应类型的 map，List 同理

https://api.dart.dev/stable/2.10.4/dart-core/Map/cast.html


上面的方式 只能针对 map 中的类型所包含的字段都是基本类型的才可以这么操作。如果是更复杂的类型可以

```dart
      (jsonStr['extraInfo'] as Map<String, dynamic>).forEach((key, value) {
        extraInfo.putIfAbsent(
            key, () => ExtraInfoItem.fromJson(value as Map<String, dynamic>));
      });
```

模仿上面的方式一层层嵌套下去。