package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.pty.Pty;
import com.aliyun.agentbay.pty.PtyHandle;
import com.aliyun.agentbay.pty.PtySession;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

/**
 * Integration tests for the PTY module.
 */
public class PtyIntegrationTest {
    private static final String IMAGE_ID = "imgc-0ab5takiyxtc4h5bn";

    private static AgentBay agentBay;
    private static Session session;

    @BeforeClass
    public static void setUp() throws Exception {
        agentBay = new AgentBay();
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(IMAGE_ID);
        SessionResult result = agentBay.create(params);
        assertTrue("Session creation failed", result.isSuccess());
        assertNotNull(result.getSession());
        session = result.getSession();
        System.out.println("Session created: " + session.getSessionId());
    }

    @AfterClass
    public static void tearDown() {
        if (session != null && agentBay != null) {
            try {
                agentBay.delete(session, false);
                System.out.println("Session deleted");
            } catch (Exception e) {
                System.out.println("Warning: failed to delete session: " + e.getMessage());
            }
        }
    }

    @Test
    public void testCreateAndEcho() throws Exception {
        List<byte[]> chunks = Collections.synchronizedList(new ArrayList<>());
        PtyHandle handle = session.getPty().create(80, 24, data -> chunks.add(data.clone()));

        assertNotNull(handle.getPtySessionId());
        assertTrue(handle.isConnected());

        Thread.sleep(1000);
        handle.sendInput("echo 'PTY_JAVA_OK_99887'\r".getBytes(StandardCharsets.UTF_8));
        Thread.sleep(2000);

        StringBuilder combined = new StringBuilder();
        for (byte[] c : chunks) combined.append(new String(c, StandardCharsets.UTF_8));

        assertTrue("Expected PTY_JAVA_OK_99887 in output, got: " + combined,
            combined.toString().contains("PTY_JAVA_OK_99887"));

        handle.disconnect();
        System.out.println("testCreateAndEcho PASSED");
    }

    @Test
    public void testResize() throws Exception {
        List<byte[]> chunks = Collections.synchronizedList(new ArrayList<>());
        PtyHandle handle = session.getPty().create(80, 24, data -> chunks.add(data.clone()));

        Thread.sleep(1000);
        handle.resize(120, 40);
        Thread.sleep(1000);
        handle.sendInput("echo \"cols=$(tput cols) lines=$(tput lines)\"\r".getBytes(StandardCharsets.UTF_8));
        Thread.sleep(2000);

        StringBuilder combined = new StringBuilder();
        for (byte[] c : chunks) combined.append(new String(c, StandardCharsets.UTF_8));

        assertTrue("Expected cols=120 in output, got: " + combined,
            combined.toString().contains("cols=120"));
        assertTrue("Expected lines=40 in output, got: " + combined,
            combined.toString().contains("lines=40"));

        handle.disconnect();
        System.out.println("testResize PASSED");
    }

    @Test
    public void testList() throws Exception {
        PtyHandle handle = session.getPty().create();
        Thread.sleep(1000);

        List<PtySession> sessions = session.getPty().list();
        boolean found = false;
        for (PtySession s : sessions) {
            if (s.getPtySessionId().equals(handle.getPtySessionId())) {
                found = true;
                break;
            }
        }
        assertTrue("Created PTY not found in list", found);

        handle.disconnect();
        System.out.println("testList PASSED");
    }

    @Test
    public void testExitCode() throws Exception {
        PtyHandle handle = session.getPty().create();
        Thread.sleep(1000);

        handle.sendInput("exit\r".getBytes(StandardCharsets.UTF_8));
        int exitCode = handle.wait(10000);

        System.out.println("Exit code: " + exitCode);
        assertFalse(handle.isConnected());

        System.out.println("testExitCode PASSED");
    }

    @Test
    public void testKill() throws Exception {
        PtyHandle handle = session.getPty().create();
        Thread.sleep(1000);

        handle.kill();
        int exitCode = handle.wait(10000);

        assertEquals(-9, exitCode);
        System.out.println("testKill PASSED");
    }

    @Test
    public void testDisconnectReconnect() throws Exception {
        PtyHandle handle1 = session.getPty().create();
        Thread.sleep(1000);

        String ptyId = handle1.getPtySessionId();
        handle1.disconnect();
        assertFalse(handle1.isConnected());

        Thread.sleep(1000);

        List<byte[]> output2 = Collections.synchronizedList(new ArrayList<>());
        PtyHandle handle2 = session.getPty().connect(ptyId, data -> output2.add(data.clone()));
        assertTrue(handle2.isConnected());

        handle2.sendInput("echo 'RECONNECTED_JAVA'\r".getBytes(StandardCharsets.UTF_8));
        Thread.sleep(2000);

        StringBuilder combined = new StringBuilder();
        for (byte[] c : output2) combined.append(new String(c, StandardCharsets.UTF_8));

        assertTrue("Expected RECONNECTED_JAVA in output, got: " + combined,
            combined.toString().contains("RECONNECTED_JAVA"));

        handle2.disconnect();
        System.out.println("testDisconnectReconnect PASSED");
    }
}
