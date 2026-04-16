'use strict'

const {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} = require('fs')
const path = require('path')
const yaml = require('js-yaml')
const { runWithFallback } = require('./run_with_fallback')

const projectRoot = path.resolve(__dirname, '..')
const docsRoot = path.join(projectRoot, 'docs', 'api')
const docsDir = docsRoot
const legacyDocsDir = path.join(projectRoot, 'docs', 'api-preview', 'typescript')
const outputDir = path.join(projectRoot, '.typedoc-output')

const docMappings = [
  { target: 'common-features/basics/agentbay.md', symbol: 'AgentBay', identifiers: ['Class AgentBay', 'AgentBay'] },
  { target: 'common-features/basics/session.md', symbol: 'Session', identifiers: ['Class Session', 'Session'] },
  { target: 'common-features/basics/command.md', symbol: 'Command', identifiers: ['Class Command', 'Command'] },
  {
    target: 'common-features/basics/context.md',
    symbol: 'ContextService',
    identifiers: ['Class ContextService', 'Class Context', 'ContextService', 'Context'],
  },
  { target: 'common-features/basics/context-manager.md', symbol: 'ContextManager', identifiers: ['Class ContextManager', 'ContextManager'] },
  { target: 'common-features/basics/filesystem.md', symbol: 'FileSystem', identifiers: ['Class FileSystem', 'FileSystem'] },
  {
    target: 'common-features/basics/context-sync.md',
    symbol: 'ContextSync',
    identifiers: ['Interface ContextSync', 'ContextSync', 'SyncPolicy', 'UploadPolicy', 'DownloadPolicy', 'DeletePolicy', 'ExtractPolicy', 'RecyclePolicy', 'WhiteList', 'BWList', 'MappingPolicy'],
  },
  {
    target: 'common-features/basics/logging.md',
    symbol: 'logger',
    identifiers: ['logger', 'log'],
  },
  { target: 'common-features/advanced/agent.md', symbol: 'Agent', identifiers: ['Class Agent', 'Agent'] },
  { target: 'common-features/advanced/browser-use-agent.md', symbol: 'BrowserUseAgent', identifiers: ['Class BrowserUseAgent', 'BrowserUseAgent'] },
  { target: 'common-features/advanced/computer-use-agent.md', symbol: 'ComputerUseAgent', identifiers: ['Class ComputerUseAgent', 'ComputerUseAgent'] },
  { target: 'common-features/advanced/mobile-use-agent.md', symbol: 'MobileUseAgent', identifiers: ['Class MobileUseAgent', 'MobileUseAgent'] },
  { target: 'common-features/advanced/oss.md', symbol: 'Oss', identifiers: ['Class Oss', 'Oss'] },
  {
    target: 'common-features/advanced/network.md',
    symbol: 'BetaNetworkService',
    identifiers: ['Class BetaNetworkService', 'BetaNetworkService', 'beta-network'],
  },
  { target: 'browser-use/browser.md', symbol: 'Browser', identifiers: ['Class Browser', 'Browser'] },
  {
    target: 'browser-use/extension.md',
    symbol: 'ExtensionsService',
    identifiers: ['Class ExtensionsService', 'Class Extension', 'ExtensionsService', 'Extension'],
  },
  { target: 'browser-use/browser-operator.md', symbol: 'BrowserOperator', identifiers: ['Class BrowserOperator', 'BrowserOperator', 'browser_operator'] },
  { target: 'browser-use/fingerprint.md', symbol: 'FingerprintFormat', identifiers: ['Class FingerprintFormat', 'FingerprintFormat', 'Fingerprint', 'browser/fingerprint'] },
  { target: 'codespace/code.md', symbol: 'Code', identifiers: ['Class Code', 'Code'] },
  { target: 'computer-use/computer.md', symbol: 'Computer', identifiers: ['Class Computer', 'Computer'] },
  {
    target: 'common-features/basics/session-params.md',
    symbol: 'CreateSessionParams',
    identifiers: ['Class CreateSessionParams', 'CreateSessionParams', 'BrowserContext', 'session-params'],
  },
  { target: 'mobile-use/mobile.md', symbol: 'Mobile', identifiers: ['Class Mobile', 'Mobile'] },
  {
    target: 'mobile-use/mobile-simulate.md',
    symbol: 'MobileSimulateService',
    identifiers: ['Class MobileSimulateService', 'MobileSimulateService', 'mobile-simulate'],
  },
  { target: 'common-features/advanced/git.md', symbol: 'Git', identifiers: ['Class Git', 'Git'] },
  { target: 'common-features/basics/pty.md', symbol: 'Pty', identifiers: ['Class Pty', 'Pty', 'PtyHandle', 'PtySession'] },
]

