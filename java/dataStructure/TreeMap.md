# put

```java
    public V put(K key, V value) {
        Entry<K,V> t = root;
        // 如果根节点为 空 直接放入根节点
        if (t == null) {
            compare(key, key); // type (and possibly null) check

            root = new Entry<>(key, value, null);
            size = 1;
            modCount++;
            return null;
        }
        int cmp;
        Entry<K,V> parent;
        // split comparator and comparable paths
        // 比较器是否为空
        Comparator<? super K> cpr = comparator;
        if (cpr != null) { // 不为空
            do {
                parent = t;  // 父节点为 根节点
                cmp = cpr.compare(key, t.key);
                if (cmp < 0)   // 比父节点小 找到父节点的左节点赋值给 t
                    t = t.left;
                else if (cmp > 0)  // 比父节点大 找到父节点的右节点赋值给 t
                    t = t.right;
                else      // 否则就是替换
                    return t.setValue(value);
            } while (t != null);  // 循环遍历 直到 t=null 确定到最终要插入节点的位置。
        }
        else { // 否则就直接以Key 作为基数进行比较
            if (key == null)
                throw new NullPointerException();
            @SuppressWarnings("unchecked")
                Comparable<? super K> k = (Comparable<? super K>) key;
            do {
                parent = t;
                cmp = k.compareTo(t.key);
                if (cmp < 0)
                    t = t.left;
                else if (cmp > 0)
                    t = t.right;
                else
                    return t.setValue(value);
            } while (t != null);   // 和上面的逻辑一样
        }
        Entry<K,V> e = new Entry<>(key, value, parent); // 新建节点
        if (cmp < 0)   // 插入节点
            parent.left = e;
        else
            parent.right = e;
        fixAfterInsertion(e); // 平衡二叉树
        size++;
        modCount++;
        return null;
    }
```