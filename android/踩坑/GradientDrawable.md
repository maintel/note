使用 GradientDrawable 动态修改背景色时，如果有当前页面的其他控件同样使用了同名资源的情况下会导致背景色被一同修改的情况，通过调用 mutate 方法来防止此类情况出现。

```kotlin
                val backGD: GradientDrawable = holder.mTipTag.background as GradientDrawable
                backGD.mutate()  // 调用 mutate 方法
                backGD.setColor(StringUtil.parseColor(bean.bottom_info.tip_tag.bg_color, 0x333333))
```

出现上述情况的原因是因为当多个控件同时使用同名资源的情况下，则他们的背景drawable （GradientDrawable ）中的 mGradientState 为同一对象， 而修改背景色其实就是修改的 mGradientState 中的内容，这就导致了多个控件同时被修改了。 而如果调用了 mutate 方法，它会给 GradientDrawable 重新 new 一个 mGradientState；

```java
    public Drawable mutate() {
        if (!mMutated && super.mutate() == this) {
            mGradientState = new GradientState(mGradientState, null);
            updateLocalState(null);
            mMutated = true;
        }
        return this;
    }
```