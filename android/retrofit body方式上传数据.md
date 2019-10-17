# Retrofit 2.0 使用@Body上传数据

# 服务器更新了

最近后台服务器调整使用`RequestBody`以及Json方式接受数据如下：

```java
    @RequestMapping(value = "/login", method = RequestMethod.POST)
    @ResponseBody
    public GeneralResponse<User> login(@RequestBody GeneralRequest<User> request) {
        ...
    }
```
# 使用@Body

项目原来使用的@Field形式参数请求后台的，但是改成@Body方式还是不能访问如下：

```java
    @POST(value = "user/login")
    Observable<BaseBean<User>> login(@Body String parameter);
```

原来后台是使用@RequestBody方式接收数据，直接解析Body中的json为一个对象来接收参数的。所以请求是body参数应该为`RequestBody`:

```java
    @POST(value = "user/login")
    Observable<BaseBean<User>> login(@Body RequestBody parameter);
```

同时，需要将请求的参数组装成一个json，然后转成`RequestBody`方式来上传，于是写了一个通用方法如下：

```java
    public static <T> RequestBody assRequestNoSession(T bean) {
        GeneralRequest<T> generalRequest = new GeneralRequest<>();
        generalRequest.setData(bean);
        Gson gson = new Gson();
        return RequestBody.create(MediaType.parse("application/json"), gson.toJson(generalRequest));
    }
```

# 添加请求头

但是修改以后还是不能成功访问后台，经过查阅资料发现因为后台是使用Json方式接受的，所以应该在请求头中添加`Content-Type: application/json`:

```java
    @Headers({"Content-Type: application/json"})
    @POST(value = "user/login")
    Observable<BaseBean<User>> login(@Body RequestBody parameter);
```

这样倒可是访问后台了，但是为每一个接口都添加请求头不够优雅，因此想到了使用拦截器，在Okhttp中添加如下：

```java
        OkHttpClient.Builder builder = new OkHttpClient.Builder();
        builder.addInterceptor(new Interceptor() {
                    @Override
                    public Response intercept(Chain chain) throws IOException {
                        Request newRequest = chain.request().newBuilder()
                                .addHeader("Content-Type", "application/json")
                                .build();
                        return chain.proceed(newRequest);
                    }
                });
```

这样，就可以正确的使用Body方式请求网络了。