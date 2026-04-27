package com.aliyun.agentbay._internal;

import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

import com.aliyun.agentbay.exception.WsCancelledException;

public class WsClient {
    private static final Logger logger = LoggerFactory.getLogger(WsClient.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();

    public enum ConnectionState {
        OPEN, CLOSED, RECONNECTING, ERROR
    }

    @FunctionalInterface
    public interface ConnectionStateListener {
        void onStateChange(ConnectionState state, String reason);
    }

    private final String wsUrl;
    private final String token;

    private final OkHttpClient client;
    private volatile WebSocket webSocket;
    private volatile CompletableFuture<Void> connecting;

    private final ConcurrentHashMap<String, PendingStream> pendingById = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, List<PushCallback>> callbacksByTarget = new ConcurrentHashMap<>();

    private volatile ConnectionState state = ConnectionState.CLOSED;
    private final CopyOnWriteArrayList<ListenerEntry> stateListeners = new CopyOnWriteArrayList<>();
    private final AtomicLong nextListenerId = new AtomicLong(0);
    private final AtomicBoolean closedExplicitly = new AtomicBoolean(false);
    private final AtomicBoolean reconnecting = new AtomicBoolean(false);

    private final int heartbeatIntervalMs;
    private final int reconnectInitialDelayMs;
    private final int reconnectMaxDelayMs;
    private volatile ScheduledFuture<?> heartbeatFuture;
    private volatile ScheduledFuture<?> reconnectFuture;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
        Thread t = new Thread(r, "WsClient-scheduler");
        t.setDaemon(true);
        return t;
    });

    private static class ListenerEntry {
        final long id;
        final ConnectionStateListener listener;
        ListenerEntry(long id, ConnectionStateListener listener) {
            this.id = id;
            this.listener = listener;
        }
    }

    public interface OnEvent {
        void onEvent(String invocationId, Map<String, Object> data);
    }

    public interface OnEnd {
        void onEnd(String invocationId, Map<String, Object> data);
    }

    public interface OnError {
        void onError(String invocationId, Exception err);
    }

    public interface PushCallback {
        void onMessage(Map<String, Object> payload);
    }

    private static class PendingStream {
        final OnEvent onEvent;
        final OnEnd onEnd;
        final OnError onError;
        final CompletableFuture<Map<String, Object>> endFuture;
        final boolean isCall;

        PendingStream(OnEvent onEvent, OnEnd onEnd, OnError onError) {
            this(onEvent, onEnd, onError, false);
        }

        PendingStream(OnEvent onEvent, OnEnd onEnd, OnError onError, boolean isCall) {
            this.onEvent = onEvent;
            this.onEnd = onEnd;
            this.onError = onError;
            this.endFuture = new CompletableFuture<>();
            this.isCall = isCall;
        }
    }

    public class StreamHandle {
        public final String invocationId;
        private final CompletableFuture<Map<String, Object>> endFuture;
        private final String target;

        StreamHandle(String invocationId, CompletableFuture<Map<String, Object>> endFuture, String target) {
            this.invocationId = invocationId;
            this.endFuture = endFuture;
            this.target = target;
        }

        public CompletableFuture<Map<String, Object>> waitEnd() {
            return endFuture;
        }

        public void cancel() {
            cancelPending(invocationId);
        }

        public void write(Map<String, Object> data) {
            WebSocket ws = WsClient.this.webSocket;
            if (ws == null) {
                logger.warn("Failed to write: WS is not connected");
                return;
            }
            Map<String, Object> payload = new HashMap<>();
            payload.put("invocationId", invocationId);
            payload.put("source", "SDK");
            payload.put("target", target);
            payload.put("data", data);
            logFrame(">>", payload);
            try {
                String raw = objectMapper.writeValueAsString(payload);
                ws.send(raw);
            } catch (Exception e) {
                logger.warn("Failed to write: {}", e.getMessage());
            }
        }
    }

    public WsClient(String wsUrl, String token) {
        this(wsUrl, token, 20000, 1000, 30000);
    }

    public WsClient(String wsUrl, String token, int heartbeatIntervalMs,
                     int reconnectInitialDelayMs, int reconnectMaxDelayMs) {
        this.wsUrl = wsUrl;
        this.token = token;
        this.heartbeatIntervalMs = heartbeatIntervalMs;
        this.reconnectInitialDelayMs = reconnectInitialDelayMs;
        this.reconnectMaxDelayMs = reconnectMaxDelayMs;
        this.client = new OkHttpClient.Builder().build();
    }

    /**
     * Register a listener for connection state changes.
     * Returns a Runnable that unsubscribes the listener when called.
     */
    public Runnable onConnectionStateChange(ConnectionStateListener listener) {
        long id = nextListenerId.incrementAndGet();
        ListenerEntry entry = new ListenerEntry(id, listener);
        stateListeners.add(entry);
        return () -> stateListeners.removeIf(e -> e.id == id);
    }

    private void setState(ConnectionState newState, String reason) {
        if (this.state == newState) return;
        this.state = newState;
        logger.debug("WS state → {}: {}", newState, reason);
        for (ListenerEntry entry : stateListeners) {
            try {
                entry.listener.onStateChange(newState, reason);
            } catch (Exception e) {
                logger.warn("WS state listener error: {}", e.getMessage());
            }
        }
    }

    public ConnectionState getState() {
        return state;
    }

    public synchronized CompletableFuture<Void> connect() {
        if (webSocket != null) {
            return CompletableFuture.completedFuture(null);
        }
        if (connecting != null) {
            return connecting;
        }

        closedExplicitly.set(false);
        connecting = new CompletableFuture<>();
        openConnection();

        return connecting;
    }

    private void openConnection() {
        Request request = new Request.Builder()
            .url(wsUrl)
            .addHeader("X-Access-Token", token)
            .build();
        client.newWebSocket(request, new Listener());
    }

    public synchronized void close() {
        closedExplicitly.set(true);
        cancelReconnect();
        stopHeartbeat();

        WebSocket ws = webSocket;
        webSocket = null;
        connecting = null;
        if (ws != null) {
            try {
                ws.close(1000, "close");
            } catch (Exception e) {
            }
        }
        failAllPending(new RuntimeException("WS connection closed"));
        setState(ConnectionState.CLOSED, "closed by client");
    }

    private void startHeartbeat() {
        stopHeartbeat();
        heartbeatFuture = scheduler.scheduleAtFixedRate(() -> {
            WebSocket ws = webSocket;
            if (ws == null) return;
            try {
                Map<String, Object> ping = new HashMap<>();
                ping.put("type", "ping");
                String raw = objectMapper.writeValueAsString(ping);
                ws.send(raw);
            } catch (Exception e) {
                logger.debug("WS heartbeat send failed: {}", e.getMessage());
            }
        }, heartbeatIntervalMs, heartbeatIntervalMs, TimeUnit.MILLISECONDS);
    }

    private void stopHeartbeat() {
        ScheduledFuture<?> f = heartbeatFuture;
        if (f != null) {
            f.cancel(false);
            heartbeatFuture = null;
        }
    }

    private void scheduleReconnect() {
        if (closedExplicitly.get() || !reconnecting.compareAndSet(false, true)) {
            return;
        }
        setState(ConnectionState.RECONNECTING, "connection lost");
        reconnectWithBackoff(0);
    }

    private void reconnectWithBackoff(int attempt) {
        if (closedExplicitly.get()) {
            reconnecting.set(false);
            return;
        }
        double delayMs = reconnectInitialDelayMs * Math.pow(2, attempt);
        if (delayMs > reconnectMaxDelayMs) delayMs = reconnectMaxDelayMs;
        double jitter = delayMs * 0.3 * Math.random();
        long delay = (long) (delayMs + jitter);

        logger.debug("WS reconnect attempt {} in {}ms", attempt + 1, delay);
        reconnectFuture = scheduler.schedule(() -> {
            if (closedExplicitly.get()) {
                reconnecting.set(false);
                return;
            }
            try {
                CompletableFuture<Void> future = new CompletableFuture<>();
                synchronized (WsClient.this) {
                    connecting = future;
                }
                openConnection();
                future.get(10, TimeUnit.SECONDS);
                reconnecting.set(false);
            } catch (Exception e) {
                logger.debug("WS reconnect failed: {}", e.getMessage());
                reconnectWithBackoff(attempt + 1);
            }
        }, delay, TimeUnit.MILLISECONDS);
    }

    private void cancelReconnect() {
        reconnecting.set(false);
        ScheduledFuture<?> f = reconnectFuture;
        if (f != null) {
            f.cancel(false);
            reconnectFuture = null;
        }
    }

    public Runnable registerCallback(String target, PushCallback callback) {
        if (target == null || target.isEmpty()) {
            throw new IllegalArgumentException("target must be a non-empty string");
        }
        if (callback == null) {
            throw new IllegalArgumentException("callback must not be null");
        }
        callbacksByTarget.compute(target, (_k, v) -> {
            List<PushCallback> list = v != null ? v : new ArrayList<>();
            list.add(callback);
            return list;
        });
        return () -> unregisterCallback(target, callback);
    }

    public void unregisterCallback(String target, PushCallback callback) {
        if (target == null || target.isEmpty()) {
            throw new IllegalArgumentException("target must be a non-empty string");
        }
        if (callback == null) {
            callbacksByTarget.remove(target);
            return;
        }
        callbacksByTarget.computeIfPresent(target, (_k, v) -> {
            v.removeIf(cb -> cb == callback);
            return v.isEmpty() ? null : v;
        });
    }

    public CompletableFuture<StreamHandle> callStream(
        String target,
        Map<String, Object> data,
        OnEvent onEvent,
        OnEnd onEnd,
        OnError onError
    ) {
        return connect().thenApply(_v -> {
            WebSocket ws = webSocket;
            if (ws == null) {
                throw new RuntimeException("WS is not connected");
            }

            String invocationId = newInvocationId();
            PendingStream pending = new PendingStream(onEvent, onEnd, onError);
            pendingById.put(invocationId, pending);

            Map<String, Object> payload = new HashMap<>();
            payload.put("invocationId", invocationId);
            payload.put("source", "SDK");
            payload.put("target", target);
            payload.put("data", data);
            logFrame(">>", payload);

            try {
                String raw = objectMapper.writeValueAsString(payload);
                ws.send(raw);
            } catch (Exception e) {
                pendingById.remove(invocationId);
                pending.endFuture.completeExceptionally(e);
                throw new RuntimeException(e);
            }

            return new StreamHandle(invocationId, pending.endFuture, target);
        });
    }

    private void cancelPending(String invocationId) {
        PendingStream pending = pendingById.remove(invocationId);
        if (pending == null) {
            return;
        }
        Exception err = new WsCancelledException("Stream " + invocationId + " was cancelled by caller");
        if (pending.onError != null) {
            try {
                pending.onError.onError(invocationId, err);
            } catch (Exception cbErr) {
                logger.warn("onError callback failed during cancel", cbErr);
            }
        }
        pending.endFuture.completeExceptionally(err);
    }

    private void handleIncoming(String raw) {
        Map<String, Object> msg;
        try {
            msg = objectMapper.readValue(raw, Map.class);
        } catch (Exception e) {
            failAllPending(e);
            return;
        }

        Object invocationIdObj = msg.get("invocationId");
        if (invocationIdObj == null) invocationIdObj = msg.get("requestId");
        if (!(invocationIdObj instanceof String)) return;
        String invocationId = (String) invocationIdObj;

        PendingStream pending = pendingById.get(invocationId);
        Object sourceObj = msg.get("source");
        String source = sourceObj instanceof String ? (String) sourceObj : "";
        Object dataObj = msg.get("data");
        Object targetObj = msg.get("target");
        String target = targetObj instanceof String ? (String) targetObj : "";

        if ("WEBSOCKET_SERVER".equals(source)) {
            if (pending == null) return;
            Map<String, Object> lf = new HashMap<>();
            lf.put("invocationId", invocationId);
            lf.put("source", source);
            lf.put("data", dataObj);
            logFrame("<<", lf);
            String errMsg = "";
            Object errObj = msg.get("error");
            if (errObj instanceof String && !((String) errObj).isEmpty()) {
                errMsg = (String) errObj;
            }
            if (errMsg.isEmpty() && dataObj instanceof Map) {
                Object e = ((Map<?, ?>) dataObj).get("error");
                if (e instanceof String && !((String) e).isEmpty()) {
                    errMsg = (String) e;
                }
            }
            if (!errMsg.isEmpty()) {
                Exception err = new RuntimeException(errMsg);
                if (pending.onError != null) pending.onError.onError(invocationId, err);
                pending.endFuture.completeExceptionally(err);
                pendingById.remove(invocationId);
                return;
            }
            Map<String, Object> d = dataObj instanceof Map ? (Map<String, Object>) dataObj : new HashMap<>();
            if (pending.onEnd != null) pending.onEnd.onEnd(invocationId, d);
            pending.endFuture.complete(d);
            pendingById.remove(invocationId);
            return;
        }

        Map<String, Object> data = null;
        if (dataObj instanceof Map) {
            data = (Map<String, Object>) dataObj;
        } else if (dataObj instanceof String) {
            try {
                Object parsed = objectMapper.readValue((String) dataObj, Object.class);
                if (parsed instanceof Map) {
                    logger.warn("WS protocol violation: backend sent data as string; decoded to object");
                    data = (Map<String, Object>) parsed;
                } else {
                    return;
                }
            } catch (Exception e) {
                return;
            }
        } else {
            return;
        }

        if (pending == null) {
            String routeTarget = target;
            if ("SDK".equals(routeTarget) && source != null && !source.isEmpty() && !"SDK".equals(source)) {
                routeTarget = source;
            }
            if (routeTarget == null || routeTarget.isEmpty()) return;
            List<PushCallback> callbacks = callbacksByTarget.get(routeTarget);
            if (callbacks == null || callbacks.isEmpty()) return;

            Map<String, Object> payload = new HashMap<>();
            payload.put("requestId", invocationId);
            payload.put("target", routeTarget);
            payload.put("data", data);
            for (PushCallback cb : new ArrayList<>(callbacks)) {
                try {
                    cb.onMessage(payload);
                } catch (Exception e) {
                    logger.warn("Push callback failed: {}", e.getMessage());
                }
            }
            return;
        }

        Map<String, Object> lf = new HashMap<>();
        lf.put("invocationId", invocationId);
        lf.put("source", source);
        lf.put("target", msg.get("target"));
        lf.put("data", data);
        logFrame("<<", lf);

        if (pending.isCall) {
            Object callErr = data.get("error");
            if (callErr instanceof String && !((String) callErr).isEmpty()) {
                pending.endFuture.completeExceptionally(new RuntimeException((String) callErr));
            } else {
                pending.endFuture.complete(data);
            }
            pendingById.remove(invocationId);
            return;
        }

        Object errObj = data.get("error");
        if (errObj instanceof String && !((String) errObj).isEmpty()) {
            Exception err = new RuntimeException((String) errObj);
            if (pending.onError != null) pending.onError.onError(invocationId, err);
            pending.endFuture.completeExceptionally(err);
            pendingById.remove(invocationId);
            return;
        }

        Object phaseObj = data.get("phase");
        String phase = phaseObj instanceof String ? (String) phaseObj : "";
        if ("event".equals(phase)) {
            if (pending.onEvent != null) pending.onEvent.onEvent(invocationId, data);
            return;
        }
        if ("end".equals(phase)) {
            if (pending.onEnd != null) pending.onEnd.onEnd(invocationId, data);
            pending.endFuture.complete(data);
            pendingById.remove(invocationId);
            return;
        }

        Exception err = new RuntimeException("Unsupported phase: " + phaseObj);
        if (pending.onError != null) pending.onError.onError(invocationId, err);
        pending.endFuture.completeExceptionally(err);
        pendingById.remove(invocationId);
    }

    private void failAllPending(Exception err) {
        for (Map.Entry<String, PendingStream> e : pendingById.entrySet()) {
            PendingStream p = e.getValue();
            if (p.onError != null) p.onError.onError(e.getKey(), err);
            p.endFuture.completeExceptionally(err);
        }
        pendingById.clear();
    }

    private void logFrame(String direction, Map<String, Object> payload) {
        try {
            String raw = objectMapper.writeValueAsString(payload);
            if (raw.length() > 1200) raw = raw.substring(0, 1200) + "...";
            logger.debug("WS {} {}", direction, raw);
        } catch (Exception e) {
            logger.debug("WS {} {}", direction, String.valueOf(payload));
        }
    }

    /**
     * Send a request and wait for a single response (no phase semantics).
     * Expects data.result or data.error from the server.
     *
     * @param target    The target service
     * @param data      The request data
     * @param timeoutMs Timeout in milliseconds (0 defaults to 30 000)
     * @return The response data map
     * @throws Exception on timeout, connection failure, or server error
     */
    public Map<String, Object> call(String target, Map<String, Object> data, long timeoutMs) throws Exception {
        if (timeoutMs <= 0) timeoutMs = 30000;
        connect().get(timeoutMs, TimeUnit.MILLISECONDS);

        WebSocket ws = webSocket;
        if (ws == null) {
            throw new RuntimeException("WS is not connected");
        }

        String invocationId = newInvocationId();
        PendingStream pending = new PendingStream(null, null, null, true);
        pendingById.put(invocationId, pending);

        Map<String, Object> payload = new HashMap<>();
        payload.put("invocationId", invocationId);
        payload.put("source", "SDK");
        payload.put("target", target);
        payload.put("data", data);
        logFrame(">>", payload);

        try {
            String raw = objectMapper.writeValueAsString(payload);
            ws.send(raw);
        } catch (Exception e) {
            pendingById.remove(invocationId);
            throw e;
        }

        try {
            return pending.endFuture.get(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (java.util.concurrent.TimeoutException e) {
            pendingById.remove(invocationId);
            throw new RuntimeException("call() timed out after " + timeoutMs + "ms");
        }
    }

    /**
     * Send a message to the specified target without expecting a response.
     * This is a fire-and-forget operation.
     *
     * @param target The target service to send the message to
     * @param data The data to send
     */
    public void sendMessage(String target, Map<String, Object> data) {
        connect().thenAccept(_v -> {
            WebSocket ws = webSocket;
            if (ws == null) {
                logger.warn("Failed to send message: WS is not connected");
                return;
            }

            String invocationId = newInvocationId();
            Map<String, Object> payload = new HashMap<>();
            payload.put("invocationId", invocationId);
            payload.put("source", "SDK");
            payload.put("target", target);
            payload.put("data", data);
            logFrame(">>", payload);

            try {
                String raw = objectMapper.writeValueAsString(payload);
                ws.send(raw);
            } catch (Exception e) {
                logger.warn("Failed to send message: {}", e.getMessage());
            }
        }).exceptionally(e -> {
            logger.warn("Failed to connect for sending message: {}", e.getMessage());
            return null;
        });
    }

    private static String newInvocationId() {
        return Long.toHexString(System.nanoTime());
    }

    private class Listener extends WebSocketListener {
        @Override
        public void onOpen(WebSocket webSocket, Response response) {
            WsClient.this.webSocket = webSocket;
            CompletableFuture<Void> c = WsClient.this.connecting;
            WsClient.this.connecting = null;
            if (c != null && !c.isDone()) {
                c.complete(null);
            }
            startHeartbeat();
            setState(ConnectionState.OPEN, "connected");
        }

        @Override
        public void onMessage(WebSocket webSocket, String text) {
            handleIncoming(text);
        }

        @Override
        public void onClosing(WebSocket webSocket, int code, String reason) {
            stopHeartbeat();
            WsClient.this.webSocket = null;
            failAllPending(new RuntimeException("WS closing: " + code + " " + reason));
            if (!closedExplicitly.get()) {
                scheduleReconnect();
            }
        }

        @Override
        public void onClosed(WebSocket webSocket, int code, String reason) {
            stopHeartbeat();
            WsClient.this.webSocket = null;
            failAllPending(new RuntimeException("WS closed: " + code + " " + reason));
            if (!closedExplicitly.get()) {
                scheduleReconnect();
            }
        }

        @Override
        public void onFailure(WebSocket webSocket, Throwable t, Response response) {
            stopHeartbeat();
            WsClient.this.webSocket = null;
            Exception e = t instanceof Exception ? (Exception) t : new RuntimeException(t);
            CompletableFuture<Void> c = WsClient.this.connecting;
            WsClient.this.connecting = null;
            if (c != null && !c.isDone()) {
                c.completeExceptionally(e);
            }
            failAllPending(e);
            if (!closedExplicitly.get()) {
                setState(ConnectionState.ERROR, t.getMessage());
                scheduleReconnect();
            }
        }
    }
}

