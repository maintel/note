# input

[地址](http://2x.ant.design/components/input-cn/)

# 关于 input 组件获取值的问题

在很多回答中都是使用 onChange 来获取值得，但是在 react 中如果把数据存在 state 中每次都要更新 state 感觉不够好，能不能通过 refs 来获取呢。

使用下面代码来获取值获取不到：

```js
<Input style={{width:"150px"}} ref={(ref) => {this.phoneInput = ref}} placeholder="请输入手机号" />

...
mobile = this.phoneInput.value
...

```

获取到的值是一个未定义的，一直不明白为啥。查看 Input 源码发现官方在 input 组件外面又写了一层 dom，而本身的 refs 已经写死了是 input。

```js
export default class Input extends Component<InputProps, any> {
    ...
    refs: {
        input: HTMLInputElement;
    };
    ...
}
```

所以通过 ref 来获取值得方式应该这样写

```js
mobile = this.phoneInput.refs.input.value
```