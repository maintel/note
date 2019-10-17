package com.yiqizuoye.jzt.view.anim

import android.animation.TypeEvaluator
import android.graphics.PointF

/**
 * 用于动画计算贝塞尔曲线
 * @author jieyu.chen
 * @date 2018/8/2
 *
 * pointFs 用来传递给定点 不包含首尾
 *
 */

const val BEZIER_CURVE_TYPE_ONE = 2  // 线性贝塞尔曲线
const val BEZIER_CURVE_TYPE_TWO = 3 // 二次贝塞尔曲线
const val BEZIER_CURVE_TYPE_THREE = 4 // 三次贝塞尔曲线

class BezierCurveEvaluator(val type: Int, private val pointFs: List<PointF>) : TypeEvaluator<PointF> {


    override fun evaluate(t: Float, pStart: PointF?, pEnd: PointF?): PointF {

        val startX = pStart!!.x
        val startY = pStart.y
        val endX = pEnd!!.x
        val endY = pEnd.y

        val pointF: PointF = PointF()
        val coeff = 1 - t
        when (type) {
            BEZIER_CURVE_TYPE_ONE -> {
                pointF.x = coeff * startX + t * endX
                pointF.y = coeff * startY + t * endY
            }
            BEZIER_CURVE_TYPE_TWO -> {
                pointF.x = coeff * coeff * startX + 2 * t * coeff * pointFs[0].x + t * t * endX
                pointF.y = coeff * coeff * startY + 2 * t * coeff * pointFs[0].y + t * t * endY
            }
            BEZIER_CURVE_TYPE_THREE -> {
                pointF.x = coeff * coeff * coeff * startX + 3 * pointFs[0].x * t * coeff * coeff
                +3 * pointFs[1].x * t * t * coeff + endX * t * t * t
                pointF.y = coeff * coeff * coeff * startY + 3 * pointFs[0].y * t * coeff * coeff
                +3 * pointFs[1].y * t * t * coeff + endY * t * t * t
            }
        }

        return pointF
    }


}