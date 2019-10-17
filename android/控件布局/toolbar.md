# toolbar 子布局左边总是留白

原因是默认的 toolbar 样式引起的
```xml
<style name="Base.Widget.AppCompat.Toolbar" parent="android:Widget">    
    <item name="titleTextAppearance">@style/TextAppearance.Widget.AppCompat.Toolbar.Title</item>    
    <item name="subtitleTextAppearance">@style/TextAppearance.Widget.AppCompat.Toolbar.Subtitle</item>    
    <item name="android:minHeight">?attr/actionBarSize</item>    
    <item name="titleMargins">4dp</item>    
    <item name="maxButtonHeight">56dp</item>    
    <item name="collapseIcon">?attr/homeAsUpIndicator</item>    
    <item name="collapseContentDescription">@string/abc_toolbar_collapse_description</item>    
    <item name="contentInsetStart">16dp</item>     
</style> 
```
主要就是`contentInsetStart`引起的。可以使用以下几种方式来解决：

- 自定义样式

```xml
<style name="ClubToolbar" parent="Widget.AppCompat.Toolbar">    
        <item name="contentInsetStart">0dp</item><!-- 设置该属性解决空白部分-->    
</style>  
```
然后引用
```xml
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">  
        //.....  
        <item name="toolbarStyle">@style/ClubToolbar</item>  
    </style> 
```

- 直接指定属性

```xml
app:contentInsetEnd="0dp"
app:contentInsetLeft="0dp"
app:contentInsetRight="0dp"
app:contentInsetStart="0dp"
```