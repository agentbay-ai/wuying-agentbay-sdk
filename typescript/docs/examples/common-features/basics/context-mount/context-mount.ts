#!/usr/bin/env node

/**
 * AgentBay SDK - Context Mount Example
 *
 * This example demonstrates the Context Mount (direct-mount persistence) feature:
 * - Mounting a context at session creation time
 * - Write-through persistence (no manual sync needed)
 * - Cross-session data persistence via mount
 * - Dynamic mounting using bind()
 */

import type { CreateSessionParams } from 'wuying-agentbay-sdk';
import { AgentBay, ContextMount, logError } from 'wuying-agentbay-sdk';

async function main(): Promise<void> {
    console.log('📌 AgentBay Context Mount Example');

    const apiKey = process.env.AGENTBAY_API_KEY || '';
    if (!apiKey) {
        console.log('❌ Please set AGENTBAY_API_KEY environment variable');
        process.exit(1);
    }

    const agentBay = new AgentBay({ apiKey });

    try {
        await contextMountDemo(agentBay);
    } catch (error) {
        console.log(`❌ Example execution failed: ${error}`);
        logError('Error:', error);
    }

    console.log('✅ Context mount example completed');
}

async function contextMountDemo(agentBay: AgentBay): Promise<void> {
    console.log('\n🔄 === Context Mount Demonstration ===');

    // Step 1: Create a context for persistent storage
    console.log('\n📦 Step 1: Creating context for persistent storage...');
    const contextName = `mount-demo-${Date.now()}`;
    const contextResult = await agentBay.context.get(contextName, true);

    if (!contextResult.success) {
        console.log(`❌ Context creation failed: ${contextResult.errorMessage}`);
        return;
    }

    const context = contextResult.context;
    console.log(`✅ Context created: ${context.id} (name: ${context.name})`);

    // Step 2: Create first session with context mount
    console.log('\n🔧 Step 2: Creating first session with context mount...');
    const contextMount = new ContextMount(context.id, '/tmp/mounted_data');

    const params1: CreateSessionParams = {
        contextMount: [contextMount]
    };
    const session1Result = await agentBay.create(params1);

    if (!session1Result.success) {
        console.log(`❌ First session creation failed: ${session1Result.errorMessage}`);
        return;
    }

    const session1 = session1Result.session;
    console.log(`✅ First session created: ${session1.sessionId}`);

    const session1Id = session1.sessionId;
    try {
        // Step 3: Write data — persisted immediately via write-through
        console.log('\n💾 Step 3: Writing data (write-through persistence)...');

        await session1.command.executeCommand('mkdir -p /tmp/mounted_data/config');

        const configData = {
            app: 'mount-demo',
            version: '1.0',
            session: session1.sessionId
        };

        const configResult = await session1.fileSystem.writeFile(
            '/tmp/mounted_data/config/app.json',
            JSON.stringify(configData, null, 2)
        );
        if (configResult.success) {
            console.log('✅ Config file written (persisted immediately)');
        } else {
            console.log(`❌ Failed to write config: ${configResult.errorMessage}`);
        }

        const dataResult = await session1.fileSystem.writeFile(
            '/tmp/mounted_data/notes.txt',
            'This data is persisted via Context Mount.\nNo manual sync() call needed!'
        );
        if (dataResult.success) {
            console.log('✅ Data file written (persisted immediately)');
        } else {
            console.log(`❌ Failed to write data: ${dataResult.errorMessage}`);
        }

        // List files
        console.log('\n📋 Files in mounted path:');
        const listResult = await session1.command.executeCommand('find /tmp/mounted_data -type f -ls');
        if (listResult.success) {
            console.log(listResult.output);
        }

    } finally {
        // No sync needed — data is already persisted
        console.log('\n🧹 Deleting first session (no sync needed for mount)...');
        const deleteResult1 = await agentBay.delete(session1);
        if (deleteResult1.success) {
            console.log('✅ First session deleted');
        } else {
            console.log(`❌ First session deletion failed: ${deleteResult1.errorMessage}`);
        }
    }

    // Step 4: Create second session to verify cross-session persistence
    console.log('\n🔧 Step 4: Creating second session to verify persistence...');

    const params2: CreateSessionParams = {
        contextMount: [contextMount]
    };
    const session2Result = await agentBay.create(params2);

    if (!session2Result.success) {
        console.log(`❌ Second session creation failed: ${session2Result.errorMessage}`);
        return;
    }

    const session2 = session2Result.session;
    console.log(`✅ Second session created: ${session2.sessionId}`);

    try {
        console.log('\n🔍 Step 5: Verifying persisted data in second session...');

        const filesToCheck = [
            '/tmp/mounted_data/config/app.json',
            '/tmp/mounted_data/notes.txt',
        ];

        let filesFound = 0;

        for (const filePath of filesToCheck) {
            console.log(`\n🔍 Checking: ${filePath}`);
            const readResult = await session2.fileSystem.readFile(filePath);

            if (readResult.success) {
                console.log('✅ File found!');
                const preview = readResult.content.substring(0, 120);
                console.log(`   📄 Content: ${preview}`);
                filesFound++;
            } else {
                console.log(`❌ Not found: ${readResult.errorMessage}`);
            }
        }

        // Step 6: Dynamic mount demo (bind)
        console.log('\n🔧 Step 6: Dynamic mount using bind()...');
        const dynamicCtxResult = await agentBay.context.get(`dynamic-mount-${Date.now()}`, true);
        if (dynamicCtxResult.success) {
            const dynamicMount = new ContextMount(dynamicCtxResult.context.id, '/tmp/dynamic_mount');
            const bindResult = await session2.context.bind(dynamicMount);
            if (bindResult.success) {
                console.log('✅ Dynamic mount bound successfully');
                const writeResult = await session2.fileSystem.writeFile(
                    '/tmp/dynamic_mount/dynamic.txt',
                    'Dynamically mounted data!'
                );
                if (writeResult.success) {
                    console.log('✅ Wrote to dynamically mounted path');
                }
            } else {
                console.log(`❌ Dynamic bind failed: ${bindResult.errorMessage}`);
            }

            // Clean up dynamic context
            await agentBay.context.delete(dynamicCtxResult.context);
        }

        // Summary
        console.log('\n📊 === Persistence Summary ===');
        console.log(`✅ Context ID: ${context.id}`);
        console.log(`✅ Session 1: ${session1Id} (deleted)`);
        console.log(`✅ Session 2: ${session2.sessionId} (active)`);
        console.log(`✅ Files found: ${filesFound}/${filesToCheck.length}`);

        if (filesFound === filesToCheck.length) {
            console.log('🎉 Context Mount persistence verification SUCCESSFUL!');
        } else {
            console.log('⚠️  Some files not found — mount may still be initializing');
        }

    } finally {
        console.log('\n🧹 Cleaning up second session...');
        const deleteResult2 = await agentBay.delete(session2);
        if (deleteResult2.success) {
            console.log('✅ Second session deleted');
        }
    }

    // Clean up context
    console.log('\n🧹 Cleaning up context...');
    const deleteCtxResult = await agentBay.context.delete(context);
    if (deleteCtxResult.success) {
        console.log(`✅ Context deleted`);
    }
}

if (require.main === module) {
    main().catch(error => {
        logError('Error in main execution:', error);
        process.exit(1);
    });
}