const symbolToTarget = new Map()
for (const mapping of docMappings) {
  if (mapping.symbol) {
    symbolToTarget.set(mapping.symbol.toLowerCase(), mapping.target)
  }
}

function cleanDirectory(dirPath) {
  if (existsSync(dirPath)) {
    rmSync(dirPath, { recursive: true, force: true })
  }
  mkdirSync(dirPath, { recursive: true })
}

function runTypedoc() {
  cleanDirectory(outputDir)

  const result = runWithFallback(
    'typedoc',
    'typedoc@0.25.0',
    ['--options', 'typedoc.json', '--out', outputDir],
    {
      cwd: projectRoot,
      env: { ...process.env, FORCE_COLOR: '1' },
      stdio: 'pipe',
    },
  )

  if (result.status !== 0) {
    const outputChunks = []
    if (result.stdout) {
      outputChunks.push(result.stdout)
    }
    if (result.stderr) {
      outputChunks.push(result.stderr)
    }
    const output = outputChunks.length ? Buffer.concat(outputChunks).toString() : 'Unknown error'
    throw new Error(`TypeDoc generation failed:\n${output}`)
  }
}

function removeLegacyDocsDir() {
  if (existsSync(legacyDocsDir)) {
    rmSync(legacyDocsDir, { recursive: true, force: true })
  }
}

function findMarkdownFiles(dir) {
  const results = []
  for (const entry of readdirSync(dir)) {
    const fullPath = path.join(dir, entry)
    const stats = statSync(fullPath)
    if (stats.isDirectory()) {
      results.push(...findMarkdownFiles(fullPath))
    } else if (stats.isFile() && entry.endsWith('.md')) {
      results.push(fullPath)
    }
  }
  return results
}

function extractTitle(content) {
  const lines = content.split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith('#')) {
      return trimmed.replace(/^#+\s*/, '')
    }
  }
  return ''
}

function loadPages() {
  const files = findMarkdownFiles(outputDir)
  return files.map((file) => {
    const content = readFileSync(file, 'utf8')
    const title = extractTitle(content)
    return { title, content, source: file }
  })
}

function normalize(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
}

function resolvePage(pages, identifiers) {
  for (const identifier of identifiers) {
    const normalizedIdentifier = normalize(identifier)

    const exact = pages.find((page) => normalize(page.title) === normalizedIdentifier)
    if (exact) {
      return exact
    }

    const partial = pages.find((page) => normalize(page.title).includes(normalizedIdentifier))
    if (partial) {
      return partial
    }
  }

  throw new Error(`Unable to locate documentation page for identifiers: ${identifiers.join(', ')}`)
}

function writeDocument(targetRelativePath, markdown) {
  const targetPath = path.join(docsDir, targetRelativePath)
  const parentDir = path.dirname(targetPath)
  if (!existsSync(parentDir)) {
    mkdirSync(parentDir, { recursive: true })
  }

  writeFileSync(targetPath, normalizeContent(markdown, targetRelativePath), 'utf8')
}

