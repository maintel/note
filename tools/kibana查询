# 使用饼图

https://www.cnblogs.com/royfans/p/9711937.html

# 使用图表可视化查询时分组问题

查询出数据以后通过添加 Split Slices （分组）可以对不同类型的数据进行聚合，支持的类型如下：

## Date Histogram
一个 date histogram 从一个数值型字段构建，并按日期组织。可以为间隔指定一个按秒、分钟、小时、天、周、月或年的时间段。也可以指定一个自定义的时间区间，只需选择 Custom 作为间隔，并在文本字段中指定一个数字和一个时间单位即可。对于自定义间隔时间单位，s 表示秒， m 表示分钟，h 表示小时， d 表示天， w 表示周， y 表示年。不同单位支持不同的精度级别，最低为一秒。
## Histogram
一个标准的 histogram 从一个数值型字段构建，并为该字段指定一个整数类型的间隔，选择 Show empty buckets 复选框可在直方图中包括空的间隔。
## Range
通过一个 range 聚合，可以为一个数值型字段指定值的范围。点击 Add Range 增加一个范围聚合，点击红色的 (x) 符号来删除一个范围。

Range 类型的只支持数值型的字段。

## Date Range
date range 聚合展示在指定日期范围内的值。可通过 date math 表达式来指定日期范围。点击 Add Range 增加一个范围聚合，点击红色的 (/) 符号来删除一个范围。
## IPv4 Range
IPv4 range 聚合支持指定IPV4地址范围。点击 Add Range 增加一组范围端点，点击红色的 (/) 符号移除范围。
## Terms
terms 聚合支持指定要显示的给定字段的头部或尾部 n 个元素，并按数量或自定义指标进行排序。
## Filters
可以为数据指定一系列 filters 。支持通过一个查询串或者 JSON 格式来指定一个过滤器，就像在 Discover 搜索框中一样。点击 Add Filter 来增加另一个过滤器。点击 labelbutton label 按钮打开标签字段，输入一个可显示在视图中的名称。

filters 实际上也是执行了 query 语句，因此它支持使用通配符的方式查询，可以参考：[通配符查询](https://www.elastic.co/guide/cn/elasticsearch/guide/current/_wildcard_and_regexp_queries.html)。

举例：
比如要对某个字段的空和非空做分组看他们占比则可以添加两个 filter。

```
filter1: cookie.keyword:""    // 查询 cookie 为空的
filter2: {"wildcard":{"cookie.keyword":"*"}} // 查询 cookie 不为空的
```

## Significant Terms
显示试验 significant terms 聚合的结果。Size 参数的值定义了该聚合返回的实体数量。
