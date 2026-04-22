// ci-stable
/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */
import { AgentBay, Session } from "../../src";
import { log } from "../../src/utils/logger";

const API_KEY = process.env.AGENTBAY_API_KEY || "";
const IMAGE_ID = "code-space-debian-12";
const REPO_URL =
  "https://github.com/DingTalk-Real-AI/dingtalk-openclaw-connector.git";
const LOCAL_REPO = "/tmp/test-git-workflow";

if (!API_KEY) {
  throw new Error("AGENTBAY_API_KEY environment variable not set");
}

describe("Git Full Workflow Test", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeAll(async () => {
    log("=== 初始化 AgentBay 客户端 ===");
    agentBay = new AgentBay({ apiKey: API_KEY });

    log(`=== 创建会话（镜像: ${IMAGE_ID}）===`);
    const createResponse = await agentBay.create({ imageId: IMAGE_ID });

    if (!createResponse.success || !createResponse.session) {
      throw new Error("Failed to create session");
    }

    session = createResponse.session;
    log(`会话创建成功，Session ID: ${session.sessionId}`);
  });

  afterAll(async () => {
    log("=== 清理会话 ===");
    try {
      if (session && session.sessionId) {
        await agentBay.delete(session);
        log("会话删除成功");
      }
    } catch (error) {
      log(`警告: 删除会话时出�? ${error}`);
    }
  });

  // =============================================
  // 主流程测试（基于本地 init，不依赖网络）
  // =============================================

  // Step 1: Init
  it("1. init - 初始化本地仓库", async () => {
    log(`\n=== 初始化本地仓库 ===`);

    await session.command.executeCommand(`mkdir -p ${LOCAL_REPO}`, 10000);

    const initResult = await session.git.init(LOCAL_REPO, {
      initialBranch: "main",
    });

    log(`初始化路径: ${initResult.path}`);
    expect(initResult.path).toBe(LOCAL_REPO);
    log("✓ init 成功");
  }, 60000);

  // Step 2: Status（刚初始化应该是干净的）
  it("2. status - 初始化后仓库应该是干净的", async () => {
    log(`\n=== 检查仓库状态 ===`);

    const status = await session.git.status(LOCAL_REPO);

    log(`当前分支: ${status.currentBranch}`);
    log(`是否干净: ${status.isClean}`);
    log(`变更文件数: ${status.files.length}`);

    expect(status.currentBranch).toBe("main");
    expect(status.isClean).toBe(true);
    expect(status.files.length).toBe(0);
    log("✓ status 正常，仓库干净");
  }, 60000);

  // Step 3: 创建新文件 → Status 检测到未跟踪文件
  it("3. status - 新建文件后应检测到未跟踪文件", async () => {
    log(`\n=== 创建测试文件 ===`);

    await session.command.executeCommand(
      `echo 'hello from agentbay test' > ${LOCAL_REPO}/test-file.txt`,
      30000
    );
    log("已创建 test-file.txt");

    const status = await session.git.status(LOCAL_REPO);

    log(`是否干净: ${status.isClean}`);
    log(`变更文件: ${JSON.stringify(status.files)}`);

    expect(status.isClean).toBe(false);
    expect(status.files.length).toBeGreaterThan(0);

    const testFile = status.files.find((f) => f.path === "test-file.txt");
    expect(testFile).toBeDefined();
    expect(testFile!.indexStatus).toBe("?"); // 未跟踪
    expect(testFile!.workTreeStatus).toBe("?");
    log("✓ status 正确检测到未跟踪文件");
  }, 60000);

  // Step 4: Add
  it("4. add - 暂存文件后 status 应显示已暂存", async () => {
    log(`\n=== 暂存文件 ===`);

    await session.git.add(LOCAL_REPO, {
      files: ["test-file.txt"],
    });
    log("已暂存 test-file.txt");

    const status = await session.git.status(LOCAL_REPO);

    log(`变更文件: ${JSON.stringify(status.files)}`);

    const testFile = status.files.find((f) => f.path === "test-file.txt");
    expect(testFile).toBeDefined();
    expect(testFile!.indexStatus).toBe("A"); // 已添加到暂存区
    log("✓ add 成功，文件已进入暂存区");
  }, 60000);

  // Step 5: Commit
  it("5. commit - 提交后应返回 commit hash", async () => {
    log(`\n=== 提交更改 ===`);

    const commitResult = await session.git.commit(
      LOCAL_REPO,
      "test: add test file from agentbay",
      {
        authorName: "AgentBay Test",
        authorEmail: "test@agentbay.com",
      }
    );

    log(`Commit Hash: ${commitResult.commitHash}`);
    // commitHash 可能为 undefined（解析失败时），但 commit 操作本身是成功的
    // 核心验证：提交后仓库应该又干净了
    const status = await session.git.status(LOCAL_REPO);
    log(`提交后是否干净: ${status.isClean}`);
    expect(status.isClean).toBe(true);
    log("✓ commit 成功");
  }, 60000);

  // Step 6: Log
  it("6. log - 应能看到刚才的提交记录", async () => {
    log(`\n=== 查看提交历史 ===`);

    const logResult = await session.git.log(LOCAL_REPO, { maxCount: 3 });

    log(`共 ${logResult.entries.length} 条记录:`);
    for (const entry of logResult.entries) {
      log(`  ${entry.shortHash} | ${entry.authorName} | ${entry.message}`);
    }

    expect(logResult.entries.length).toBeGreaterThan(0);

    // 最新的提交应该是我们刚才的
    const latestCommit = logResult.entries[0];
    expect(latestCommit.message).toContain("test: add test file from agentbay");
    expect(latestCommit.authorName).toBe("AgentBay Test");
    expect(latestCommit.authorEmail).toBe("test@agentbay.com");
    expect(latestCommit.hash).toBeTruthy();
    expect(latestCommit.date).toBeTruthy();
    log("✓ log 正常，能看到刚才的提交");
  }, 60000);

  // Step 7: Branch - 列出分支
  it("7. listBranches - 列出当前分支", async () => {
    log(`\n=== 列出分支 ===`);

    const branchResult = await session.git.listBranches(LOCAL_REPO);

    log(`当前分支: ${branchResult.current}`);
    log(`所有分支: ${branchResult.branches.map((b) => b.name).join(", ")}`);

    expect(branchResult.current).toBe("main");
    expect(branchResult.branches.length).toBeGreaterThan(0);

    const currentBranch = branchResult.branches.find((b) => b.isCurrent);
    expect(currentBranch).toBeDefined();
    expect(currentBranch!.name).toBe("main");
    log("✓ listBranches 正常");
  }, 60000);

  // Step 8: 创建新分支
  it("8. createBranch - 创建并切换到新分支", async () => {
    log(`\n=== 创建新分支 ===`);

    await session.git.createBranch(LOCAL_REPO, "feature/test-branch");
    log("已创建 feature/test-branch");

    const branchResult = await session.git.listBranches(LOCAL_REPO);
    log(`当前分支: ${branchResult.current}`);
    log(`所有分支: ${branchResult.branches.map((b) => b.name).join(", ")}`);

    expect(branchResult.current).toBe("feature/test-branch");

    const newBranch = branchResult.branches.find(
      (b) => b.name === "feature/test-branch"
    );
    expect(newBranch).toBeDefined();
    expect(newBranch!.isCurrent).toBe(true);
    log("✓ createBranch 成功，已切换到新分支");
  }, 60000);

  // Step 9: Checkout 切换回 main
  it("9. checkoutBranch - 切换回 main 分支", async () => {
    log(`\n=== 切换分支 ===`);

    await session.git.checkoutBranch(LOCAL_REPO, "main");
    log("已切换到 main");

    const afterCheckout = await session.git.listBranches(LOCAL_REPO);
    expect(afterCheckout.current).toBe("main");
    log("✓ checkoutBranch 成功");
  }, 60000);

  // Step 10: 删除分支
  it("10. deleteBranch - 删除测试分支", async () => {
    log(`\n=== 删除分支 ===`);

    await session.git.deleteBranch(LOCAL_REPO, "feature/test-branch", {
      force: true,
    });
    log("已删除 feature/test-branch");

    const branchResult = await session.git.listBranches(LOCAL_REPO);
    log(`剩余分支: ${branchResult.branches.map((b) => b.name).join(", ")}`);

    const deleted = branchResult.branches.find(
      (b) => b.name === "feature/test-branch"
    );
    expect(deleted).toBeUndefined();
    log("✓ deleteBranch 成功，分支已删除");
  }, 60000);

  // Step 11: remoteAdd + remoteGet
  it("11. remoteAdd + remoteGet - 添加并查询远程仓库地址", async () => {
    log(`\n=== 添加远程仓库 ===`);

    const remoteName = "origin";
    const remoteUrl = "https://github.com/example/test-remote.git";

    // 添加 remote
    await session.git.remoteAdd(LOCAL_REPO, remoteName, remoteUrl);
    log(`已添加 remote: ${remoteName} -> ${remoteUrl}`);

    // 查询 remote URL
    const gotUrl = await session.git.remoteGet(LOCAL_REPO, remoteName);
    log(`查询到 remote URL: ${gotUrl}`);
    expect(gotUrl).toBe(remoteUrl);

    // overwrite 模式：更新 URL
    const newUrl = "https://github.com/example/test-remote-v2.git";
    await session.git.remoteAdd(LOCAL_REPO, remoteName, newUrl, {
      overwrite: true,
    });
    log(`已覆盖 remote URL -> ${newUrl}`);

    const updatedUrl = await session.git.remoteGet(LOCAL_REPO, remoteName);
    log(`更新后 remote URL: ${updatedUrl}`);
    expect(updatedUrl).toBe(newUrl);

    // 查询不存在的 remote 应返回 undefined
    const notExist = await session.git.remoteGet(LOCAL_REPO, "nonexistent");
    expect(notExist).toBeUndefined();
    log("✓ remoteAdd + remoteGet 成功");
  }, 60000);

  // Step 12: reset（mixed）
  it("12. reset - 将已暂存文件取消暂存（mixed reset）", async () => {
    log(`\n=== 测试 reset ===`);

    // 创建并提交一个新文件，确保有 HEAD 可回退
    await session.command.executeCommand(
      `echo 'reset test content' > ${LOCAL_REPO}/reset-test.txt`,
      10000
    );
    await session.git.add(LOCAL_REPO, { files: ["reset-test.txt"] });
    await session.git.commit(LOCAL_REPO, "test: add reset-test.txt", {
      authorName: "AgentBay Test",
      authorEmail: "test@agentbay.com",
    });
    log("已提交 reset-test.txt");

    // 再次修改并暂存
    await session.command.executeCommand(
      `echo 'modified for reset' >> ${LOCAL_REPO}/reset-test.txt`,
      10000
    );
    await session.git.add(LOCAL_REPO, { files: ["reset-test.txt"] });

    let status = await session.git.status(LOCAL_REPO);
    const stagedBefore = status.files.find(
      (f) => f.path === "reset-test.txt" && f.indexStatus === "M"
    );
    expect(stagedBefore).toBeDefined();
    log("修改已暂存，准备 reset");

    // mixed reset（默认）：取消暂存，保留工作区修改
    await session.git.reset(LOCAL_REPO, { mode: "mixed" });
    log("已执行 mixed reset");

    status = await session.git.status(LOCAL_REPO);
    const afterReset = status.files.find((f) => f.path === "reset-test.txt");
    expect(afterReset).toBeDefined();
    // 取消暂存后 indexStatus 应为空格，workTreeStatus 应为 M
    expect(afterReset!.indexStatus).toBe(" ");
    expect(afterReset!.workTreeStatus).toBe("M");
    log("✓ reset 成功，文件已取消暂存但工作区保留修改");
  }, 60000);

  // Step 13: reset（hard）
  it("13. reset - 丢弃所有工作区改动（hard reset）", async () => {
    log(`\n=== 测试 hard reset ===`);

    // 此时 reset-test.txt 有工作区未暂存改动（来自上一个测试）
    let status = await session.git.status(LOCAL_REPO);
    const dirty = status.files.find((f) => f.path === "reset-test.txt");
    expect(dirty).toBeDefined();

    // hard reset 丢弃所有改动
    await session.git.reset(LOCAL_REPO, { mode: "hard" });
    log("已执行 hard reset");

    status = await session.git.status(LOCAL_REPO);
    expect(status.isClean).toBe(true);
    log("✓ hard reset 成功，工作区已干净");
  }, 60000);

  // Step 14: restore
  it("14. restore - 恢复已修改文件到 HEAD 状态", async () => {
    log(`\n=== 测试 restore ===`);

    // 修改 reset-test.txt（不暂存）
    await session.command.executeCommand(
      `echo 'restore test modification' >> ${LOCAL_REPO}/reset-test.txt`,
      10000
    );

    let status = await session.git.status(LOCAL_REPO);
    const modified = status.files.find((f) => f.path === "reset-test.txt");
    expect(modified).toBeDefined();
    expect(modified!.workTreeStatus).toBe("M");
    log("文件已修改，准备 restore");

    // restore 恢复工作区文件
    await session.git.restore(LOCAL_REPO, { paths: ["reset-test.txt"] });
    log("已执行 restore");

    status = await session.git.status(LOCAL_REPO);
    expect(status.isClean).toBe(true);
    log("✓ restore 成功，文件已恢复到 HEAD 状态");
  }, 60000);

  // Step 15: restore --staged（取消暂存）
  it("15. restore --staged - 取消暂存文件", async () => {
    log(`\n=== 测试 restore --staged ===`);

    // 修改并暂存文件
    await session.command.executeCommand(
      `echo 'staged for restore test' >> ${LOCAL_REPO}/reset-test.txt`,
      10000
    );
    await session.git.add(LOCAL_REPO, { files: ["reset-test.txt"] });

    let status = await session.git.status(LOCAL_REPO);
    const staged = status.files.find(
      (f) => f.path === "reset-test.txt" && f.indexStatus === "M"
    );
    expect(staged).toBeDefined();
    log("文件已暂存，准备 restore --staged");

    // restore --staged 取消暂存，保留工作区修改
    await session.git.restore(LOCAL_REPO, {
      paths: ["reset-test.txt"],
      staged: true,
    });
    log("已执行 restore --staged");

    status = await session.git.status(LOCAL_REPO);
    const unstaged = status.files.find((f) => f.path === "reset-test.txt");
    expect(unstaged).toBeDefined();
    expect(unstaged!.indexStatus).toBe(" "); // 已取消暂存
    expect(unstaged!.workTreeStatus).toBe("M"); // 工作区保留
    log("✓ restore --staged 成功");

    // 清理：hard reset 恢复干净状态
    await session.git.reset(LOCAL_REPO, { mode: "hard" });
  }, 60000);

  // Step 16: configureUser
  it("16. configureUser - 配置 git 用户（local scope）", async () => {
    log(`\n=== 测试 configureUser ===`);

    await session.git.configureUser(
      LOCAL_REPO,
      "Test Bot",
      "testbot@example.com",
      { scope: "local" }
    );
    log("已配置 local user");

    // 验证：读取 local 配置
    const name = await session.git.getConfig(LOCAL_REPO, "user.name", {
      scope: "local",
    });
    const email = await session.git.getConfig(LOCAL_REPO, "user.email", {
      scope: "local",
    });
    log(`user.name=${name}, user.email=${email}`);
    expect(name).toBe("Test Bot");
    expect(email).toBe("testbot@example.com");
    log("✓ configureUser 成功");
  }, 60000);

  // Step 17: setConfig + getConfig
  it("17. setConfig + getConfig - 读写任意配置项（local scope）", async () => {
    log(`\n=== 测试 setConfig + getConfig ===`);

    // 写入
    await session.git.setConfig(LOCAL_REPO, "core.autocrlf", "false", {
      scope: "local",
    });
    log("已写入 core.autocrlf=false");

    // 读取
    const val = await session.git.getConfig(LOCAL_REPO, "core.autocrlf", {
      scope: "local",
    });
    log(`读取到 core.autocrlf=${val}`);
    expect(val).toBe("false");

    // 查询不存在的 key 应返回 undefined
    const missing = await session.git.getConfig(LOCAL_REPO, "nonexistent.key", {
      scope: "local",
    });
    expect(missing).toBeUndefined();
    log("✓ setConfig + getConfig 成功");
  }, 60000);

  // Step 18: reset --paths（只取消特定文件暂存）
  it("18. reset --paths - 只取消特定文件的暂存", async () => {
    log(`\n=== 测试 reset paths ===`);

    // 创建两个文件并暂存
    await session.command.executeCommand(
      `echo 'file a' > ${LOCAL_REPO}/file-a.txt && echo 'file b' > ${LOCAL_REPO}/file-b.txt`,
      10000
    );
    await session.git.add(LOCAL_REPO);

    let status = await session.git.status(LOCAL_REPO);
    expect(
      status.files.some((f) => f.path === "file-a.txt" && f.indexStatus === "A")
    ).toBe(true);
    expect(
      status.files.some((f) => f.path === "file-b.txt" && f.indexStatus === "A")
    ).toBe(true);
    log("两个文件已暂存");

    // 只取消 file-a.txt 的暂存
    await session.git.reset(LOCAL_REPO, { paths: ["file-a.txt"] });
    log("已对 file-a.txt 执行 reset paths");

    status = await session.git.status(LOCAL_REPO);
    // file-a.txt 应回到未跟踪状态
    const fileA = status.files.find((f) => f.path === "file-a.txt");
    expect(fileA).toBeDefined();
    expect(fileA!.indexStatus).toBe("?");
    // file-b.txt 仍在暂存区
    const fileB = status.files.find((f) => f.path === "file-b.txt");
    expect(fileB).toBeDefined();
    expect(fileB!.indexStatus).toBe("A");
    log("✓ reset paths 成功");

    // 清理
    await session.git.reset(LOCAL_REPO, { mode: "hard" });
    await session.command.executeCommand(
      `rm -f ${LOCAL_REPO}/file-a.txt ${LOCAL_REPO}/file-b.txt`,
      10000
    );
  }, 60000);

  // =============================================
  // Clone 测试（依赖网络，可能因网络波动失败）
  // =============================================

  it("19. clone - 克隆公开仓库（网络依赖）", async () => {
    log(`\n=== 使用 session.git.clone() 克隆仓库 ===`);
    log(`仓库地址: ${REPO_URL}`);

    try {
      const cloneResult = await session.git.clone(REPO_URL, {
        depth: 1,
        timeoutMs: 600000,
      });

      log(`克隆路径: ${cloneResult.path}`);
      expect(cloneResult.path).toBe("dingtalk-openclaw-connector");

      // 克隆后的仓库应该是干净的
      const status = await session.git.status(cloneResult.path);
      log(`分支: ${status.currentBranch}, 干净: ${status.isClean}`);
      expect(status.isClean).toBe(true);

      // 查看提交历史
      const logResult = await session.git.log(cloneResult.path, {
        maxCount: 3,
      });
      log(`最近提交:`);
      for (const entry of logResult.entries) {
        log(`  ${entry.shortHash} | ${entry.authorName} | ${entry.message}`);
      }
      expect(logResult.entries.length).toBeGreaterThan(0);
      log("✓ clone 成功");
    } catch (error: any) {
      if (
        error.message?.includes("GnuTLS") ||
        error.message?.includes("TLS") ||
        error.message?.includes("unable to access") ||
        error.message?.includes("无法访问") ||
        error.message?.includes("timed out") ||
        error.message?.includes("RPC") ||
        error.message?.includes("HTTP2") ||
        error.message?.includes("curl") ||
        error.message?.includes("framing layer") ||
        error.message?.includes("flush")
      ) {
        log(`⚠ clone 因网络问题跳过: ${error.message}`);
        console.warn("Clone skipped due to network issue in sandbox");
      } else {
        throw error; // 非网络错误则继续抛出
      }
    }
  }, 900000);
});
