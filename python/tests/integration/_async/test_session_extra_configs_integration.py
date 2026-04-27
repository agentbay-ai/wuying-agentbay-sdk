"""Integration tests for session creation with extra configurations."""

import pytest

from agentbay import (
    AppManagerRule,
    AsyncAgentBay,
    CreateSessionParams,
    ExtraConfigs,
    MobileExtraConfig,
)


@pytest.mark.asyncio
async def test_create_session_with_mobile_extra_configs_integration(make_session):
    """Integration test for creating a mobile session with extra configurations."""
    print("=" * 80)
    print("TEST: Mobile Session with Extra Configurations")
    print("=" * 80)

    print("Step 1: Creating mobile configuration with extra configs...")
    app_rule = AppManagerRule(
        rule_type="White",
        app_package_name_list=["com.android.settings", "com.example.test.app"],
    )
    mobile_config = MobileExtraConfig(
        lock_resolution=True,
        app_manager_rule=app_rule,
        hide_navigation_bar=True,
        uninstall_blacklist=[
            "com.android.systemui",
            "com.android.settings",
        ],
    )
    extra_configs = ExtraConfigs(mobile=mobile_config)
    print(
        f"Mobile config created: lock_resolution={mobile_config.lock_resolution}, "
        f"hide_navigation_bar={mobile_config.hide_navigation_bar}, "
        f"uninstall_blacklist={len(mobile_config.uninstall_blacklist)} packages, "
        f"app_rule={mobile_config.app_manager_rule.rule_type}"
    )

    params = CreateSessionParams(
        image_id="mobile_latest",
        labels={
            "test_type": "mobile_extra_configs_integration",
            "created_by": "integration_test",
        },
        extra_configs=extra_configs,
    )
    print(f"Session params: image_id={params.image_id}, labels={params.labels}")

    print("Step 2: Creating mobile session with extra configurations...")
    lc = await make_session(params=params)
    session = lc._result.session

    print(f"Mobile session created successfully with ID: {session.session_id}")

    # Step 3: Verify session properties
    print("Step 3: Verifying session properties...")
    assert session.session_id is not None
    assert len(session.session_id) > 0, "Session ID should not be empty"
    print(f"Session properties verified: ID={session.session_id}")

    # Step 4: Verify mobile environment
    print("Step 4: Verifying mobile environment...")
    info_result = await session.info()
    if info_result.success:
        resource_url = info_result.data.resource_url.lower()
        assert "android" in resource_url or "mobile" in resource_url, \
            f"Session should be mobile-based, got URL: {info_result.data.resource_url}"
        print(f"Mobile environment verified (RequestID: {info_result.request_id})")
    else:
        print(f"Failed to get session info: {info_result.error_message}")

    # Step 5: Verify labels
    print("Step 5: Verifying session labels...")
    labels_result = await session.get_labels()
    if labels_result.success:
        labels = labels_result.data
        assert labels.get("test_type") == "mobile_extra_configs_integration"
        print(f"Labels verified: {labels} (RequestID: {labels_result.request_id})")
    else:
        print(f"Failed to get session labels: {labels_result.error_message}")

    # Step 6: Test mobile functionality
    print("Step 6: Testing mobile functionality...")
    screenshot_result = await session.mobile.screenshot()
    if screenshot_result.success:
        assert screenshot_result.data is not None
        print(f"Mobile screenshot working (RequestID: {screenshot_result.request_id})")
    else:
        print(f"Mobile screenshot failed: {screenshot_result.error_message}")

    # Step 7: Test mobile configuration methods
    print("Step 7: Testing mobile configuration methods...")
    try:
        await session.mobile.set_resolution_lock(True)
        await session.mobile.set_navigation_bar_visibility(True)
        await session.mobile.set_uninstall_blacklist(["com.android.systemui"])
        print("Mobile configuration methods executed successfully")
    except Exception as e:
        print(f"Mobile configuration methods failed: {e}")

    print("Mobile extra configs integration test completed successfully")
