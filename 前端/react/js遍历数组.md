# js 对数组操作

http://www.runoob.com/jsref/jsref-obj-array.html

# js 对数组的遍历

http://www.infoq.com/cn/articles/es6-in-depth-iterators-and-the-for-of-loop

## for of 循环

```js
for (var value of myArray) {
  console.log(value);
}
```

- 这是最简洁、最直接的遍历数组元素的语法
- 这个方法避开了for-in循环的所有缺陷
- 与forEach()不同的是，它可以正确响应break、continue和return语句

# 数组与数组的拷贝和赋值

http://www.cnblogs.com/johnblogs/p/7218344.html