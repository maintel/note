# 实现类似于.9的效果

可以使用 centerSlice 来实现，

```dart
        Container(
          decoration: BoxDecoration(
              image: DecorationImage(
                  fit: BoxFit.fill,
                  centerSlice: Rect.fromLTWH(0, 0, 152, 90),
                  image: AssetImage(ImageAsset.image(
                    "parent_user_head_add_child.9.png",
                  )))),
          constraints: BoxConstraints(
            minWidth: 48,
            maxWidth: 480,
          ),
          child: Text("添加新地址",style: TextStyle(color: Colors.white),),
          height: 45,
          alignment: Alignment.center,
        ),
```

`Rect.fromLTWH(0, 0, 152, 90)` 

- 前两个参数表示开始拉伸的起始坐标
- 后两个参数表示图片的原始宽高