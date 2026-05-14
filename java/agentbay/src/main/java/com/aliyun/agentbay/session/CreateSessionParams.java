package com.aliyun.agentbay.session;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import com.aliyun.agentbay.browser.BrowserContext;
import com.aliyun.agentbay.context.ContextMount;
import com.aliyun.agentbay.context.ContextSync;
import com.aliyun.agentbay.model.ExtraConfigs;

/**
 * Parameters for creating a new session in the AgentBay cloud environment.
 *
 * <p>Supports various configuration options including labels, context synchronization,
 * browser context, policy management, browser replay, and mobile extra configurations.</p>
 *
 * @see BrowserContext
 * @see ContextSync
 * @see ExtraConfigs
 */
public class CreateSessionParams {

    /** ID of the image to use for the session. */
    private String imageId;

    /**
     * SDK-side idle release timeout in seconds.
     *
     * @deprecated Prefer {@link #lifecyclePolicy} (minutes-based full lifecycle control).
     * Cannot be used together with {@link #lifecyclePolicy}.
     */
    @Deprecated
    private Integer idleReleaseTimeout;

    /**
     * Full lifecycle policy (idle and max runtime in minutes, optional manual release).
     * Mutually exclusive with {@link #idleReleaseTimeout}.
     */
    private LifecyclePolicy lifecyclePolicy;

    /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
    private Map<String, String> labels;

    /**
     * List of context synchronization configurations that define how contexts
     * should be synchronized and mounted.
     */
    private List<ContextSync> contextSyncs;

    /** List of context mount configurations for direct-mount persistence. */
    private List<ContextMount> contextMounts;

    /** Optional configuration for browser data synchronization. */
    private BrowserContext browserContext;

    /**
     * Framework name for tracking (e.g., "langchain").
     * Defaults to empty string (direct call).
     */
    private String framework;

    /** Policy id to apply when creating the session. */
    private String policyId;

    /**
     * Whether to enable browser recording for the session.
     * When null (not set), server-side default behavior applies.
     * Set to true to enable, false to disable.
     */
    private Boolean enableBrowserReplay;

    /** Advanced configuration parameters for mobile environments. */
    private ExtraConfigs extraConfigs;

    /** Beta network ID to bind this session to. */
    private String betaNetworkId;

    /** Whether to load skills into the sandbox. */
    private Boolean loadSkills;

    /** Skill names to load. Loads all visible skills when loadSkills=true and this is not specified. */
    private List<String> skillNames;

    /**
     * Create a new CreateSessionParams instance with default values(contextSyncs: empty list,idleReleaseTimeout: 300 seconds).
     *
     */
    public CreateSessionParams() {
        this.contextSyncs = new ArrayList<>();
        this.contextMounts = new ArrayList<>();
        this.labels = new java.util.HashMap<>();
    }

    /**
     * Set the browser context and automatically merge extension and fingerprint context syncs.
     *
     * @param browserContext Browser context configuration
     */
    public void setBrowserContext(BrowserContext browserContext) {
        this.browserContext = browserContext;

        if (browserContext != null) {
            // Initialize contextSyncs if null
            if (this.contextSyncs == null) {
                this.contextSyncs = new ArrayList<>();
            }

            // Add extension context syncs from browser_context if available
            List<ContextSync> extensionSyncs = browserContext.getExtensionContextSyncs();
            if (extensionSyncs != null && !extensionSyncs.isEmpty()) {
                this.contextSyncs.addAll(extensionSyncs);
            }

            // Add fingerprint context sync from browser_context if available
            ContextSync fingerprintSync = browserContext.getFingerprintContextSync();
            if (fingerprintSync != null) {
                this.contextSyncs.add(fingerprintSync);
            }
        }
    }

    /**
     * Get the ID of the image to use for the session.
     *
     * @return image ID, or null if not set
     */
    public String getImageId() {
        return imageId;
    }

    /**
     * Set the ID of the image to use for the session.
     *
     * @param imageId image ID
     */
    public void setImageId(String imageId) {
        this.imageId = imageId;
    }

    /**
     * Get the SDK-side idle release timeout in seconds.
     *
     * @return idle release timeout in seconds, or null if not set
     * @deprecated Use {@link #getLifecyclePolicy()} for minutes-based lifecycle control.
     */
    @Deprecated
    public Integer getIdleReleaseTimeout() {
        return idleReleaseTimeout;
    }

    /**
     * Set the SDK-side idle release timeout in seconds.
     *
     * @param idleReleaseTimeout idle release timeout in seconds
     * @deprecated Use {@link #setLifecyclePolicy(LifecyclePolicy)} for minutes-based lifecycle control.
     * @throws IllegalArgumentException if {@link #lifecyclePolicy} is already set
     */
    @Deprecated
    public void setIdleReleaseTimeout(Integer idleReleaseTimeout) {
        if (idleReleaseTimeout != null && lifecyclePolicy != null) {
            throw new IllegalArgumentException(
                "lifecyclePolicy cannot be used together with idleReleaseTimeout");
        }
        this.idleReleaseTimeout = idleReleaseTimeout;
    }

