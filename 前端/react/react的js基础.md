# 使用箭头函数的好处

在箭头函数出现之前，每个新定义的函数都有它自己的 this 值。

例如在 react 中定义了一个计数器有以下代码：

```js
class Timer extends React.Component{

    constructor(props){
        super(props);

        this.handleClick = this.handleClick.bind(this);  //需要在这里绑定 将this 值传递过来

        this.state = {
            count: 0,
        };
    }

    handleClick(e){
        e.preventDefault();

        this.setState({
            count:this.state.count + 1,   // 绑定了以后这里才能使用 this.state
        });
    }

    render(){
        return(
          <div>
              <p>{this.state.count}</p>
              <a href="#" onClick={this.handleClick}>点我更新呀</a>
          </div>
        );
    }
}

export default Timer;
```

 如果上面的函数不进行绑定，则在 handleClick 内部的 this.setState 会报空，但是如果进行如下使用箭头函数，则没有问题：

```js
//构造函数中不进行绑定
// this.handleClick = this.handleClick.bind(this);

//修改 handleClick 方法

    handleClick(){

        this.setState({
            count:this.state.count + 1,
        });
    }
// 引入箭头函数
 <a href="#" onClick={()=>{this.handleClick()}}>点我更新呀</a>
```

这里，没有进行绑定，但是一样可以使用 react 的 state 等，因为：

> 箭头函数会捕获其所在上下文的  this 值，作为自己的 this 值

# const {xxx} 和 const xxx 的区别

```js

        this.state = {
            name:'maintel',
            age:20,
        }

      const {name} = this.state;  // √
      const age = this.state;    //  ×
      const myAge = this.state.age // √
```

如上有 state 中赋值的 name 和 age，下面在某个地方用到了它，第一种调用能够拿到 name，但是第二种调用时拿不到 age 的，加个 `{}` 就能够进行自动赋值，但是前提是必须保证名字一致，而不加 `{}` 则必须指定到具体的属性值赋值，但是它的名字可以随便命名。

let 也是一样的。

调用函数

# 调用方法

```js
{this.methodName()} // 请牢记移动有括号
```

# 设置布局高度充满窗口

```js
style={{height:window.screen.height}}
```

# 使用 CSS

- 方法一

```js
require("../css/tabtest.css"); //导入 CSS 文件
<div className="bgWhite"></div> // 使用
```

# 值传递 ...

... 是ES6语法中的解构赋值。最简单的使用如下：

```js
let props = {
    a: 1,
    b: 2
}

<Hello {…props}/> 
```
上面的 hello 实际上是和下面的等效的

```html
<Hello a=1 b=1 /> 
```
很神奇，... 是展开语法， react 会自动把对象中的变量和值当作是属性的赋值，所以 Hello 实际上就拿到了 a、b 两个属性，如果没有三个点的话，Hello 拿到的实际上就是 props 对象，使用的时候还需要自己从中取出变量和值。