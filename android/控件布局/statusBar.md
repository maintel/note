# 全屏

下面的代码是设置全屏，会隐藏掉状态栏和虚拟按键

```java
        if (Build.VERSION.SDK_INT >= 19) {
            View decorView = getWindow().getDecorView();
            decorView.setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        }
```

# 透明状态栏

只有 4.4 （19） 以上生效

```java
getWindow().addFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
```

# 透明导航栏

只有 4.4 （19）有效

```java
getWindow().addFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION);
```