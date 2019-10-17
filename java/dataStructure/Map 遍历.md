# 方法一：


这是最常见的并且在大多数情况下也是最可取的遍历方式。在键值都需要时使用。

```java
Map<Integer, Integer> map = new HashMap<Integer, Integer>();
 
for (Map.Entry<Integer, Integer> entry : map.entrySet()) {
 
    System.out.println("Key = " + entry.getKey() + ", Value = " + entry.getValue());
 
}
```