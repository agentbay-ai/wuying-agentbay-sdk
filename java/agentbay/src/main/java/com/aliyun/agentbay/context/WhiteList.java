package com.aliyun.agentbay.context;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Defines the white list configuration
 *
 * Attributes:
 *     path: Path to include in the white list.
 *         When isPathRegex is false (default), this must be an exact absolute directory path
 *         and wildcard characters are not allowed.
 *         When isPathRegex is true, this is treated as a regex pattern (e.g. "/home/wuying/.*").
 *     excludePaths: Paths to exclude from the white list.
 *         When isExcludeRegex is false (default), these must be relative directory paths
 *         and wildcard characters are not allowed.
 *         When isExcludeRegex is true, these are treated as regex patterns.
 *         NOTE: exclude paths are RELATIVE to the white-listed path, not absolute.
 *     isPathRegex: If true, path is interpreted as a regex pattern.
 *         If false (default), path is an absolute directory path.
 *     isExcludeRegex: If true, excludePaths entries are interpreted as regex patterns.
 *         If false (default), excludePaths entries are relative directory paths.
 */
public class WhiteList {
    private String path = "";
    private List<String> excludePaths = new ArrayList<>();
    private boolean isPathRegex = false;
    private boolean isExcludeRegex = false;

    public WhiteList() {
    }

    public WhiteList(String path, List<String> excludePaths) {
        this.path = path;
        this.excludePaths = excludePaths != null ? excludePaths : new ArrayList<>();
        validate();
    }

    public WhiteList(String path, List<String> excludePaths, boolean isPathRegex, boolean isExcludeRegex) {
        this.path = path;
        this.excludePaths = excludePaths != null ? excludePaths : new ArrayList<>();
        this.isPathRegex = isPathRegex;
        this.isExcludeRegex = isExcludeRegex;
        validate();
    }

    /**
     * Validate that non-regex paths don't contain wildcard patterns.
     * Equivalent to Python's WhiteList.__post_init__.
     */
    private void validate() {
        if (!isPathRegex && containsWildcard(path)) {
            throw new IllegalArgumentException(
                "Wildcard patterns are not supported in path when isPathRegex=false. Got: " + path + ". "
                + "Please use exact directory paths or set isPathRegex=true for regex matching."
            );
        }
        if (!isExcludeRegex) {
            for (String excludePath : excludePaths) {
                if (containsWildcard(excludePath)) {
                    throw new IllegalArgumentException(
                        "Wildcard patterns are not supported in excludePaths when isExcludeRegex=false. "
                        + "Got: " + excludePath + ". "
                        + "Please use exact directory paths or set isExcludeRegex=true for regex matching."
                    );
                }
            }
        }
    }

    /** Check if a path string contains wildcard characters (* ? [ ]). */
    private static final Pattern WILDCARD_PATTERN = Pattern.compile("[*?\\[\\]]");

    private static boolean containsWildcard(String path) {
        return path != null && WILDCARD_PATTERN.matcher(path).find();
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        if (!isPathRegex && containsWildcard(path)) {
            throw new IllegalArgumentException(
                "Wildcard patterns are not supported in path when isPathRegex=false. Got: " + path + ". "
                + "Please use exact directory paths or set isPathRegex=true for regex matching."
            );
        }
        this.path = path;
    }

    public List<String> getExcludePaths() {
        return excludePaths;
    }

    public void setExcludePaths(List<String> excludePaths) {
        List<String> paths = excludePaths != null ? excludePaths : new ArrayList<>();
        if (!isExcludeRegex) {
            for (String p : paths) {
                if (containsWildcard(p)) {
                    throw new IllegalArgumentException(
                        "Wildcard patterns are not supported in excludePaths when isExcludeRegex=false. "
                        + "Got: " + p + ". "
                        + "Please use exact directory paths or set isExcludeRegex=true for regex matching."
                    );
                }
            }
        }
        this.excludePaths = paths;
    }

    public boolean isPathRegex() {
        return isPathRegex;
    }

    public void setPathRegex(boolean isPathRegex) {
        this.isPathRegex = isPathRegex;
    }

    public boolean isExcludeRegex() {
        return isExcludeRegex;
    }

    public void setExcludeRegex(boolean isExcludeRegex) {
        this.isExcludeRegex = isExcludeRegex;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("path", path);
        map.put("excludePaths", excludePaths);
        map.put("isPathRegex", isPathRegex);
        map.put("isExcludeRegex", isExcludeRegex);
        return map;
    }
}
