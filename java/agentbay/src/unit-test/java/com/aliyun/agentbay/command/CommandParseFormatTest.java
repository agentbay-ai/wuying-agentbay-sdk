package com.aliyun.agentbay.command;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.Session;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

/**
 * Unit tests covering Command.executeCommand() across all known MCP Server response shapes.
 *
 * <p>Background: different sandbox images return different shapes in OperationResult.data:
 * <ul>
 *   <li>code_latest image: wraps stdout into {"exit_code":0,"stdout":"...","stderr":""}</li>
 *   <li>imgc-0aae4rgmdp871l41g image: returns the command's raw stdout directly,
 *       with no wrapping at all (whether or not it happens to be valid JSON)</li>
 *   <li>SLS evidence shows a third shape exists: {"result":{...},"success":true,"class":"..."}</li>
 * </ul>
 *
 * <p>The SDK must never silently lose data when the wrapping format is absent.
 * In particular, when the command stdout happens to be a valid JSON Object/Array/scalar,
 * the SDK must NOT mistake it for the wrapping envelope.
 */
public class CommandParseFormatTest {

    @Mock
    private Session mockSession;

    private Command command;

    @Before
    public void setUp() {
        MockitoAnnotations.openMocks(this);
        command = new Command(mockSession);
    }

    private void mockData(String data) {
        OperationResult op = new OperationResult("req-id", true, data, "");
        when(mockSession.callMcpTool(anyString(), any())).thenReturn(op);
    }

    private void mockFailure(String errorMessage) {
        OperationResult op = new OperationResult("req-id", false, "", errorMessage);
        when(mockSession.callMcpTool(anyString(), any())).thenReturn(op);
    }

    // ============================================================
    //  Group 1: standard wrapped format (code_latest image)
    // ============================================================

    @Test
    public void wrappedFormat_normalSuccess() {
        mockData("{\"exit_code\":0,\"stdout\":\"hello\\n\",\"stderr\":\"\"}");
        CommandResult cr = command.executeCommand("echo hello", 5000);
        assertTrue(cr.isSuccess());
        assertEquals(0, cr.getExitCode());
        assertEquals("hello\n", cr.getStdout());
        assertEquals("", cr.getStderr());
        assertEquals("hello\n", cr.getOutput());
    }

    @Test
    public void wrappedFormat_nonZeroExit() {
        mockData("{\"exit_code\":1,\"stdout\":\"\",\"stderr\":\"oops\\n\"}");
        CommandResult cr = command.executeCommand("false", 5000);
        assertEquals(1, cr.getExitCode());
        assertEquals("", cr.getStdout());
        assertEquals("oops\n", cr.getStderr());
        assertEquals("oops\n", cr.getOutput());
    }

    @Test
    public void wrappedFormat_withTraceId() {
        mockData("{\"exit_code\":0,\"stdout\":\"x\",\"stderr\":\"\",\"traceId\":\"trace-123\"}");
        CommandResult cr = command.executeCommand("echo x", 5000);
        assertEquals("trace-123", cr.getTraceId());
    }

    // ============================================================
    //  Group 2: raw stdout, NOT a valid JSON
    //  (imgc image, plain text commands)
    // ============================================================

    @Test
    public void rawFormat_plainText() {
        mockData("hello\n");
        CommandResult cr = command.executeCommand("echo hello", 5000);
        assertTrue(cr.isSuccess());
        assertEquals("hello\n", cr.getOutput());
        assertEquals("hello\n", cr.getStdout());
    }

