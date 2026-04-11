# Env Module Example (Java)

This example shows **session-scoped** environment variables with `session.getEnv()`: set a map, get all variables, get selected keys, overwrite a key, and run `echo $DEMO_APP` via `session.getCommand()`.

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
  ../docs/examples/common-features/basics/env_management/EnvManagementExample.java \
  -d target/example-classes
java -cp "target/example-classes:target/classes:$(cat target/classpath.txt)" EnvManagementExample
```

The session uses `imageId` `AIO_ubuntu2404`.

## Expected output (illustrative)

- Session ID after create.
- Printed `DEMO_APP` / `DEMO_STAGE` values through get-all and get-by-key steps.
- After overwrite, `DEMO_STAGE` is `prod`.
- `echo $DEMO_APP` prints `agentbay`.
- Session deleted in `finally`.

## See also

- [Env API reference](../../../../api/common-features/basics/env.md)
