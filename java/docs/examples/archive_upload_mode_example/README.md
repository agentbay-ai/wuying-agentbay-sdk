# Archive Upload Mode Example (Java)

This example shows **Archive** upload mode for context sync: bulk packaging for upload efficiency, plus **`archiveExcludePaths`** so selected paths stay as individual objects (direct/Presigned URL access) while the rest are archived.

The source file lives under `docs/examples` (not on the default Maven source path). Build the `agentbay` module, then compile and run this class with the module runtime classpath.

## Prerequisites

- JDK 17+ (see `java/agentbay/pom.xml`)
- Maven
- `AGENTBAY_API_KEY` in the environment

## Run

```bash
export AGENTBAY_API_KEY="your-api-key"
cd java/agentbay
mvn -q compile -DskipTests
mvn -q dependency:build-classpath -DincludeScope=runtime -Dmdep.outputFile=target/classpath.txt
javac -cp "target/classes:$(cat target/classpath.txt)" \
  ../docs/examples/archive_upload_mode_example/ArchiveUploadModeExample.java \
  -d target/example-classes
java -cp "target/example-classes:target/classes:$(cat target/classpath.txt)" ArchiveUploadModeExample
```

## What it does

1. **Basic Archive mode** — Creates a context and session with `UploadMode.ARCHIVE`, writes a 5&nbsp;KB file under the sync path, runs context sync and info, lists files via `context.listFiles`, then deletes the session with sync enabled.
2. **`archiveExcludePaths`** — Same flow with `important/` and `config.json` excluded from the archive bundle so they can be stored and accessed as individual files; writes files under excluded and non-excluded paths, syncs, lists, then deletes with sync.

## Expected output (illustrative)

- Printed context IDs and session IDs for each demo.
- Confirmation after file writes, sync, and list operations.
- Sessions deleted in `finally` blocks.

## See also

- Other Java examples under `java/docs/examples/`
- Context sync / upload policy documentation for your SDK version
