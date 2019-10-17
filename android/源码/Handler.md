handler 的底层需要 MessageQueue 和 Looper 来支撑。

MessageQueue 用来存储消息，它内部以队列的形式对外提供插入和删除工作。虽然叫队列，但是它的内部实现并不是一个队列，而是一个单链表的数据结构。

Looper 消息循环，Looper 会无限循环去查询消息队列中是否有新的消息，有的话就处理否则一直等待。

Looper 中还有一个特殊的概念 ThreadLocal，它并不是线程，而是用来在每个线程中存储数据。TheadLocal 可以在不同线程中互不干扰的存储并提供数据，通过 ThreadLocal 可以轻松的获取每个线程的 Looper。

子线程默认是没有 Looper 的。

