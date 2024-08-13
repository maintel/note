
```java
resp.setContentType("text/html;charset=utf-8");
```

`setContetType()` 方法的参数可以参考 `tomact` 安装目录 `\conf\web.xml` 中的 `<mime-mapping>`。同参考[对照表](http://blog.csdn.net/luman1991/article/details/53423305)




# form 表单如何和java文件关联起来

有一个 hello.html 中有以下代码

```html
<form action="Hello" method="GET">  //Hello 对应java文件
    网址名：<input type="text" name="name">
    <br />
    网址：<input type="text" name="url" />
    <input type="submit" value="提交" />
</form>
```

这个表单数据怎么在 java 文件中接收呢？

在要接收的 servlet 这样操作：

```java
@WebServlet("/Hello")   // 和上面的action="Hello"一致即可。
public class Hello extends HttpServlet {
    ...
}
```

- 接收的参数中如果有中文记得转码

```java
String name =new String(request.getParameter("name").getBytes("ISO8859-1"),"UTF-8");
```