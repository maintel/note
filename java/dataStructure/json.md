# GSON 解析得到list或者map

使用 typeToken

```java
    @Test
    public void testMap() {
        String json = "{\"test\":\"aaa\",\"test2\":\"bbbb\",\"test3\":\"cccc\"}";

        Map<String, String> map = new Gson().fromJson(json, new TypeToken<Map<String, String>>() {
        }.getType());

        System.out.println(map.toString());
    }

    public void testList(){
        gson.fromJson(jsonObject.optString("data"),
                        new TypeToken<List<AllStudyRecResult>>() {
                        }.getType());
    }
```

# 使用jsonObject 来得到 map

```java
    public static Map<String, String> jsonToMap(String json) {
        Map<String, String> data = new HashMap<String, String>();
        try {

//            data = GsonUtils.getGsson().fromJson(json, HashMap.class);
            JSONObject jsonObject = new JSONObject(json);
            Iterator ite = jsonObject.keys();
            while (ite.hasNext()) {
                String key = ite.next().toString();
                String value = jsonObject.get(key).toString();
                data.put(key, value);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
        return data;
    }
```