    /**
     * Gets the lifecycle policy (minutes-based), if set.
     *
     * @return lifecycle policy, or null
     */
    public LifecyclePolicy getLifecyclePolicy() {
        return lifecyclePolicy;
    }

    /**
     * Sets the lifecycle policy. Mutually exclusive with {@link #idleReleaseTimeout}.
     *
     * @param lifecyclePolicy lifecycle configuration
     * @throws IllegalArgumentException if idle release timeout was already set (non-null)
     */
    public void setLifecyclePolicy(LifecyclePolicy lifecyclePolicy) {
        if (lifecyclePolicy != null && idleReleaseTimeout != null) {
            throw new IllegalArgumentException(
                "idleReleaseTimeout cannot be used together with lifecyclePolicy");
        }
        this.lifecyclePolicy = lifecyclePolicy;
    }

    /**
     * Get the custom labels for the Session.
     *
     * @return labels map, or null if not set
     */
    public Map<String, String> getLabels() {
        return labels;
    }

    /**
     * Set the custom labels for the Session.
     *
     *
     * @param labels labels map
     */
    public void setLabels(Map<String, String> labels) {
        this.labels = labels != null ? labels : new java.util.HashMap<>();
    }

    /**
     * Get the list of context synchronization configurations.
     *
     *
     * @return list of context syncs, or null if not set
     */
    public List<ContextSync> getContextSyncs() {
        return contextSyncs;
    }

    /**
     * Set the list of context synchronization configurations.
     *
     * @param contextSyncs list of context syncs
     */
    public void setContextSyncs(List<ContextSync> contextSyncs) {
        this.contextSyncs = contextSyncs;
    }

    /**
     * Get the list of context mount configurations.
     *
     * @return list of context mounts, or empty list if not set
     */
    public List<ContextMount> getContextMounts() {
        return contextMounts;
    }

    /**
     * Set the list of context mount configurations.
     *
     * @param contextMounts list of context mounts
     */
    public void setContextMounts(List<ContextMount> contextMounts) {
        this.contextMounts = contextMounts;
    }

    /**
     * Get the browser context configuration.
     *
     * @return browser context, or null if not set
     */
    public BrowserContext getBrowserContext() {
        return browserContext;
    }

    /**
     * Get the framework name (e.g., "langchain").
     * This is used for SDK statistics tracking.
     *
     * @return framework name, or null if not set
     */
    public String getFramework() {
        return framework;
    }

    /**
     * Set the framework name (e.g., "langchain").
     * This is used for SDK statistics tracking.
     *
     * @param framework framework name
     */
    public void setFramework(String framework) {
        this.framework = framework;
    }

    /**
     * Get the policy ID to apply when creating the session.
     *
     * @return Policy ID, or null if not set
     */
    public String getPolicyId() {
        return policyId;
    }

    /**
     * Set the policy ID to apply when creating the session.
     *
     * @param policyId Policy ID
     */
    public void setPolicyId(String policyId) {
        this.policyId = policyId;
    }

    /**
     * Get whether browser replay recording is enabled.
     *
     * @return true if enabled, false if disabled, null if not set
     */
    public Boolean getEnableBrowserReplay() {
        return enableBrowserReplay;
    }

    /**
     * Set whether to enable browser replay recording for the session.
     *
     * @param enableBrowserReplay true to enable, false to disable
     */
    public void setEnableBrowserReplay(Boolean enableBrowserReplay) {
        this.enableBrowserReplay = enableBrowserReplay;
    }

    /**
     * Get Advanced configuration parameters for mobile environments.
     *
     * @return ExtraConfigs instance, or null if not set
     */
    public ExtraConfigs getExtraConfigs() {
        return extraConfigs;
    }

    /**
     * Set Advanced configuration parameters for mobile environments.
     *
     * @param extraConfigs Advanced configuration parameters
     * @see ExtraConfigs
     */
    public void setExtraConfigs(ExtraConfigs extraConfigs) {
        this.extraConfigs = extraConfigs;
    }

    /**
     * Get the Beta network ID to bind this session to.
     *
     * @return beta network ID, or null if not set
     */
    public String getBetaNetworkId() {
        return betaNetworkId;
    }

    /**
     * Set the Beta network ID to bind this session to.
     *
     * @param betaNetworkId beta network ID
     */
    public void setBetaNetworkId(String betaNetworkId) {
        this.betaNetworkId = betaNetworkId;
    }

    /**
     * Get whether to load skills into the sandbox.
     *
     * @return true to load skills, null or false otherwise
     */
    public Boolean getLoadSkills() {
        return loadSkills;
    }

    /**
     * Set whether to load skills into the sandbox.
     *
     * @param loadSkills true to load skills
     */
    public void setLoadSkills(Boolean loadSkills) {
        this.loadSkills = loadSkills;
    }

    /**
     * Get skill names to load.
     *
     * @return list of skill names, or null
     */
    public List<String> getSkillNames() {
        return skillNames;
    }

    /**
     * Set skill names to load. Loads all visible skills when loadSkills=true and this is not specified.
     *
     * @param skillNames list of skill names
     */
    public void setSkillNames(List<String> skillNames) {
        this.skillNames = skillNames;
    }

}