# 展示歌词

```kotlin
const val SHOW_MODEL_NORMAL = 1
const val SHOW_MODEL_MOVE = 2

class LrcView :
    View, ILrcView {
    override fun setVisible(invisible: Int) {
        this.visibility = invisible
    }

    override fun setOnClick(listener: () -> Unit) {
        mListener = listener
    }

    override fun setSeekChangeListener(listener: (currentTime: Long) -> Unit) {
        this.seekChange = listener
    }

    private var lrcBean: LrcBean? = null
    private var lrcRows: MutableList<LrcRow> = mutableListOf()
    private var currentTime: Long = -1
    private var currentPoi = -2
    private var showModel = SHOW_MODEL_NORMAL
    private var hasLrc = false
    private var mListener: (() -> Unit)? = null

    override fun setLrc(lrcBean: LrcBean?) {
        if (lrcBean == null) {
            hasLrc = false
            return
        }
        hasLrc = true
        this.lrcBean = lrcBean
        if (lrcBean.lrcRow != null) {
            lrcRows.addAll(lrcBean.lrcRow as Collection<LrcRow>)
        }
        var itemOffset = (height / 2).toFloat()
        var rowOffset = 0f
        for (i in 0 until lrcRows.size) {
            val item = lrcRows[i]
            item.staticLayout = StaticLayout(
                item.content, textPaint,
                width, Layout.Alignment.ALIGN_CENTER, 1f, 0f, true
            )
            if (i > 0) {
                val offset =
                    lrcRows[i - 1].staticLayout!!.height - lrcRows[i - 1].staticLayout!!.height / 2 + item.staticLayout!!.height / 2 + 30f
                itemOffset -= offset
                rowOffset += offset
            } else {
                itemOffset = (height / 2).toFloat()
                rowOffset = 0f
            }
            item.offset = itemOffset
            item.rowOffset = rowOffset
        }
        offset = (height / 2).toFloat()

        currentPoi = 0
        requestLayout()
    }

    override fun setSeek(currentTime: Long) {
        this.currentTime = currentTime
        if (!isLrcState()) {
            return
        }
        //计算应当高亮的内容
        val rePoi = matchCurrentPoi()
        if (currentPoi != rePoi) {
            this.currentPoi = rePoi
            if (showModel == SHOW_MODEL_NORMAL) {
                doScroll(currentPoi)
            }
        }
    }

    private lateinit var animObj: ValueAnimator

    /**
     * 执行滑动
     */
    private fun doScroll(poi: Int) {
        endAnim()
        val newOffset = lrcRows[poi].offset
        val oldOffset = offset
        animObj = ValueAnimator.ofFloat(oldOffset, newOffset)
        animObj.duration = 400
        animObj.repeatMode = ValueAnimator.REVERSE
        animObj.interpolator = LinearInterpolator()
        animObj.addUpdateListener {
            offset = it.animatedValue as Float
            invalidate()
        }
        animObj.start()
    }


    private fun endAnim() {
        if (this::animObj.isInitialized && animObj.isRunning) {
            animObj.end()
        }
    }

    private fun matchCurrentPoi(): Int {
        if (lrcBean == null) {
            return -2
        }
        lrcBean?.let {
            if (it.lrcRow == null || it.lrcRow!!.size == 0) { // 没有歌词
                return -2
            }
            val startPoi =
                if (currentPoi < 0 || currentTime < it.lrcRow!![currentPoi].time) 0 else currentPoi
            for (i in startPoi until it.lrcRow!!.size) {
                if (currentTime < it.lrcRow!![i].time) { // 应当显示的肯定比它上一个大，比它下一个小
                    return i - 1
                }
            }
            return it.lrcRow!!.size - 1
        }
        return -2
    }

    private var seekChange: ((time: Long) -> Unit)? = null
    private val paint: Paint = Paint()
    private val textPaint: TextPaint = TextPaint()
    private val mSimpleOnGestureListener: GestureDetector.SimpleOnGestureListener
    private val mGestureDetector: GestureDetector
    private val mScroller: Scroller

    constructor(context: Context?, attrs: AttributeSet?) : this(context, attrs, 0)
    constructor(context: Context?) : this(context, null, 0)
    constructor(context: Context?, attrs: AttributeSet?, defStyleAttr: Int) : super(
        context,
        attrs,
        defStyleAttr
    ) {
        handler = EventHandler(this)
        paint.color = Color.BLUE
        paint.textSize = 40f
        textPaint.textSize = 40f
        mScroller = Scroller(context)
        mSimpleOnGestureListener = object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent?): Boolean {
//                return super.onDown(e)
                if (hasLrc) {
                    return true
                } else {
                    return super.onDown(e)
                }
            }

            override fun onScroll(
                e1: MotionEvent?,
                e2: MotionEvent?,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                if (hasLrc) {
                    offset -= distanceY
                    offset = min(offset, lrcRows[0].offset)
                    offset = max(offset, lrcRows[lrcRows.size - 1].offset)
                    showModel = SHOW_MODEL_MOVE
                    invalidate()
                    return true
                } else {
                    return super.onScroll(e1, e2, distanceX, distanceY)
                }
            }

            override fun onSingleTapConfirmed(e: MotionEvent?): Boolean {
                mListener?.invoke()
                return super.onSingleTapConfirmed(e)
            }
        }
        mGestureDetector = GestureDetector(context, mSimpleOnGestureListener)
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        super.onLayout(changed, left, top, right, bottom)
    }

    var offset: Float = 0f

    override fun onDraw(canvas: Canvas?) {
        super.onDraw(canvas)
        // 第三版
        val centerHeight = (height / 2).toFloat()

        if (!hasLrc) {
            canvas?.save()
            val staticLayout = StaticLayout(
                "暂无歌词", textPaint,
                width, Layout.Alignment.ALIGN_CENTER, 1f, 0f, true
            )
            canvas?.translate(0f, centerHeight - staticLayout.height / 2)
            staticLayout.draw(canvas)
            canvas?.restore()
            return
        }

        if (showModel == SHOW_MODEL_MOVE && isLrcState()) {
            paint.color = Color.DKGRAY
            paint.strokeWidth = 3f
            canvas?.drawLine(0f, centerHeight, width.toFloat(), centerHeight, paint)
        }
        /**
         *         //先移动画布到指定位置 而不是让每一行都移动, 即 画布的基准位置
        // 中心思想就是，保证让歌词的第一行从画布0位置开始画
        // 所以为了同时保证每行歌词都在画面中心，要把从第0行开始要把画布的起始位置移动到中间
        // 然后根据每行歌词的偏移量 每次减小或者增大 offset 的值，来抵消掉歌词的向下偏移
        // 从而达到歌词向上滚动的效果，保证每行歌词都在中间位置{@link doScroll()  setLrc()}
         */
        canvas?.translate(0f, offset)
        // 绘制所有的歌词
        // rowsY 每行歌词的偏移量
        for (i in 0 until lrcRows.size) {
            if (!isLrcState()) {
                textPaint.color = Color.BLUE
            } else if (i == currentPoi) {
                textPaint.color = Color.RED
            } else if (i == getCenterLine() && showModel == SHOW_MODEL_MOVE) {
                textPaint.color = Color.GRAY
            } else {
                textPaint.color = Color.BLUE
            }

            val item = lrcRows[i]
            canvas?.save()
            // 平移的距离为 应当移动的距离 - 当前行高度/2 保证在正中间
            canvas?.translate(0f, item.rowOffset - item.staticLayout!!.height / 2)
            item.staticLayout!!.draw(canvas)
            canvas?.restore()
        }
    }

    private fun getCenterLine(): Int {
        var minDistance = Float.MAX_VALUE
        var centerLine = 0
        for (i in 0 until lrcRows.size) {
            if (abs(offset - lrcRows[i].offset) < minDistance) {
                minDistance = abs(offset - lrcRows[i].offset)
                centerLine = i
            }
        }
        return centerLine
    }

    private var handler: EventHandler
    override fun onTouchEvent(event: MotionEvent?): Boolean {
        if (lrcBean == null || lrcRows.size == 0) {
            return super.onTouchEvent(event)
        }

        //判断点击
        //判断拖动
        //拖动的时候画线以及时间计算
        when (event?.action) {
            MotionEvent.ACTION_UP -> {
                // 滚动到特定位置
                if (showModel == SHOW_MODEL_MOVE && isLrcState()) {
                    showModel = SHOW_MODEL_NORMAL
//                println(getCenterLine())
//                doScroll(getCenterLine())
                    scrollToSelect()
                } else {
                    showModel = SHOW_MODEL_NORMAL
                }
            }
        }
        return mGestureDetector.onTouchEvent(event)
    }

    private fun scrollToSelect() {
        val centerLin = getCenterLine()
        doScroll(centerLin)
        currentPoi = centerLin
        seekChange?.invoke(lrcRows[centerLin].time)
    }

    class EventHandler(view: LrcView) : Handler() {

        private val views = WeakReference<LrcView>(view)

        override fun handleMessage(msg: Message?) {
            super.handleMessage(msg)
            val view = views.get() ?: return
            when (msg?.what) {
                LRC_VIEW_CHANGE_NORMAL -> {
                    view.switchModelNormal()
                }
            }
        }
    }

    private fun switchModelNormal() {
        showModel = SHOW_MODEL_NORMAL
        invalidate()
    }

    /**
     * 判断是否是lrc 格式的歌词
     */
    private fun isLrcState(): Boolean {
        return Utils.isStringEquals(lrcBean?.lrcType, LRC_TYPE_LRC)
    }
}
```