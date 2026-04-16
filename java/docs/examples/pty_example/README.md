# PTY Terminal Example (Java)

Java SDK examples are often documented as runnable snippets. This README shows the core PTY flow: create, echo, resize, list, disconnect/reconnect, kill, and exit with `wait`.

## Prerequisites

- `AGENTBAY_API_KEY` set in the environment
- Maven dependency on `com.aliyun:agentbay` (see the main Java README)

## Pattern: Session and Default Image

Use `CreateSessionParams` without setting an image ID when the platform default is sufficient for PTY:

```java
AgentBay agentBay = new AgentBay(System.getenv("AGENTBAY_API_KEY"));
CreateSessionParams params = new CreateSessionParams();
SessionResult result = agentBay.create(params);
Session session = result.getSession();
try {
    runPtyDemo(session);
} finally {
    agentBay.delete(session);
}
```

## 1. Create PTY, Echo, Resize, List

```java
import com.aliyun.agentbay.pty.Pty;
import com.aliyun.agentbay.pty.PtyHandle;
import com.aliyun.agentbay.pty.PtySession;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

List<byte[]> chunks = new ArrayList<>();
Consumer<byte[]> onData = chunks::add;

Pty pty = session.getPty();
PtyHandle handle = pty.create(80, 24, onData);
Thread.sleep(1000L);
handle.sendInput("echo 'AGENTBAY_PTY_EXAMPLE_ECHO'\r".getBytes(StandardCharsets.UTF_8));
Thread.sleep(2000L);

handle.resize(120, 40);
Thread.sleep(1000L);
handle.sendInput("echo \"cols=$(tput cols) lines=$(tput lines)\"\r".getBytes(StandardCharsets.UTF_8));
Thread.sleep(2000L);

List<PtySession> listed = pty.list();
boolean found = listed.stream().anyMatch(s -> s.getPtySessionId().equals(handle.getPtySessionId()));
```

## 2. Disconnect and Reconnect

```java
String ptyId = handle.getPtySessionId();
handle.disconnect();

List<byte[]> out2 = new ArrayList<>();
PtyHandle handle2 = pty.connect(ptyId, out2::add);
Thread.sleep(1000L);
handle2.sendInput("echo 'AGENTBAY_PTY_EXAMPLE_RECONNECT'\r".getBytes(StandardCharsets.UTF_8));
Thread.sleep(2000L);
handle2.disconnect();
```

## 3. Kill (Exit Code -9)

```java
PtyHandle killHandle = pty.create();
Thread.sleep(1000L);
killHandle.kill();
int killCode = killHandle.wait(10000); // expect -9
```

## 4. Exit Shell (Exit Code 0)

```java
PtyHandle exitHandle = pty.create();
Thread.sleep(1000L);
exitHandle.sendInput("exit\r".getBytes(StandardCharsets.UTF_8));
int exitCode = exitHandle.wait(10000); // expect 0
```

## API Reference

- `com.aliyun.agentbay.pty.Pty` — `create`, `list`, `connect`, `kill`
- `com.aliyun.agentbay.pty.PtyHandle` — `sendInput`, `resize`, `kill`, `wait`, `disconnect`

## Related

- Source: `java/agentbay/src/main/java/com/aliyun/agentbay/pty/`
