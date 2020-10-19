# 支持显示隐藏的控件

- Visibility
- Offstage

# Visibility

Visibility 的实现其实就是用一个空的控件来替换，虽然不太高明但是很有效

它支持保持原来的位置大小，但是不可见 ———— 此种情况其实是用 Opacity 包裹控件然后设置透明度。

同样还支持保持控件状态 ———— 此种情况是使用 Offstage 包裹控件来实现，

如果上面两种都不设置，则使用了一个大小为 0 的 SizedBox 来替代原来的控件实现的。

# Offstage

通过覆盖 debugVisitOnstageChildren 方法来实现是否将子组件显示在前台。