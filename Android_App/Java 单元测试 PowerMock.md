title: Android 单元测试 PowerMock
date: 2021-10-26 21:00:00
tags: Android

---



## 基本概念
PowerMock是一个Java模拟框架，用于解决测试问题。
PowerMock使用一个自定义类加载器和字节码操作来模拟静态方法、构造方法、final类和方法、私有方法、去除静态初始化器等等。

## 使用步骤
### 引入
``` build.gradle
    testImplementation "org.powermock:powermock-module-junit4:2.0.2"
    testImplementation "org.powermock:powermock-api-mockito2:2.0.2"
```
### 注解
``` java
@RunWith(PowerMockRunner.class) // 告诉JUnit使用PowerMockRunner进行测试

@PrepareForTest({RandomUtil.class}) // 所有需要测试的类列在此处，适用于模拟final类或有final, private, static, native方法的类

@PowerMockIgnore("javax.management.*") //为了解决使用powermock后，提示classloader错误
```

### Mock代码
``` java
public interface MockMapper {
　　public int count(MockModel model);
}

@Service
public class MockServiceImpl {
　　@Autowired
　　private MockMapper mockMapper;

　　public int count(MockModel model) {
　　　　return mockMapper.count(model);
　　}
}

public class MockExample {
    // 将@Mock注解的示例注入进来
    @InjectMocks
    private MockServiceImpl mockService;
    @Mock
    private MockMapper mockMapper;
    
    /**
     * mock普通方法
     */
    @Test
    public void testSelectAppAdvertisementList() {
        MockModel model = new MockModel();
        PowerMockito.when(mockMapper.count(model)).thenReturn(2);
        
        Assert.assertEquals(2, mockService.count(model));
    }
}


```

## 参考文章

PowerMock使用详解：https://www.cnblogs.com/lovezmc/p/11232112.html