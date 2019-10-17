# put 方法解析

```java
    public V put(K key, V value) {
        return putVal(hash(key), key, value, false, true);
    }
```

hash(key) 方法，可以看出来是允许 key 为 null 的。

```java
    static final int hash(Object key) {
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }
```

putVal() 方法：

```java
    final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
        Node<K,V>[] tab; Node<K,V> p; int n, i;
        // 先获取当前 tab 的长度 n，初始值为 16   这里 如果 tab 为空 就创建新的，并给 n 赋值。
        if ((tab = table) == null || (n = tab.length) == 0)
            n = (tab = resize()).length;
        // 根据索引找到 tab 响应位置有没有值 如果没有 就直接赋值
        // node 是hashMap 定义的内部类，里面存放了 hash 值，key值，value 值，以及 next 指向的下一个
        //值。因为 hashMap 是数组加链表结构  tab 就是数组，链表就有 node 组成。
        if ((p = tab[i = (n - 1) & hash]) == null)
            tab[i] = newNode(hash, key, value, null);
        else {
          // 如果已经有值 继续如下
            Node<K,V> e; K k;
            // 这里判断了 如果数组当前位置的第一个的 node 中 hash，key 和要存入的一样，就覆盖掉
            if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))
                e = p;
            // 如果这个链表为树结构，就填入进去
            else if (p instanceof TreeNode)
                e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
            else {
              // 否则在后面追加  这里是遍历链表
                for (int binCount = 0; ; ++binCount) {
                  // 给临时变量 e 赋值 并判断它的 next 是否为 null
                    if ((e = p.next) == null) {
                        //在当前链表后 追加新内容
                        p.next = newNode(hash, key, value, null);
                        // 如果一个链表过长，长度大于8，就扩容，规则是如果当前列表（即数组的长度大于64）
                        //就把当前链表转换成红黑树，否则就直接对列表的长度进行扩容。
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
                    // 判断是否和要插入的内容key是一致的，如果是就跳出循环
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    // 如果不是 就把遍历指针后移一位
                    p = e;
                }
            }
            if (e != null) { // existing mapping for key
                V oldValue = e.value;
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
                afterNodeAccess(e);
                return oldValue;
            }
        }
        ++modCount;
        // 如果长度大于最大阈值就扩容 threshold 原始值是 负载因子(0.75) * 初始长度(16)
        if (++size > threshold)
            resize();
        afterNodeInsertion(evict);
        return null;
    }
```

# get 方法

```java
    public V get(Object key) {
        Node<K,V> e;
        // 先计算 hash 值，然后 通过 getNode 方法
        return (e = getNode(hash(key), key)) == null ? null : e.value;
    }
```

```java
    final Node<K,V> getNode(int hash, Object key) {
        Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
        // 判断空，
        if ((tab = table) != null && (n = tab.length) > 0 &&
            (first = tab[(n - 1) & hash]) != null) {
            //判断在列表相应位置的第一个是否是要找的对象
            if (first.hash == hash && // always check first node
                ((k = first.key) == key || (key != null && key.equals(k))))
                return first;
            if ((e = first.next) != null) {
              // 如果是树结构
                if (first instanceof TreeNode)
                    return ((TreeNode<K,V>)first).getTreeNode(hash, key);
                // 循环遍历链表
                do {
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        return e;
                } while ((e = e.next) != null);
            }
        }
        return null;
    }
```

# 扩容方法 resize()

resize 大致过程就是，把列表的长度扩展到原来的两倍，然后重新计算 index，然后把旧的内容放入新的表中。

```java
    final Node<K,V>[] resize() {
        // 先复制出一份旧的表
        Node<K,V>[] oldTab = table;
        // 原始列表长度
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        // 原始列表阈值
        int oldThr = threshold;
        // 需要扩容的列表长度和 阈值
        int newCap, newThr = 0;
        if (oldCap > 0) {
          // 如果列表长度已经达到最大值了 就把阈值扩展到最大
            if (oldCap >= MAXIMUM_CAPACITY) {
                threshold = Integer.MAX_VALUE;
                return oldTab;
            }  // 否则 就把列表长度和阈值翻一倍
            else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                     oldCap >= DEFAULT_INITIAL_CAPACITY)
                newThr = oldThr << 1; // double threshold
        } 
        else if (oldThr > 0) // 否则就将初始长度设为阈值
            newCap = oldThr;
        else {               // 否则就是默认值
            newCap = DEFAULT_INITIAL_CAPACITY;
            newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
        }
        if (newThr == 0) {
            float ft = (float)newCap * loadFactor;
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                      (int)ft : Integer.MAX_VALUE);
        }
        threshold = newThr;
        @SuppressWarnings({"rawtypes","unchecked"})
            Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
        table = newTab;
        // 将原来的内容填入新的表中
        if (oldTab != null) {
          // 遍历列表
            for (int j = 0; j < oldCap; ++j) {
                Node<K,V> e;
                if ((e = oldTab[j]) != null) {
                    oldTab[j] = null;
                    // 如果只有一个 就替换了ok
                    if (e.next == null)
                        newTab[e.hash & (newCap - 1)] = e;
                    // 如果是红黑树交给红黑树做
                    else if (e instanceof TreeNode)
                        ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                    else { // 重新排序填入
                        Node<K,V> loHead = null, loTail = null; // 不用移动位置的
                        Node<K,V> hiHead = null, hiTail = null; // 需要移动位置的
                        Node<K,V> next;
                        // 重新组织链表
                        // 因为使用了 2 次幂的扩展机制，所以链表中的元素要么在原来列表的位置，要么就是移动2次幂的位置。很巧妙的设计
                        do {
                            next = e.next;
                            // 不需要移位的链表
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            }
                            // 需要移位的链表
                            else {
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        // 填入响应的位置
                        if (loTail != null) {
                            loTail.next = null;
                            newTab[j] = loHead;
                        }
                        if (hiTail != null) {
                            hiTail.next = null;
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        return newTab;
    }
```