function normalizeContent(content, targetRelativePath) {
  const lines = content.split(/\r?\n/)

  while (lines.length && lines[0].includes('**Docs**')) {
    lines.shift()
  }

  while (lines.length && lines[0].trim() === '') {
    lines.shift()
  }

  if (lines.length && lines[0].trim() === '***') {
    lines.shift()
  }

  while (lines.length && lines[0].trim() === '') {
    lines.shift()
  }

  const headingIndex = lines.findIndex((line) => line.trim().startsWith('#'))
  if (headingIndex > 0) {
    const heading = lines[headingIndex].replace(/^#+\s*/, '# ')
    lines.splice(0, headingIndex + 1, heading)
  } else if (headingIndex === 0) {
    lines[0] = lines[0].replace(/^#+\s*/, '# ')
  }

  let normalized = lines.join('\n')

  // Apply TypeDoc optimization before link rewriting
  if (shouldOptimizeTypedoc(normalized)) {
    normalized = optimizeTypedocOutput(normalized)
  }

  // Fix same-file anchor links when TypeDoc/markdown anchor generation differs.
  normalized = fixSameFileAnchorLinks(normalized)

  const rewritten = rewriteLinks(normalized, targetRelativePath)
  return rewritten.trimEnd() + '\n'
}

function slugifyHeading(text) {
  // Approximate GitHub-style heading anchors used by our link checker.
  return text
    .trim()
    .toLowerCase()
    .replace(/[`*_~]/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9\u4e00-\u9fff\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
}

function collectAnchorsFromHeadings(markdown) {
  const anchors = new Set()
  const counts = new Map()
  const lines = markdown.split('\n')
  for (const line of lines) {
    const match = line.match(/^#{1,6}\s+(.+?)\s*$/)
    if (!match) continue
    const raw = match[1].trim()
    if (!raw) continue
    const base = slugifyHeading(raw)
    if (!base) continue
    const prev = counts.get(base) ?? 0
    counts.set(base, prev + 1)
    const anchor = prev === 0 ? base : `${base}-${prev}`
    anchors.add(anchor)
  }
  return anchors
}

function fixSameFileAnchorLinks(markdown) {
  const anchors = collectAnchorsFromHeadings(markdown)
  return markdown.replace(/\]\(#([^)]+)\)/g, (match, hash) => {
    const target = String(hash).trim()
    if (!target) return match
    if (anchors.has(target)) return match

    const deduped = target.replace(/-\d+$/, '')
    if (deduped !== target && anchors.has(deduped)) {
      return `](#${deduped})`
    }
    return match
  })
}

function rewriteLinks(markdown, targetRelativePath) {
  const currentPath = path.join(docsDir, targetRelativePath)
  const currentFileName = path.basename(targetRelativePath, '.md').toLowerCase()

  return markdown.replace(/\[([^\]]+)]\(([^)]+)\)/g, (match, label, link) => {
    if (link.startsWith('http') || link.startsWith('#')) {
      return match
    }

    const [pathPart, hash] = link.split('#')
    if (!pathPart.endsWith('.md')) {
      return match
    }

    const symbol = path.basename(pathPart, '.md').toLowerCase()
    const mappedTarget = symbolToTarget.get(symbol)

    if (!mappedTarget) {
      return `\`${label}\``
    }

    // Check if this is a same-file anchor link
    const targetFileName = path.basename(mappedTarget, '.md').toLowerCase()
    if (targetFileName === currentFileName && hash) {
      // Convert to pure anchor link for same-file references
      return `[${label}](#${hash})`
    }

    const toPath = path.join(docsDir, mappedTarget)
    const relative = path.relative(path.dirname(currentPath), toPath).replace(/\\/g, '/')
    const anchor = hash ? `#${hash}` : ''
    return `[${label}](${relative}${anchor})`
  })
}

function collectDirectoryContent(relativeDir) {
  const dirPath = path.join(outputDir, relativeDir)
  if (!existsSync(dirPath)) {
    throw new Error(`TypeDoc output directory not found: ${relativeDir}`)
  }

  const files = findMarkdownFiles(dirPath).sort((a, b) => {
    const aName = path.basename(a)
    const bName = path.basename(b)
    if (aName === 'README.md') {
      return -1
    }
    if (bName === 'README.md') {
      return 1
    }
    return a.localeCompare(b)
  })

  const contents = files.map((file) => readFileSync(file, 'utf8'))
  return contents.join('\n\n')
}

function collectPagesContent(pages, identifiers) {
  const seenSources = new Set()
  const contents = []

  for (const identifier of identifiers) {
    const page = resolvePage(pages, [identifier])
    if (seenSources.has(page.source)) {
      continue
    }
    seenSources.add(page.source)
    contents.push(page.content)
  }

  if (!contents.length) {
    throw new Error(`No pages found for identifiers: ${identifiers.join(', ')}`)
  }

  return contents.join('\n\n')
}

