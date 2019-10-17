# 枚举类的使用

```java
public enum RecommendTimeEnum {
        MORNING(1, "早晨", true),
        NOON(2, "下午", true),
        NIGHT(3, "晚上", true),
        NO_INNER(0, "不在推荐时间段内", false);

        int key;
        boolean isShow;
        String msg;

        RecommendTimeEnum(int i, String msg, boolean isShow) {
            key = i;
            this.isShow = isShow;
            this.msg = msg;
        }


        public static RecommendTimeEnum getByKey(int i) {
            for (RecommendTimeEnum item: RecommendTimeEnum.values()) {
                if (item.key == i) {
                    return item;
                }
            }
            return null;
        }


        public int getKey() {
            return key;
        }

        public boolean isShow() {
            return isShow;
        }

        public String getMsg() {
            return msg;
        }

        public static boolean isShow(int i) {
            for (RecommendTimeEnum item: RecommendTimeEnum.values()) {
                if (item.key == i) {
                    return item.isShow;
                }
            }
            return false;
        }

    }
```
