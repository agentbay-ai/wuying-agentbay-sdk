"""Integration tests for OSS (Object Storage Service) operations."""

import os

import pytest

from agentbay import CreateSessionParams


def _get_oss_credentials() -> dict:
    """Get OSS credentials from environment variables or use defaults."""
    return {
        "access_key_id": os.getenv("OSS_ACCESS_KEY_ID", "test-access-key-id"),
        "access_key_secret": os.getenv("OSS_ACCESS_KEY_SECRET", "test-access-key-secret"),
        "security_token": os.getenv("OSS_SECURITY_TOKEN", "test-security-token"),
        "endpoint": os.getenv("OSS_ENDPOINT", "https://oss-cn-hangzhou.aliyuncs.com"),
        "region": os.getenv("OSS_REGION", "cn-hangzhou"),
    }


@pytest.mark.asyncio
async def test_env_init(make_session):
    """Test OSS environment initialization."""
    params = CreateSessionParams(image_id="code_latest")
    lc = await make_session(params=params)
    session = lc._result.session

    if not session.oss:
        pytest.skip("OSS interface is not available")

    print("Initializing OSS environment...")
    credentials = _get_oss_credentials()
    result = await session.oss.env_init(
        credentials["access_key_id"],
        credentials["access_key_secret"],
        credentials["security_token"],
        credentials["endpoint"],
        credentials["region"],
    )
    print(f"EnvInit result: {result}")
    assert result.success
    assert result.request_id is not None
    assert result.client_config is not None


@pytest.mark.asyncio
async def test_upload(make_session):
    """Test OSS file upload."""
    params = CreateSessionParams(image_id="code_latest")
    lc = await make_session(params=params)
    session = lc._result.session

    if not session.oss or not session.file_system:
        pytest.skip("OSS or FileSystem interface is not available")

    credentials = _get_oss_credentials()
    init_result = await session.oss.env_init(
        credentials["access_key_id"],
        credentials["access_key_secret"],
        credentials["security_token"],
        credentials["endpoint"],
        credentials["region"],
    )
    assert init_result.success

    test_content = "This is a test file for OSS upload."
    test_file_path = "/tmp/test_oss_upload.txt"
    await session.file_system.write_file(test_file_path, test_content, "overwrite")

    print("Uploading file to OSS...")
    bucket = os.getenv("OSS_TEST_BUCKET", "test-bucket")
    object_key = "test-object.txt"
    result = await session.oss.upload(bucket, object_key, test_file_path)
    print(f"Upload result: {result}")
    assert result.success
    assert result.request_id is not None
    assert "Upload success" in result.content


@pytest.mark.asyncio
async def test_upload_anonymous(make_session):
    """Test OSS anonymous file upload."""
    params = CreateSessionParams(image_id="code_latest")
    lc = await make_session(params=params)
    session = lc._result.session

    if not session.oss or not session.file_system:
        pytest.skip("OSS or FileSystem interface is not available")

    test_content = "This is a test file for OSS anonymous upload."
    test_file_path = "/tmp/test_oss_upload_anon.txt"
    await session.file_system.write_file(test_file_path, test_content, "overwrite")

    print("Uploading file anonymously...")
    upload_url = os.getenv(
        "OSS_TEST_UPLOAD_URL", "https://example.com/upload/test-file.txt"
    )
    result = await session.oss.upload_anonymous(upload_url, test_file_path)
    print(f"UploadAnonymous result: {result}")
    assert result.success
    assert result.request_id is not None
    assert "Upload success" in result.content


@pytest.mark.asyncio
async def test_download(make_session):
    """Test OSS file download."""
    params = CreateSessionParams(image_id="code_latest")
    lc = await make_session(params=params)
    session = lc._result.session

    if not session.oss or not session.file_system:
        pytest.skip("OSS or FileSystem interface is not available")

    credentials = _get_oss_credentials()
    print(f"credentials: {credentials}")
    init_result = await session.oss.env_init(
        credentials["access_key_id"],
        credentials["access_key_secret"],
        credentials["security_token"],
        credentials["endpoint"],
        credentials["region"],
    )
    assert init_result.success

    print("Downloading file from OSS...")
    bucket = os.getenv("OSS_TEST_BUCKET", "test-bucket")
    object_key = "test-object.txt"
    download_path = "/tmp/test_oss_download.txt"
    result = await session.oss.download(bucket, object_key, download_path)

    assert result.success
    assert result.request_id is not None
    assert "Download success" in result.content

    file_info = await session.file_system.get_file_info(download_path)
    assert file_info is not None


@pytest.mark.asyncio
async def test_download_anonymous(make_session):
    """Test OSS anonymous file download."""
    params = CreateSessionParams(image_id="code_latest")
    lc = await make_session(params=params)
    session = lc._result.session

    if not session.oss or not session.file_system:
        pytest.skip("OSS or FileSystem interface is not available")

    print("Downloading file anonymously...")
    download_url = os.getenv(
        "OSS_TEST_DOWNLOAD_URL",
        "https://example.com/download/test-file.txt",
    )
    download_path = "/tmp/test_oss_download_anon.txt"
    result = await session.oss.download_anonymous(download_url, download_path)
    print(f"DownloadAnonymous result: {result}")
    assert result.success
    assert result.request_id is not None
    assert "Download success" in result.content

    file_info = await session.file_system.get_file_info(download_path)
    assert file_info is not None