function createReadme() {
  const lines = [
    '# TypeScript SDK API Reference',
    '',
    'These documents are generated automatically using TypeDoc. Run `npm run docs:generate` to refresh them after changing the SDK.',
    '',
    '## Structure',
  ]

  const groups = {}

  for (const mapping of docMappings) {
    const parts = mapping.target.split('/')
    const groupKey = parts.slice(0, parts.length - 1).join('/') || '.'
    groups[groupKey] = groups[groupKey] ?? []
    groups[groupKey].push(parts[parts.length - 1])
  }

  const sortedGroups = Object.keys(groups).sort()
  for (const group of sortedGroups) {
    lines.push(`- \`${group}\``)
    const files = groups[group].sort()
    for (const file of files) {
      lines.push(`  - ${file}`)
    }
  }

  lines.push('')

  writeDocument('README.md', lines.join('\n'))
}

// ============================================================================
// TypeDoc Output Optimization Functions
// ============================================================================

function isPropertyDeclaration(line) {
  return /^•\s+\*\*\w+\*\*:\s+/.test(line.trim())
}

function isPropertySection(lines, startIndex) {
  if (startIndex >= lines.length) return null

  const heading = lines[startIndex]
  if (!heading.startsWith('### ')) return null

  const propertyName = heading.replace(/^###\s+/, '').trim()

  for (let i = startIndex + 1; i < Math.min(startIndex + 5, lines.length); i++) {
    const line = lines[i].trim()
    if (line === '') continue

    if (isPropertyDeclaration(line)) {
      const match = line.match(/^•\s+\*\*(\w+)\*\*:\s+(.+)$/)
      if (match) {
        const type = match[2].replace(/\\/g, '')
        return { name: propertyName, type, lineNumber: startIndex }
      }
    }
    break
  }

  return null
}

function isSimpleGetter(methodName) {
  if (/^get[A-Z]/.test(methodName)) {
    // Keep non-trivial getters in docs.
    const excludeList = [
      'getLabels',
      'getLink',
      'getLinkAsync',
      'getMetrics',
      'getFileUploadUrl',
      'getFileDownloadUrl',
    ]
    return !excludeList.includes(methodName)
  }
  return false
}

function parseSections(lines) {
  const sections = []
  let currentSection = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const h2Match = line.match(/^##\s+(.+)$/)

    if (h2Match) {
      if (currentSection) {
        currentSection.endLine = i - 1
        sections.push(currentSection)
      }
      currentSection = { title: h2Match[1], startLine: i, endLine: -1 }
    }
  }

  if (currentSection) {
    currentSection.endLine = lines.length - 1
    sections.push(currentSection)
  }

  return sections
}

function extractProperties(lines, startLine, endLine) {
  const properties = []

  for (let i = startLine; i <= endLine && i < lines.length; i++) {
    const propInfo = isPropertySection(lines, i)
    if (propInfo) {
      properties.push(propInfo)
    }
  }

  return properties
}

function generatePropertiesCodeBlock(properties) {
  if (properties.length === 0) return []

  const lines = ['```typescript']
  properties.forEach(prop => {
    lines.push(`${prop.name}: ${prop.type}`)
  })
  lines.push('```', '')

  return lines
}

function optimizeTypedocOutput(content) {
  const lines = content.split('\n')
  const sections = parseSections(lines)

  const tocSection = sections.find(s => s.title === 'Table of contents')
  const constructorSection = sections.find(s => s.title === 'Constructors')
  const propertiesSection = sections.find(s => s.title === 'Properties')
  const methodsSection = sections.find(s => s.title === 'Methods')

  const linesToRemove = new Set()
  const linesToAdd = new Map()

  // Collect removed property names and getter method names
  const removedPropertyNames = new Set()
  const removedGetterNames = new Set()

  // 1. Handle Properties section - merge into code block
  if (propertiesSection) {
    const properties = extractProperties(lines, propertiesSection.startLine, propertiesSection.endLine)

    if (properties.length > 0) {
      for (const prop of properties) {
        removedPropertyNames.add(prop.name)
        let endLine = prop.lineNumber + 1
        while (endLine < lines.length && !lines[endLine].startsWith('###') && !lines[endLine].startsWith('##')) {
          endLine++
        }
        for (let i = prop.lineNumber; i < endLine; i++) {
          linesToRemove.add(i)
        }
      }

      const codeBlock = generatePropertiesCodeBlock(properties)
      linesToAdd.set(propertiesSection.startLine + 1, ['', ...codeBlock])
    }
  }

  // 2. Remove constructor section
  if (constructorSection) {
    for (let i = constructorSection.startLine; i <= constructorSection.endLine; i++) {
      linesToRemove.add(i)
    }
  }

  // 3. Filter getter methods
  if (methodsSection) {
    for (let i = methodsSection.startLine + 1; i <= methodsSection.endLine && i < lines.length; i++) {
      const line = lines[i]
      const h3Match = line.match(/^###\s+(.+)$/)

      if (h3Match) {
        const methodName = h3Match[1].trim()
        if (isSimpleGetter(methodName)) {
          removedGetterNames.add(methodName)

          // Find the start line (including preceding separator if exists)
          // But skip lines that are already marked for removal
          let startLine = i
          // Check if there's a separator (___) before this method
          if (i > 0 && !linesToRemove.has(i - 1) && lines[i - 1].trim() === '') {
            if (i > 1 && !linesToRemove.has(i - 2) && lines[i - 2].trim() === '___') {
              startLine = i - 2
            }
          } else if (i > 0 && !linesToRemove.has(i - 1) && lines[i - 1].trim() === '___') {
            startLine = i - 1
          }

          // Find the end line (until next ### or ##, but not ####)
          let endLine = i + 1
          while (endLine < lines.length) {
            const line = lines[endLine]
            if (line.startsWith('### ') || line.startsWith('## ')) {
              break
            }
            endLine++
          }

          // Mark all lines for removal (from startLine to endLine, not including endLine)
          for (let j = startLine; j < endLine; j++) {
            linesToRemove.add(j)
          }
        }
      }
    }
  }

  // 4. Optimize Table of Contents
  if (tocSection) {
    for (let i = tocSection.startLine + 1; i <= tocSection.endLine && i < lines.length; i++) {
      const line = lines[i]

      // Remove "### Constructors" heading line in TOC
      if (line.trim() === '### Constructors') {
        linesToRemove.add(i)
        continue
      }

      // Remove constructor link
      if (line.includes('- [constructor]')) {
        linesToRemove.add(i)
        continue
      }

      // Remove property links from TOC
      const propertyLinkMatch = line.match(/- \[(\w+)\]\(/)
      if (propertyLinkMatch) {
        const linkName = propertyLinkMatch[1]
        if (removedPropertyNames.has(linkName)) {
          linesToRemove.add(i)
          continue
        }
      }

      // Remove getter method links from TOC
      const methodLinkMatch = line.match(/- \[(\w+)\]\(/)
      if (methodLinkMatch) {
        const methodName = methodLinkMatch[1]
        if (removedGetterNames.has(methodName)) {
          linesToRemove.add(i)
          continue
        }
      }
    }
  }

  // Build optimized content
  const optimizedLines = []
  for (let i = 0; i < lines.length; i++) {
    if (linesToRemove.has(i)) continue
    if (linesToAdd.has(i)) {
      optimizedLines.push(...linesToAdd.get(i))
    }
    optimizedLines.push(lines[i])
  }

  // Clean up multiple consecutive empty lines
  const cleaned = []
  let emptyCount = 0
  for (const line of optimizedLines) {
    if (line.trim() === '') {
      emptyCount++
      if (emptyCount <= 2) cleaned.push(line)
    } else {
      emptyCount = 0
      cleaned.push(line)
    }
  }

  return cleaned.join('\n')
}

function shouldOptimizeTypedoc(content) {
  return content.includes('## Table of contents') &&
         (content.includes('## Properties') || content.includes('## Methods'))
}

// ============================================================================
// Metadata Enhancement Functions
// ============================================================================

function loadMetadata() {
  const metadataPath = path.join(__dirname, '../../scripts/doc-metadata.yaml')
  if (!existsSync(metadataPath)) {
    return { modules: {} }
  }
  const content = readFileSync(metadataPath, 'utf8')
  return yaml.load(content)
}

function extractModuleName(filePath) {
  return path.basename(filePath, '.md')
}

function getTutorialSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.tutorial) {
    return ''
  }

  const emoji = config.emoji || '📖'
  const category = config.category || 'common-features/basics'
  const categoryDepth = category.split('/').length
  const depth = categoryDepth + 3
  const upLevels = '../'.repeat(depth)

  let tutorialUrl = config.tutorial.url
  const docsMatch = tutorialUrl.match(/docs\/(.+)$/)
  if (docsMatch) {
    tutorialUrl = `${upLevels}docs/${docsMatch[1]}`
  }

  return `## ${emoji} Related Tutorial\n\n- [${config.tutorial.text}](${tutorialUrl}) - ${config.tutorial.description}\n\n`
}

function getOverviewSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.overview) {
    return ''
  }
  return `## Overview\n\n${config.overview}\n\n`
}

function getRequirementsSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.requirements || config.requirements.length === 0) {
    return ''
  }

  const lines = ['## Requirements\n']
  for (const req of config.requirements) {
    lines.push(`- ${req}`)
  }
  lines.push('\n')

  return lines.join('\n')
}

function getDataTypesSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.data_types || config.data_types.length === 0) {
    return ''
  }

  const lines = ['## Data Types\n']
  for (const dataType of config.data_types) {
    lines.push(`### ${dataType.name}\n`)
    lines.push(`${dataType.description}\n`)
  }
  lines.push('')

  return lines.join('\n')
}

function getImportantNotesSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.important_notes || config.important_notes.length === 0) {
    return ''
  }

  const lines = ['## Important Notes\n']
  for (const note of config.important_notes) {
    lines.push(`- ${note}`)
  }
  lines.push('\n')

  return lines.join('\n')
}

function getBestPracticesSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.best_practices || config.best_practices.length === 0) {
    return ''
  }

  const lines = ['## Best Practices\n']
  for (let i = 0; i < config.best_practices.length; i++) {
    lines.push(`${i + 1}. ${config.best_practices[i]}`)
  }
  lines.push('\n')

  return lines.join('\n')
}

function calculateResourcePath(resource, moduleConfig) {
  const targetCategory = resource.category || 'common-features/basics'
  const currentCategory = moduleConfig.category || 'common-features/basics'
  const module = resource.module

  if (targetCategory === currentCategory) {
    return `${module}.md`
  }

  const currentParts = currentCategory.split('/')
  const targetParts = targetCategory.split('/')

  let relativePath = ''
  for (let i = 0; i < currentParts.length; i++) {
    relativePath += '../'
  }

  relativePath += targetParts.join('/') + '/' + module + '.md'
  return relativePath
}

