



spring 在创建指运行开始 通过 ClassPathXmlApplicationContext 就把配置文件中的类全部 new 出来了

过程是


AbstractBeanFactory.doGetBean  获取 bean  如果没有  

```java
 protected <T> T doGetBean(String name, Class<T> requiredType, final Object[] args, boolean typeCheckOnly) throws BeansException {
     ...
    if(sharedInstance != null && args == null) {
        ...
    }else{
         if(!typeCheckOnly) {
                this.markBeanAsCreated(beanName);
            }

         if(ex1.isSingleton()) {
                    sharedInstance = this.getSingleton(beanName, new ObjectFactory() {
                        public Object getObject() throws BeansException {
                            try {
                                return AbstractBeanFactory.this.createBean(beanName, ex1, args);
                            } catch (BeansException var2) {
                                AbstractBeanFactory.this.destroySingleton(beanName);
                                throw var2;
                            }
                        }
                    });
                    bean = this.getObjectForBeanInstance(sharedInstance, name, beanName, ex1);
                }
    }
 }

```
AbstractBeanFactory 内部有一个 map 是它

    private final Map<String, RootBeanDefinition> mergedBeanDefinitions = new ConcurrentHashMap(256);





并存放在 DefaultSingletonBeanRegistry.singletonObjects 中  singletonObjects 是一个map

![](http://blogqn.maintel.cn/spring 分析 bean加载机制.png?e=3080883743&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:NegbLeefFbemOSGBy7fD8njQFlE=)