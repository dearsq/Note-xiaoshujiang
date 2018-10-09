---
title: SOP_WebView_XML和JSON.md
tags: android
grammar_cjkRuby: true
---

# JSON
两种解析方法

## JSONObject
```
private void parseJSONWithJSONObject(String jsonData) {
        try {
            // 定义 JASON 数组 , 将服务器返回的数据传入到了 JSONObject 对象中
            JSONArray jsonArray = new JSONArray(jsonData);
            for(int i = 0; i < jsonArray.length(); i++) {
                JSONObject jsonObject = jsonArray.getJSONObject(i);
                String id = jsonObject.getString("id");
                String name = jsonObject.getString("name");
                String version = jsonObject.getString("version");

                Log.d(TAG, "parseJSONWithJSONObject: id is "+id);
                Log.d(TAG, "parseJSONWithJSONObject: name is "+name);
                Log.d(TAG, "parseJSONWithJSONObject: version is "+version);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
}
```

## GSON
比如要解析 App 类型的数据
1. 先实现 App 类:
```
public class App {
    private String id;
    private String name;
    private String version;

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getVersion() {
        return version;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setVersion(String version) {
        this.version = version;
    }
}
```
然后直接利用 json 创建对象
```
    private void parseJSONWithGSON(String jsonData) {
        Gson gson = new Gson();
        List<App> appList = gson.fromJson(jsonData, new TypeToken<List<App>>(){}.getType());
        for (App app : appList) {
            Log.d(TAG, "parseJSONWithGSON: id is " + app.getId());
            Log.d(TAG, "parseJSONWithGSON: name is " + app.getName());
            Log.d(TAG, "parseJSONWithGSON: version is " + app.getVersion());
        }
    }
```

# XML


## Pull 解析
```java
private void parseXMLWithPull(String xmlData) {
        try {
            // 1. 工厂类 , 借助工厂类实例的 nuwPullParser() 获得 XmlPullParse 的实例
            XmlPullParserFactory factory = XmlPullParserFactory.newInstance();
            XmlPullParser xmlPullParser = factory.newPullParser();
            // 2. setInput() 将服务器返回的 XML 数据 (xmlData) 设置进去并开始解析
            xmlPullParser.setInput(new StringReader(xmlData));
            // 3. 开始解析
            // 3.1 getEventType() 获取当前的解析事件
            int eventType = xmlPullParser.getEventType();
            String id = "";
            String name = "";
            String version = "";
            // 3.2 循环解析当前节点 直到 文件结束
            while (eventType != XmlPullParser.END_DOCUMENT) {
                String nodeName = xmlPullParser.getName();
                switch (eventType) {
                    // 开始解析某个节点
                    case XmlPullParser.START_TAG: {
                        if ("id".equals(nodeName)){
                            id = xmlPullParser.nextText();
                        } else if("version".equals(nodeName)) {
                            version = xmlPullParser.nextText();
                        } else if ("name".equals(nodeName)) {
                            name = xmlPullParser.nextText();
                        }
                        break;
                    }
                    // 完成解析某个节点
                    case XmlPullParser.END_TAG: {
                        if ("app".equals(nodeName)) {
                            Log.d(TAG, "parseXMLWithPull id is " + id);
                            Log.d(TAG, "parseXMLWithPull name is " + name);
                            Log.d(TAG, "parseXMLWithPull version is" + version);
                        }
                        break;
                    }
                    default:
                        break;
                }
                eventType =  xmlPullParser.next();
            }
        } catch (XmlPullParserException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
```