function getRelatedResourcesSection(moduleName, metadata) {
  const config = metadata.modules?.[moduleName]
  if (!config?.related_resources || config.related_resources.length === 0) {
    return ''
  }

  const lines = ['## Related Resources\n']
  for (const resource of config.related_resources) {
    const resourcePath = calculateResourcePath(resource, config)
    lines.push(`- [${resource.name}](${resourcePath})`)
  }
  lines.push('\n')

  return lines.join('\n')
}

function addAfterTitle(content, insertion) {
  const lines = content.split('\n')
  let titleIndex = -1

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('# ')) {
      titleIndex = i
      break
    }
  }

  if (titleIndex === -1) {
    return insertion + content
  }

  lines.splice(titleIndex + 1, 0, '', insertion.trimEnd())
  return lines.join('\n')
}

function addBeforeFooter(content, insertion) {
  const lines = content.split('\n')
  let footerIndex = -1

  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim()
    if (line === '---') {
      if (i === 0 || !lines[i - 1].includes('|')) {
        footerIndex = i
        break
      }
    }
  }

  if (footerIndex === -1) {
    return content + '\n' + insertion
  }

  lines.splice(footerIndex, 0, insertion.trimEnd(), '')
  return lines.join('\n')
}

function insertAfterTitle(content, sections) {
  const lines = content.split('\n')
  let titleIndex = -1

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('# ')) {
      titleIndex = i
      break
    }
  }

  if (titleIndex === -1) {
    return sections.join('') + content
  }

  const combinedSections = sections.join('')
  lines.splice(titleIndex + 1, 0, '', combinedSections.trimEnd())
  return lines.join('\n')
}

