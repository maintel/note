# 在 drawable 中设置图片纯色组合的背景

```xml
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">

    <item android:gravity="center">
        <shape android:shape="rectangle">
            <solid android:color="#fff8e6d3" />
            <corners android:radius="5dp" />
        </shape>
    </item>

    <item>
        <bitmap
            android:gravity="bottom|right"
            android:src="@drawable/icon_study_plan_card_hw" />
    </item>

</layer-list>
```

效果图如下，图片并不会变形：

![](http://blogqn.maintel.cn/TIM截图20181128154318.png?e=3120191041&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:56wwaaxKA31bDcYjneOlcvvcoaw=)

![](http://blogqn.maintel.cn/TIM截图20181128154341.png?e=3120191042&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:QdT_o4YJGXkAYV1HDeaFwg6xF4U=)