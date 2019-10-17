# JSP 结构

网络服务器需要一个JSP引擎，也就是一个容器来处理JSP页面。容器负责截获对JSP页面的请求。

JSP容器与Web服务器协同合作，为JSP的正常运行提供必要的运行环境和其他服务，并且能够正确识别专属于JSP网页的特殊元素。

**以下步骤表明了Web服务器是如何使用JSP来创建网页的：**

- 就像其他普通的网页一样，您的浏览器发送一个HTTP请求给服务器。

- Web服务器识别出这是一个对JSP网页的请求，并且将该请求传递给JSP引擎。通过使用URL或者.jsp文件来完成。

- JSP引擎从磁盘中载入JSP文件，然后将它们转化为servlet。这种转化只是简单地将所有模板文本改用println()语句，并且将所有的JSP元素转化成Java代码。

- JSP引擎将servlet编译成可执行类，并且将原始请求传递给servlet引擎。

- Web服务器的某组件将会调用servlet引擎，然后载入并执行servlet类。在执行过程中，servlet产生HTML格式的输出并将其内嵌于HTTP response中上交给Web服务器。

- Web服务器以静态HTML网页的形式将HTTP response返回到您的浏览器中。

- 最终，Web浏览器处理HTTP response中动态产生的HTML网页，就好像在处理静态网页一样。

# JSP 生命周期

JSP生命周期就是从创建到销毁的整个过程，类似于servlet生命周期，区别在于JSP生命周期还包括将JSP文件编译成servlet。

- 编译阶段：

    servlet容器编译servlet源文件，生成servlet类

- 初始化阶段：

    加载与JSP对应的servlet类，创建其实例，并调用它的初始化方法

- 执行阶段：

    调用与JSP对应的servlet实例的服务方法

- 销毁阶段：

    调用与JSP对应的servlet实例的销毁方法，然后销毁servlet实例