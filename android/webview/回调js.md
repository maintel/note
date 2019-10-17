```js
// 现在回调过来的两种方法   这应该是 H5 那边自己写的框架 ——17zy
if (typeof window!="undefined" && typeof window.document!="undefined" && typeof window.document.dispatchEvent!="undefined"){window.document.dispatchEvent(new CustomEvent("_17m.refreshData",{"detail":[""]}))}


if (typeof vox!="undefined" && typeof vox.task!="undefined" && typeof vox.task.refreshData!="undefined"){vox.task.refreshData("")}
```