    @Test
    public void rawFormat_largeText() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1024; i++) sb.append("x");
        sb.append("\n");
        mockData(sb.toString());
        CommandResult cr = command.executeCommand("python3 -c \"print('x'*1024)\"", 5000);
        assertEquals(sb.toString(), cr.getOutput());
        assertEquals(1025, cr.getOutput().length());
    }

    @Test
    public void rawFormat_multilineText() {
        mockData("line1\nline2\nline3\n");
        CommandResult cr = command.executeCommand("printf 'line1\\nline2\\nline3\\n'", 5000);
        assertEquals("line1\nline2\nline3\n", cr.getOutput());
    }

    // ============================================================
    //  Group 3: raw stdout that IS valid JSON
    //  (imgc image, commands that output JSON)
    //  *** This is exactly the user-reported regression. ***
    // ============================================================

    @Test
    public void rawFormat_jsonObjectWithoutWrapperFields() {
        mockData("{\"key\":\"value\"}");
        CommandResult cr = command.executeCommand("echo '{\"key\":\"value\"}'", 5000);
        assertTrue(cr.isSuccess());
        // The whole JSON must be returned as the command's stdout, NOT silently dropped.
        assertEquals("{\"key\":\"value\"}", cr.getOutput());
        assertEquals("{\"key\":\"value\"}", cr.getStdout());
    }

    @Test
    public void rawFormat_businessEnvelope_NextResultDO() {
        // This is the exact shape SLS captured for the user's failing case.
        String body = "{\"result\":{\"summary\":\"x\",\"items\":[],\"totalCount\":9},"
                + "\"success\":true,\"class\":\"com.taobao.next.common.domain.NextResultDO\"}";
        mockData(body);
        CommandResult cr = command.executeCommand("./risk-monitor get-risk-items", 5000);
        assertTrue(cr.isSuccess());
        assertEquals(body, cr.getOutput());
        assertEquals(body, cr.getStdout());
    }

    @Test
    public void rawFormat_jsonArray() {
        mockData("[1,2,3]");
        CommandResult cr = command.executeCommand("echo '[1,2,3]'", 5000);
        assertEquals("[1,2,3]", cr.getOutput());
    }

    @Test
    public void rawFormat_jsonScalar_boolean() {
        mockData("true");
        CommandResult cr = command.executeCommand("echo true", 5000);
        assertEquals("true", cr.getOutput());
    }

    @Test
    public void rawFormat_jsonScalar_number() {
        mockData("123");
        CommandResult cr = command.executeCommand("echo 123", 5000);
        assertEquals("123", cr.getOutput());
    }

    @Test
    public void rawFormat_jsonScalar_null() {
        mockData("null");
        CommandResult cr = command.executeCommand("echo null", 5000);
        assertEquals("null", cr.getOutput());
    }

    @Test
    public void rawFormat_prettyPrintedJson() {
        String pretty = "{\n  \"a\": 1,\n  \"b\": 2\n}";
        mockData(pretty);
        CommandResult cr = command.executeCommand("cat /tmp/pretty.json", 5000);
        assertEquals(pretty, cr.getOutput());
    }

    // ============================================================
    //  Group 4: edge cases for wrapper-format detection
    // ============================================================

    @Test
    public void wrappedFormat_partialFieldsButValid() {
        // Has stdout AND stderr (no exit_code). Reasonably treated as wrapped (defaults exit_code=0).
        mockData("{\"stdout\":\"hi\",\"stderr\":\"\"}");
        CommandResult cr = command.executeCommand("echo hi", 5000);
        assertEquals("hi", cr.getStdout());
        assertEquals("", cr.getStderr());
    }

    @Test
    public void rawFormat_jsonWithStdoutFieldButNoExitCode_isAmbiguousButTreatedAsRaw() {
        // Only stdout, no exit_code, no stderr. Cannot reliably tell if this is the wrapper
        // or a coincidental business JSON. Conservative choice: raw, return whole body.
        // (This matches the principle: only treat as wrapped when we're sure.)
        String body = "{\"stdout\":\"this is a business field, not the wrapper\"}";
        mockData(body);
        CommandResult cr = command.executeCommand("cat business.json", 5000);
        assertEquals(body, cr.getOutput());
    }

    @Test
    public void rawFormat_jsonWithExitCodeStringTypeFieldOnly_isRaw() {
        // exit_code present but as a string (not int). Definitely not the wrapper.
        String body = "{\"exit_code\":\"failed\",\"reason\":\"unknown\"}";
        mockData(body);
        CommandResult cr = command.executeCommand("cat status.json", 5000);
        assertEquals(body, cr.getOutput());
    }

    // ============================================================
    //  Group 5: failure path
    // ============================================================

    @Test
    public void failurePath_plainErrorMessage() {
        mockFailure("connection timeout");
        CommandResult cr = command.executeCommand("anything", 5000);
        assertEquals(false, cr.isSuccess());
        assertEquals("connection timeout", cr.getErrorMessage());
    }

    @Test
    public void failurePath_wrappedErrorJson() {
        mockFailure("{\"exit_code\":127,\"stdout\":\"\",\"stderr\":\"command not found\\n\"}");
        CommandResult cr = command.executeCommand("xxx", 5000);
        assertEquals(false, cr.isSuccess());
        assertEquals(127, cr.getExitCode());
        assertEquals("command not found\n", cr.getStderr());
    }
}
