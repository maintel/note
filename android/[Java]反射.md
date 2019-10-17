            /*
            field.get
            字段不是静态字段的话,要传入反射类的对象.如果传null是会报
                java.lang.NullPointerException

                但是如果字段是静态字段的话,传入任何对象都是可以的,包括null
             */