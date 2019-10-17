# 滑动禁止加载图片

在列表滑动时禁止加载图片

```kotlin
        rcyImgs.addOnScrollListener(object : RecyclerView.OnScrollListener() {

            override fun onScrollStateChanged(recyclerView: RecyclerView?, newState: Int) {
                super.onScrollStateChanged(recyclerView, newState)
                if (newState == 0) {
                    adapter.startLoad()
                }
            }


            override fun onScrolled(recyclerView: RecyclerView?, dx: Int, dy: Int) {
                super.onScrolled(recyclerView, dx, dy)
                // 优化列表滑动加载图片 不再使用是否是滑动作为标志 而是使用滑动速度，这样在慢速的情况下也进行加载体验更好
                // 不过这样写有一个 bug 如果急速滑动的时候一下子按住暂停 这个时候onScrolled方法不会响应 所以要配合onScrollStateChanged 使用
                when (dy) {
                    in (-100..100) -> {
                        adapter.startLoad()
                    }
                    else -> {
                        adapter.stopLoading()
                    }
                }
            }
        })
```