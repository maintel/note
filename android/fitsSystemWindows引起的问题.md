
# android:fitsSystemWindows="true"　引起toast不显示在中间的问题

由于使用了沉浸式状态栏，为了方便在AppTheme中加入了

```xml
android:fitsSystemWindows="true"
```
但是加入以后却造成Toast居中显示，甚至在一些版本上Progress也出现了问题。

这个时候在弹出Toast的时候必须使用`getapplicationcontext`。