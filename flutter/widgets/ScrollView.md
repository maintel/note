通常使用的有  CustomScrollView、NestedScrollView 

NestedScrollView 可以通过嵌套 ListView 来完成滑动，

CustomScrollView 则需要通过使用 sliver 来完成滑动，

https://www.cnblogs.com/lxlx1798/p/11115573.html


# 一些常用的可滚动组件

- ListView
- NestedScrollView
  支持嵌套滚动
- GridView
- SingleChildScrollView
  有一个子 Widget 的可滚动组件，子内容超过父容器时可滚动
- ScrollView
- CustomScrollView
  也可以支持嵌套滚动，并控制每个组件的滚动效果

# CustomScrollView

CustomScrollView 通过使用 sliver 来完成嵌套滑动，它可以嵌套多个列表，每一个滚动列表都都应的有一个 sliver，如 listView 对应 SliverList 等。

举个例子，假设有一个页面，顶部需要一个GridView，底部需要一个ListView，而要求整个页面的滑动效果是统一的，即它们看起来是一个整体，如果使用GridView+ListView来实现的话，就不能保证一致的滑动效果，因为它们的滚动效果是分离的，所以这时就需要一个"胶水"，把这些彼此独立的可滚动widget（Sliver）"粘"起来，而CustomScrollView的功能就相当于“胶水”。
　　CustomScrollView让你可以直接提供 slivers来创建不同的滚动效果，比如Lists,grids 以及 expanding headers。

```dart
  Widget build(BuildContext context) {
    return CustomScrollView(
        slivers: <Widget>[
          SliverList(
            delegate: SliverChildListDelegate(
              _getAttenTion()
              ),
          ),
          SliverPadding(    //SliverPadding 包裹的也必须是一个 sliver 控件
            padding: const EdgeInsets.fromLTRB(10, 20, 20, 10),
            sliver: SliverList(
              delegate: SliverChildListDelegate(
                _getAttenTion()
              ),
            ),
            ),
          SliverGrid(
            gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 200,  // 每一行的宽度 不能超过屏幕的最大宽度
              mainAxisSpacing: 10,   // 平行于主坐标轴的间距， 竖直情况下就是 每行之间的距离 默认为0
              crossAxisSpacing: 20, // 垂直于主坐标轴的间距 竖直情况下就是 列间距  默认为0
              childAspectRatio: 2 //  垂直和平行坐标轴的宽高比。默认为1 比如竖直排列的话，设置为2就是宽 ： 高 2：1
            ),
            delegate: SliverChildBuilderDelegate(
              (BuildContext context, int index){
                return Text("data");
              },
              childCount:10
            )
        ],
    );
  }

List<Text> _getAttenTion() {
    List<Text> list = List();
    for(var i = 0;i < 100;i++){
        list.add(Text("i::$i"));
    }
    return list;
  }
```