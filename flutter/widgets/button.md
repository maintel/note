flutter 官方实现的按钮 FlatButton ，

```dart
                        FlatButton(
                          color: const Color(0xffffffff),
                          highlightColor: const Color(0xCCff7C60),
                          splashColor: Colors.transparent,
                          child: Text("更换手机号"),
                          shape: RoundedRectangleBorder(
                              side: BorderSide(color: Color(0xFFF95540),width: 1),
                              borderRadius: BorderRadius.circular(25)),
                          onPressed: () {
                            dimiss();
                          },
                        ),
```

如果一些其他控件需要点击事件可以使用 GestureDetector 或者 InkWell 来包裹控件，

# 按压颜色
如果需要按压颜色则需要用 Inkwell 来实现，而且要注意的是外层一定要包裹一个 Material

下面是一个圆角按钮

```dart

Material(
      child: Ink(  // 通过 Ink 带的装饰器来实现圆角
        decoration: BoxDecoration(
            color: Color(0xfff95540),  // 通常的颜色
            borderRadius: BorderRadius.all(Radius.circular(25))),
        child: InkWell(
          highlightColor: Color(0xCCff7C60),  // 按压时的颜色
          radius: 0.0,      
          borderRadius: new BorderRadius.all(new Radius.circular(25.0)), // 和外层设置成同样大小的圆角，否则按压时边界不一致
          onTap: () {},
          child: Container(
            padding: EdgeInsets.fromLTRB(4, 8, 4, 8),
            alignment: Alignment.center,
            child: Text(
              widget.positiveStr,
              style: TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
        ),
      ),
    );
```
InkWell 还有两个属性 

```dart
                //水波纹的颜色 设置了highlightColor属性后 splashColor将不起效果
                splashColor: Colors.red,
                //true表示要剪裁水波纹响应的界面   false不剪裁  如果控件是圆角不剪裁的话水波纹是矩形
                containedInkWell: true,
```

