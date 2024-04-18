涉及平台：mac、windows、iOS、Android
涉及技术：网络、go、flutter、swift、C++、OC、java

整体架构：

上层使用 flutter 实现UI界面同时达到嵌入到当前项目以实现权限控制的目的。

底层使用go语言实现启动客户端与vpn节点通讯的能力。

中间使用flutter plugin 实现上层与底层库对应平台之间的通讯能力，同时实现在对应平台的一些特别化操作。

![整体架构](../img/WX20230321-111549.png)