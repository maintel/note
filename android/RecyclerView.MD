# RecyclerView 问题

# RecyclerView 嵌套 RecyclerView 自动滑动问题

**问题描述：**

  当 RecyclerView 的 item 中嵌套有 RecyclerView 时，子 RecyclerView 刷新 View 时，外层的 RecyclerView 会自动滑动到子 RecyclerView 的底部。

**解决办法：**

  很简单，对子 RecyclerView 设置无焦点。

```java
recyclerView.setFocusable(false);
```

*注意要在代码中设置，使用`android:focusable="false"`无效*

