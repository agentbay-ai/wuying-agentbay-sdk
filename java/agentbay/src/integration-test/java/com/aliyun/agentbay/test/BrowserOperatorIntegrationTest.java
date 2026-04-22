package com.aliyun.agentbay.test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.fail;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.browser.ActOptions;
import com.aliyun.agentbay.browser.ActResult;
import com.aliyun.agentbay.browser.BrowserOperator;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.browser.ExtractOptions;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * BrowserOperator 接口集成测试
 * 演示 act / actAsync / extract / extractAsync 四种调用方式
 *
 * act / actAsync     — 用于操作行为（点击、输入、导航等）
 * extract / extractAsync — 用于提取页面结构化信息
 *
 * act 与 actAsync 的区别：
 *   - act() 调用 page_use_act，服务端同步执行完成后直接返回结果
 *   - actAsync() 调用 page_use_act_async + 轮询 page_use_get_act_result，适合长时间任务
 *
 * extract 与 extractAsync 的区别：
 *   - extract() 调用 page_use_extract，服务端同步执行完成后直接返回结果
 *   - extractAsync() 调用 page_use_extract_async + 轮询 page_use_get_extract_result，适合复杂提取
 */
public class BrowserOperatorIntegrationTest {

    private static AgentBay agentBay;
    private static Session session;

    /**
     * 页面信息提取结果 schema
     */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class PageInfo {
        @JsonProperty("title")
        private String title;

        @JsonProperty("content")
        private List<String> content;

        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public List<String> getContent() { return content; }
        public void setContent(List<String> content) { this.content = content; }

        @Override
        public String toString() {
            return "PageInfo{title='" + title + "', content=" + content + "}";
        }
    }

    @BeforeClass
    public static void setUp() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull("AGENTBAY_API_KEY environment variable must be set", apiKey);
        assertFalse("AGENTBAY_API_KEY cannot be empty", apiKey.trim().isEmpty());

        agentBay = new AgentBay(apiKey);
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        SessionResult sessionResult = agentBay.create(params);

        if (sessionResult.isSuccess()) {
            session = sessionResult.getSession();
            System.out.println("Session created, resourceUrl: " + session.getResourceUrl());
        } else {
            fail("Failed to create session: " + sessionResult.getErrorMessage());
        }
    }

    @AfterClass
    public static void tearDown() {
        if (agentBay != null && session != null) {
            try {
                agentBay.delete(session);
                System.out.println("Session deleted.");
            } catch (Exception e) {
                System.err.println("Failed to delete session: " + e.getMessage());
            }
        }
    }

    /**
     * act() — 同步操作，调用 page_use_act，服务端执行完成后直接返回
     */
    @Test
    public void testAct() throws Exception {
        assertNotNull("Session must be created", session);
        session.getBrowser().initialize(new BrowserOption());
        BrowserOperator operator = session.getBrowser().getOperator();

        operator.navigate("https://www.aliyun.com");
        System.out.println("Navigated to aliyun.com");

        ActOptions options = new ActOptions("点击搜索框并输入agentbay");
        ActResult result = operator.act(options);
        System.out.println("act result: " + result);
        assertNotNull("act result should not be null", result);
    }

    /**
     * actAsync() — 异步操作，调用 page_use_act_async + 轮询 page_use_get_act_result
     * 适合耗时较长的操作，客户端 3s 轮询一次直到 is_done=true
     */
    @Test
    public void testActAsync() throws Exception {
        assertNotNull("Session must be created", session);
        session.getBrowser().initialize(new BrowserOption());
        BrowserOperator operator = session.getBrowser().getOperator();

        operator.navigate("https://www.aliyun.com");
        System.out.println("Navigated to aliyun.com");

        ActOptions options = new ActOptions("点击搜索框并输入agentbay");
        ActResult result = operator.actAsync(options);
        System.out.println("actAsync result: " + result);
        assertNotNull("actAsync result should not be null", result);
    }

    /**
     * extract() — 同步提取，调用 page_use_extract，服务端执行完成后直接返回
     */
    @Test
    public void testExtract() throws Exception {
        assertNotNull("Session must be created", session);
        session.getBrowser().initialize(new BrowserOption());
        BrowserOperator operator = session.getBrowser().getOperator();

        operator.navigate("https://www.aliyun.com");
        System.out.println("Navigated to aliyun.com");

        ExtractOptions<PageInfo> extractOptions = new ExtractOptions<>(
                "获取当前页面的标题和页面上的主要内容",
                PageInfo.class);
        BrowserOperator.ExtractResultTuple<PageInfo> result = operator.extract(extractOptions);
        System.out.println("extract result: " + result.getData());
        assertNotNull("extract result should not be null", result.getData());
    }

    /**
     * extractAsync() — 异步提取，调用 page_use_extract_async + 轮询 page_use_get_extract_result
     * 适合复杂页面提取，客户端 3s 轮询一次直到有结果返回
     */
    @Test
    public void testExtractAsync() throws Exception {
        assertNotNull("Session must be created", session);
        session.getBrowser().initialize(new BrowserOption());
        BrowserOperator operator = session.getBrowser().getOperator();

        operator.navigate("https://www.aliyun.com");
        System.out.println("Navigated to aliyun.com");

        ExtractOptions<PageInfo> extractOptions = new ExtractOptions<>(
                "获取当前页面的标题和页面上的主要内容",
                PageInfo.class);
        BrowserOperator.ExtractResultTuple<PageInfo> result = operator.extractAsync(extractOptions);
        System.out.println("extractAsync result: " + result.getData());
        assertNotNull("extractAsync result should not be null", result.getData());
    }
}
