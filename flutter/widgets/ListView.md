# 在一个 row 或者 Column 使用 list 时，

需要用 Expanded 把 listview 包裹起来，否则会报错

```dart
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
           Expanded(
              child: ListView(
                    scrollDirection: Axis.vertical,
                    shrinkWrap: true,
                    children: _getAttenTion(),
                  ),),
                  Text("dadadadad"),    
                  Text("dadadadad") 
      ]
    );
  }
```