## SAX 解析
MainActivity.java
```
private void parseXMLWithSAX(String xmlData) {
        try {
            // 创建工厂类
            SAXParserFactory factory = SAXParserFactory.newInstance();
            // 通过工厂类获取 XMLReader 对象
            XMLReader xmlReader = factory.newSAXParser().getXMLReader();

            ContentHandler handler = new ContentHandler();
            //设置 ContentHanlder 实例到 XMLReader 中
            xmlReader.setContentHandler(handler);
            //开始执行解析
            xmlReader.parse(new InputSource(new StringReader(xmlData)));
        } catch (SAXException e) {
            e.printStackTrace();
        } catch (ParserConfigurationException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
```
ContentHandler.java
```

public class ContentHandler extends DefaultHandler {

    private static final String TAG = "ContentHandler";

    private String nodeName;
    private StringBuilder id;
    private StringBuilder name;
    private StringBuilder version;

    /**
     * Receive notification of the beginning of the document.
     * <p>
     * <p>By default, do nothing.  Application writers may override this
     * method in a subclass to take specific actions at the beginning
     * of a document (such as allocating the root node of a tree or
     * creating an output file).</p>
     *
     * @throws SAXException Any SAX exception, possibly
     *                      wrapping another exception.
     * @see org.xml.sax.ContentHandler#startDocument
     */
    @Override
    public void startDocument() throws SAXException {
        id = new StringBuilder();
        name = new StringBuilder();
        version = new StringBuilder();
    }

    /**
     * Receive notification of the end of the document.
     * <p>
     * <p>By default, do nothing.  Application writers may override this
     * method in a subclass to take specific actions at the end
     * of a document (such as finalising a tree or closing an output
     * file).</p>
     *
     * @throws SAXException Any SAX exception, possibly
     *                      wrapping another exception.
     * @see org.xml.sax.ContentHandler#endDocument
     */
    @Override
    public void endDocument() throws SAXException {
        super.endDocument();
    }

    /**
     * Receive notification of the start of an element.
     * 记录当前节点名字
     * <p>
     * <p>By default, do nothing.  Application writers may override this
     * method in a subclass to take specific actions at the start of
     * each element (such as allocating a new tree node or writing
     * output to a file).</p>
     *
     * @param uri        The Namespace URI, or the empty string if the
     *                   element has no Namespace URI or if Namespace
     *                   processing is not being performed.
     * @param localName  The local name (without prefix), or the
     *                   empty string if Namespace processing is not being
     *                   performed.
     * @param qName      The qualified name (with prefix), or the
     *                   empty string if qualified names are not available.
     * @param attributes The attributes attached to the element.  If
     *                   there are no attributes, it shall be an empty
     *                   Attributes object.
     * @throws SAXException Any SAX exception, possibly
     *                      wrapping another exception.
     * @see org.xml.sax.ContentHandler#startElement
     */
    @Override
    public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException {
        // 记录当前节点名字
        nodeName = localName;
    }

    /**
     * Receive notification of character data inside an element.
     * <p>
     * <p>By default, do nothing.  Application writers may override this
     * method to take specific actions for each chunk of character data
     * (such as adding the data to a node or buffer, or printing it to
     * a file).</p>
     *
     * @param ch     The characters.
     * @param start  The start position in the character array.
     * @param length The number of characters to use from the
     *               character array.
     * @throws SAXException Any SAX exception, possibly
     *                      wrapping another exception.
     * @see org.xml.sax.ContentHandler#characters
     */
    @Override
    public void characters(char[] ch, int start, int length) throws SAXException {
        // 根据当前的节点名判断将内容添加到哪一个 StringBuilder 中
        if ("id".equals(nodeName)) {
            id.append(ch, start, length);
        } else if ("name".equals(nodeName)) {
            name.append(ch, start, length);
        } else if ("version".equals(nodeName)) {
            version.append(ch, start, length);
        }
    }

    /**
     * Receive notification of the end of an element.
     * <p>
     * <p>By default, do nothing.  Application writers may override this
     * method in a subclass to take specific actions at the end of
     * each element (such as finalising a tree node or writing
     * output to a file).</p>
     *
     * @param uri       The Namespace URI, or the empty string if the
     *                  element has no Namespace URI or if Namespace
     *                  processing is not being performed.
     * @param localName The local name (without prefix), or the
     *                  empty string if Namespace processing is not being
     *                  performed.
     * @param qName     The qualified name (with prefix), or the
     *                  empty string if qualified names are not available.
     * @throws SAXException Any SAX exception, possibly
     *                      wrapping another exception.
     * @see org.xml.sax.ContentHandler#endElement
     */
    @Override
    public void endElement(String uri, String localName, String qName) throws SAXException {
        if ("app".equals(localName)) {
            Log.d(TAG, "endElement: id is " + id.toString().trim());
            Log.d(TAG, "endElement: name is " + name.toString().trim());
            Log.d(TAG, "endElement: version is " + version.toString().trim());
            // 最后将 StringBuilder 清空
            id.setLength(0);
            name.setLength(0);
            version.setLength(0);
        }
    }
}

```

