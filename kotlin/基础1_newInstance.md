# 单例模式的实现

```
class RemoteDataSourceImpl private constructor() : IDataSource {
    companion object {
        val INSTANCE: RemoteDataSourceImpl by lazy { Inner.INSTANCE }
    }

    private object Inner {
        val INSTANCE = RemoteDataSourceImpl()
    }
}
```

```
class DataManager private constructor(private val remoteDataSource: IDataSource, private val localDataSource: IDataSource) {

    companion object {
        var instance: DataManager? = null
        fun newInstance(remoteDataSource: IDataSource, localDataSource: IDataSource): DataManager {
            if (instance == null) {
                instance = DataManager(remoteDataSource, localDataSource)
            }
            return instance!!
        }
    }
}
```

