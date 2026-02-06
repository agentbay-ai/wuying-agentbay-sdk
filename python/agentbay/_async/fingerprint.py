from typing import Any, Dict, List, Optional, Union

from .._common.logger import get_logger
from .._common.models.fingerprint import FingerprintFormat

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None  # type: ignore[misc, assignment]

# Global _logger for this module
_PLAYWRIGHT_REQUIRED_MSG = (
    "Playwright is required for this feature. "
    "Install it with: pip install wuying-agentbay-sdk[playwright] or poetry install --with playwright"
)
_logger = get_logger("fingerprint")


class AsyncBrowserFingerprintGenerator:
    """
    Browser fingerprint generator class.

    Args:
        headless: Whether to run browser in headless mode.
        use_chrome_channel: Whether to launch via the Chrome channel.
    """

    def __init__(self, headless: bool = False, use_chrome_channel: bool = True):
        """
        Initialize the fingerprint generator.

        Args:
            headless: Whether to run browser in headless mode
            use_chrome_channel: Whether to use Chrome channel
        """
        self.headless = headless
        self.use_chrome_channel = use_chrome_channel

    async def generate_fingerprint(self) -> Optional[FingerprintFormat]:
        """
        Extract comprehensive browser fingerprint using Playwright.

        Returns:
            Optional[FingerprintFormat]: FingerprintFormat object containing fingerprint and headers, or None if generation failed

        Example:
            generator = AsyncBrowserFingerprintGenerator(headless=True)
            fingerprint = await generator.generate_fingerprint()
            if fingerprint:
                print(fingerprint.headers.get("user-agent"))
        """
        try:
            if async_playwright is None:
                raise RuntimeError(_PLAYWRIGHT_REQUIRED_MSG)
            _logger.info("Starting fingerprint generation")

            async with async_playwright() as p:
                # Launch Chrome browser with specific options
                launch_options = {
                    "headless": self.headless,
                    "args": ["--start-maximized"],
                }

                if self.use_chrome_channel:
                    launch_options["channel"] = "chrome"

                browser = await p.chromium.launch(**launch_options)
                context = await browser.new_context(no_viewport=True)
                page = await context.new_page()

                # Navigate to a test page to ensure proper loading
                await page.goto("about:blank")

                _logger.info("Extracting comprehensive browser fingerprint...")

                # Extract comprehensive fingerprint data
                fingerprint_data = await self._extract_fingerprint_data(page)

                # Get request headers
                headers_data = await self._extract_headers_data(page)

                await browser.close()

                # Combine fingerprint and headers using FingerprintFormat
                fingerprint_format = FingerprintFormat._from_dict(
                    {"fingerprint": fingerprint_data, "headers": headers_data}
                )

                _logger.info("Fingerprint generation completed successfully!")
                return fingerprint_format

        except Exception as e:
            _logger.error(f"Error generating fingerprint: {e}")
            return None

    async def generate_fingerprint_to_file(
        self, output_filename: str = "fingerprint_output.json"
    ) -> bool:
        """
        Extract comprehensive browser fingerprint and save to file.

        Args:
            output_filename: Name of the file to save fingerprint data

        Returns:
            bool: True if fingerprint generation and saving succeeded, False otherwise

        Example:
            generator = AsyncBrowserFingerprintGenerator(use_chrome_channel=False)
            success = await generator.generate_fingerprint_to_file("browser_fp.json")
            print(f"Saved fingerprint: {success}")
        """
        try:
            _logger.info(
                f"Starting fingerprint generation, output file: {output_filename}"
            )

            # Generate fingerprint data (FingerprintFormat object)
            fingerprint_format = await self.generate_fingerprint()

            if fingerprint_format is None:
                _logger.error("Failed to generate fingerprint data")
                return False

            # Convert to JSON string and save to file
            fingerprint_json = fingerprint_format._to_json(indent=2, ensure_ascii=False)
            success = await self._save_to_file(fingerprint_json, output_filename)

            if success:
                _logger.info(
                    f"Fingerprint generation completed successfully! Saved to {output_filename}"
                )
                return True
            else:
                _logger.error("Failed to save fingerprint data")
                return False

        except Exception as e:
            _logger.error(f"Error generating fingerprint to file: {e}")
            return False

    async def _extract_fingerprint_data(self, page):
        """Extract fingerprint data from the page."""
        return await page.evaluate(
            """
        async () => {
            // Helper function to get audio codec support
            function getAudioCodecs() {
                const audio = document.createElement('audio');
                return {
                    ogg: audio.canPlayType('audio/ogg; codecs="vorbis"') || '',
                    mp3: audio.canPlayType('audio/mpeg') || '',
                    wav: audio.canPlayType('audio/wav; codecs="1"') || '',
                    m4a: audio.canPlayType('audio/x-m4a') || '',
                    aac: audio.canPlayType('audio/aac') || ''
                };
            }

            // Helper function to get video codec support
            function getVideoCodecs() {
                const video = document.createElement('video');
                return {
                    ogg: video.canPlayType('video/ogg; codecs="theora"') || '',
                    h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') || '',
                    webm: video.canPlayType('video/webm; codecs="vp8, vorbis"') || ''
                };
            }

            // Helper function to get plugins data
            function getPluginsData() {
                const plugins = [];
                const mimeTypes = [];

                for (let i = 0; i < navigator.plugins.length; i++) {
                    const plugin = navigator.plugins[i];
                    const pluginData = {
                        name: plugin.name,
                        description: plugin.description,
                        filename: plugin.filename,
                        mimeTypes: []
                    };

                    for (let j = 0; j < plugin.length; j++) {
                        const mimeType = plugin[j];
                        pluginData.mimeTypes.push({
                            type: mimeType.type,
                            suffixes: mimeType.suffixes,
                            description: mimeType.description,
                            enabledPlugin: plugin.name
                        });

                        mimeTypes.push(`${mimeType.description}~~${mimeType.type}~~${mimeType.suffixes}`);
                    }

                    plugins.push(pluginData);
                }

                return { plugins, mimeTypes };
            }

            // Helper function to get battery info
            async function getBatteryInfo() {
                try {
                    if ('getBattery' in navigator) {
                        const battery = await navigator.getBattery();
                        return {
                            charging: battery.charging,
                            chargingTime: battery.chargingTime,
                            dischargingTime: battery.dischargingTime,
                            level: battery.level
                        };
                    }
                } catch (e) {
                    console.log('Battery API not supported');
                }

                return {
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: null,
                    level: 1
                };
            }

            // Helper function to get WebGL info
            function getWebGLInfo() {
                try {
                    const canvas = document.createElement('canvas');
                    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

                    if (gl) {
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        return {
                            renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                            vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR)
                        };
                    }
                } catch (e) {
                    console.log('WebGL not supported');
                }

                return {
                    renderer: "Adreno (TM) 735",
                    vendor: "Qualcomm"
                };
            }

            // Helper function to get multimedia devices
            async function getMultimediaDevices() {
                try {
                    if ('mediaDevices' in navigator && 'enumerateDevices' in navigator.mediaDevices) {
                        const devices = await navigator.mediaDevices.enumerateDevices();
                        const speakers = [];
                        const micros = [];
                        const webcams = [];

                        devices.forEach(device => {
                            const deviceInfo = {
                                deviceId: device.deviceId || '',
                                kind: device.kind,
                                label: device.label || '',
                                groupId: device.groupId || ''
                            };

                            if (device.kind === 'audiooutput') {
                                speakers.push(deviceInfo);
                            } else if (device.kind === 'audioinput') {
                                micros.push(deviceInfo);
                            } else if (device.kind === 'videoinput') {
                                webcams.push(deviceInfo);
                            }
                        });

                        return { speakers, micros, webcams };
                    }
                } catch (e) {
                    console.log('Media devices not accessible');
                }

                return {
                    speakers: [{ deviceId: '', kind: 'audiooutput', label: '', groupId: '' }],
                    micros: [{ deviceId: '', kind: 'audioinput', label: '', groupId: '' }],
                    webcams: []
                };
            }

            // Helper function to get available fonts
            function getFonts() {
                // This is a simplified version - in practice, font detection is more complex
                const testFonts = [
                    'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
                    'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
                    'Trebuchet MS', 'Arial Black', 'Impact'
                ];

                const availableFonts = [];
                const testString = 'mmmmmmmmmmlli';
                const testSize = '72px';
                const baseWidth = {};
                const baseHeight = {};

                // Create a canvas for font testing
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');

                // Test with default fonts first
                const defaultFonts = ['monospace', 'sans-serif', 'serif'];
                defaultFonts.forEach(font => {
                    context.font = testSize + ' ' + font;
                    const metrics = context.measureText(testString);
                    baseWidth[font] = metrics.width;
                    baseHeight[font] = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
                });

                // Test each font
                testFonts.forEach(font => {
                    let detected = false;
                    defaultFonts.forEach(baseFont => {
                        context.font = testSize + ' ' + font + ', ' + baseFont;
                        const metrics = context.measureText(testString);
                        const width = metrics.width;
                        const height = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;

                        if (width !== baseWidth[baseFont] || height !== baseHeight[baseFont]) {
                            detected = true;
                        }
                    });

                    if (detected) {
                        availableFonts.push(font);
                    }
                });

                return availableFonts;
            }

            // Get battery info
            const batteryInfo = await getBatteryInfo();

            // Get multimedia devices
            const multimediaDevices = await getMultimediaDevices();

            // Build the complete fingerprint object
            const fingerprint = {
                screen: {
                    availTop: screen.availTop,
                    availLeft: screen.availLeft,
                    pageXOffset: window.pageXOffset,
                    pageYOffset: window.pageYOffset,
                    screenX: window.screenX,
                    hasHDR: screen.colorDepth > 24,
                    width: screen.width,
                    height: screen.height,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight,
                    clientWidth: document.documentElement.clientWidth,
                    clientHeight: document.documentElement.clientHeight,
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight,
                    outerWidth: window.outerWidth,
                    outerHeight: window.outerHeight,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth,
                    devicePixelRatio: window.devicePixelRatio
                },
                navigator: {
                    userAgent: navigator.userAgent,
                    userAgentData: navigator.userAgentData ? {
                        brands: navigator.userAgentData.brands || [],
                        mobile: navigator.userAgentData.mobile || false,
                        platform: navigator.userAgentData.platform || ''
                    } : null,
                    language: navigator.language,
                    languages: navigator.languages || [],
                    platform: navigator.platform,
                    deviceMemory: navigator.deviceMemory || 8,
                    hardwareConcurrency: navigator.hardwareConcurrency || 8,
                    maxTouchPoints: navigator.maxTouchPoints || 0,
                    product: navigator.product,
                    productSub: navigator.productSub,
                    vendor: navigator.vendor,
                    vendorSub: navigator.vendorSub,
                    doNotTrack: navigator.doNotTrack,
                    appCodeName: navigator.appCodeName,
                    appName: navigator.appName,
                    appVersion: navigator.appVersion,
                    oscpu: navigator.oscpu,
                    extraProperties: {
                        vendorFlavors: ['chrome'],
                        globalPrivacyControl: navigator.globalPrivacyControl || null,
                        pdfViewerEnabled: navigator.pdfViewerEnabled || true,
                        installedApps: []
                    },
                    webdriver: false
                },
                audioCodecs: getAudioCodecs(),
                videoCodecs: getVideoCodecs(),
                pluginsData: getPluginsData(),
                battery: batteryInfo,
                videoCard: getWebGLInfo(),
                multimediaDevices: multimediaDevices,
                fonts: getFonts(),
                mockWebRTC: false,
                slim: false
            };

            return fingerprint;
        }
        """
        )

    async def _extract_headers_data(self, page):
        """Extract headers data from httpbin."""
        try:
            _logger.info("Getting request headers...")
            await page.goto("https://httpbin.org/headers", wait_until="networkidle")

            # Extract headers from the response
            all_headers = await page.evaluate(
                """
            () => {
                try {
                    const preElement = document.querySelector('pre');
                    if (preElement) {
                        const data = JSON.parse(preElement.textContent);
                        return data.headers || {};
                    }
                } catch (e) {
                    console.log('Failed to parse headers:', e);
                }
                return {};
            }
            """
            )

            # Filter only the key headers from the example
            key_headers = [
                "sec-ch-ua",
                "sec-ch-ua-mobile",
                "sec-ch-ua-platform",
                "upgrade-insecure-requests",
                "user-agent",
                "accept",
                "sec-fetch-site",
                "sec-fetch-mode",
                "sec-fetch-user",
                "sec-fetch-dest",
                "accept-encoding",
                "accept-language",
            ]

            headers_data = {}
            # Convert all_headers keys to lowercase for case-insensitive matching
            all_headers_lower = {k.lower(): v for k, v in all_headers.items()}

            for header in key_headers:
                header_lower = header.lower()
                if header_lower in all_headers_lower:
                    headers_data[header] = all_headers_lower[header_lower]

            return headers_data

        except Exception as e:
            _logger.warning(f"Failed to extract headers: {e}")
            return {}

    async def _save_to_file(self, json_data, filename):
        """Save JSON string data to a file."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_data)
            _logger.info(f"Fingerprint data saved to {filename}")
            return True
        except Exception as e:
            _logger.error(f"Failed to save fingerprint data: {e}")
            return False