function enhanceMarkdownFile(filePath, metadata) {
  let content = readFileSync(filePath, 'utf8')

  // Note: TypeDoc optimization is now done in normalizeContent(),
  // so we don't need to do it again here

  // Add metadata enhancements
  const moduleName = extractModuleName(filePath)
  const moduleConfig = metadata.modules?.[moduleName]

  if (!moduleConfig) {
    // No metadata config, file was already optimized during write
    return
  }

  // Collect all sections to insert after title
  const sectionsAfterTitle = []

  // 1. Tutorial section
  const tutorialSection = getTutorialSection(moduleName, metadata)
  if (tutorialSection && !content.includes('Related Tutorial')) {
    sectionsAfterTitle.push(tutorialSection)
  }

  // 2. Overview section
  const overviewSection = getOverviewSection(moduleName, metadata)
  if (overviewSection && !content.includes('## Overview')) {
    sectionsAfterTitle.push(overviewSection)
  }

  // 3. Requirements section
  const requirementsSection = getRequirementsSection(moduleName, metadata)
  if (requirementsSection && !content.includes('## Requirements')) {
    sectionsAfterTitle.push(requirementsSection)
  }

  // 4. Data types section
  const dataTypesSection = getDataTypesSection(moduleName, metadata)
  if (dataTypesSection && !content.includes('## Data Types')) {
    sectionsAfterTitle.push(dataTypesSection)
  }

  // 5. Important notes section
  const importantNotesSection = getImportantNotesSection(moduleName, metadata)
  if (importantNotesSection && !content.includes('## Important Notes')) {
    sectionsAfterTitle.push(importantNotesSection)
  }

  // Insert all sections after title at once
  if (sectionsAfterTitle.length > 0) {
    content = insertAfterTitle(content, sectionsAfterTitle)
  }

  // Add best practices before related resources
  const bestPracticesSection = getBestPracticesSection(moduleName, metadata)
  if (bestPracticesSection && !content.includes('## Best Practices')) {
    content = addBeforeFooter(content, bestPracticesSection)
  }

  // Add related resources before footer
  const resourcesSection = getRelatedResourcesSection(moduleName, metadata)
  if (resourcesSection && !content.includes('## Related Resources')) {
    content = addBeforeFooter(content, resourcesSection)
  }

  // Ensure same-file anchor links stay consistent after all enhancements.
  content = fixSameFileAnchorLinks(content)

  writeFileSync(filePath, content, 'utf8')
}

function enhanceAllMarkdownFiles(docsDir, metadata) {
  if (!existsSync(docsDir)) {
    console.error(`Documentation directory not found: ${docsDir}`)
    return
  }

  function processDirectory(dir) {
    const entries = readdirSync(dir, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name)

      if (entry.isDirectory()) {
        processDirectory(fullPath)
      } else if (entry.isFile() && entry.name.endsWith('.md') && entry.name !== 'README.md') {
        console.log(`Enhancing: ${fullPath}`)
        enhanceMarkdownFile(fullPath, metadata)
      }
    }
  }

  processDirectory(docsDir)
}

function enhanceDocumentation() {
  try {
    console.log('Enhancing TypeDoc output with metadata...')
    const metadata = loadMetadata()
    enhanceAllMarkdownFiles(docsDir, metadata)
    console.log('Enhancement complete!')
  } catch (error) {
    console.warn('⚠️  Documentation enhancement failed:', error.message)
  }
}

function main() {
  runTypedoc()

  removeLegacyDocsDir()
  cleanDirectory(docsDir)

  const pages = loadPages()

  for (const mapping of docMappings) {
    let rawContent
    if (mapping.collectDir) {
      rawContent = collectDirectoryContent(mapping.collectDir)
    } else if (mapping.collectPages && mapping.collectPages.length) {
      rawContent = collectPagesContent(pages, mapping.collectPages)
    } else {
      if (!mapping.identifiers || !mapping.identifiers.length) {
        throw new Error(`No identifiers provided for mapping target ${mapping.target}`)
      }
      const page = resolvePage(pages, mapping.identifiers)
      rawContent = page.content
    }

    writeDocument(mapping.target, rawContent)
  }

  createReadme()

  if (existsSync(outputDir)) {
    rmSync(outputDir, { recursive: true, force: true })
  }

  process.stdout.write('✅ TypeScript API documentation generated at docs/api\n')

  enhanceDocumentation()
}

if (require.main === module) {
  try {
    main()
  } catch (error) {
    if (error instanceof Error) {
      console.error(`❌ Failed to generate TypeScript API documentation\n${error.message}`)
    } else {
      console.error('❌ Failed to generate TypeScript API documentation', error)
    }
    process.exit(1)
  }
}

module.exports = { main }

