
# appBar

[appBar](https://api.flutter-io.cn/flutter/material/AppBar-class.html)一个通用组件，使用样例如下，

```dart
class MainPageState extends State<MainPage> with SingleTickerProviderStateMixin{

  TabController _tabController;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _tabController = TabController(vsync: this,length: 3);
  }

  @override
  void dispose() {
    _tabController.dispose();
    // TODO: implement dispose
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Scaffold(
      appBar: AppBar(
        leading: Text("按钮"),  // 左侧按钮
        title: TextField(),  //标题 居中显示
        actions: <Widget>[  //右侧按钮
          Text("按钮1"),
          Text("按钮2")
        ],
        bottom: TabBar(  //底部导航，
          controller: _tabController,
          tabs: <Widget>[
            Text("1111"),
            Text("2222"),
            Text("3333")
          ],
        ),
        flexibleSpace: Image.asset("res/drawable/ic_user_center.png",width: 500,height: 100,), // 背景，它会置于底层
      ),
      body: TabBarView(
        controller: _tabController,
        children: <Widget>[
          SecondPage(),
          SecondPage(),
          SecondPage()
        ],
      ),
    );
  }

}
```

## 设置高度

设置高度可以使用 [PreferredSize](https://api.flutter-io.cn/flutter/widgets/PreferredSize-class.html) 对 appBar 进行包裹

```dart
appBar: PreferredSize(
        preferredSize: Size.fromHeight(80),
        child: AppBar(),
```

## 设置背景色

```dart
AppBar(
          backgroundColor: Colors.white,
      )
```

这里要注意的是 flutter 设置颜色的时候需要给透明度，否则无效。比如 `backgroundColor: Color(0xaaffff),` 就是无效的。