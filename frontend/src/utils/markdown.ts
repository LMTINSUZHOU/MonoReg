function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function safeLinkUrl(url: string) {
  const normalized = url.trim().replace(/&amp;/g, '&')
  if (/^(https?:\/\/|mailto:|\/)/i.test(normalized)) return escapeHtml(normalized)
  return ''
}

function safeImageUrl(url: string) {
  const normalized = url.trim().replace(/&amp;/g, '&')
  if (/^(https?:\/\/|\/)/i.test(normalized)) return escapeHtml(normalized)
  return ''
}

function renderInline(value: string) {
  let html = escapeHtml(value)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt: string, url: string) => {
    const src = safeImageUrl(url)
    return src ? `<img src="${src}" alt="${alt}" loading="lazy">` : alt
  })
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label: string, url: string) => {
    const href = safeLinkUrl(url)
    return href ? `<a href="${href}" target="_blank" rel="noopener noreferrer">${label}</a>` : label
  })
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  return html
}

export function renderMarkdown(markdown?: string | null) {
  const source = (markdown || '').replace(/\r\n/g, '\n')
  const lines = source.split('\n')
  const html: string[] = []
  let listType: 'ul' | 'ol' | null = null
  let inCode = false
  const codeLines: string[] = []

  function closeList() {
    if (listType) {
      html.push(`</${listType}>`)
      listType = null
    }
  }

  function openList(nextType: 'ul' | 'ol') {
    if (listType === nextType) return
    closeList()
    listType = nextType
    html.push(`<${nextType}>`)
  }

  function closeCode() {
    html.push(`<pre><code>${codeLines.join('\n')}</code></pre>`)
    codeLines.length = 0
    inCode = false
  }

  for (const line of lines) {
    const trimmed = line.trim()
    if (trimmed.startsWith('```')) {
      if (inCode) closeCode()
      else {
        closeList()
        inCode = true
      }
      continue
    }

    if (inCode) {
      codeLines.push(escapeHtml(line))
      continue
    }

    if (!trimmed) {
      closeList()
      continue
    }

    const heading = trimmed.match(/^(#{1,4})\s+(.+)$/)
    if (heading) {
      closeList()
      const level = Math.min(heading[1].length + 1, 5)
      html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`)
      continue
    }

    const quote = trimmed.match(/^>\s?(.+)$/)
    if (quote) {
      closeList()
      html.push(`<blockquote>${renderInline(quote[1])}</blockquote>`)
      continue
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/)
    if (unordered) {
      openList('ul')
      html.push(`<li>${renderInline(unordered[1])}</li>`)
      continue
    }

    const ordered = trimmed.match(/^\d+\.\s+(.+)$/)
    if (ordered) {
      openList('ol')
      html.push(`<li>${renderInline(ordered[1])}</li>`)
      continue
    }

    closeList()
    html.push(`<p>${renderInline(trimmed)}</p>`)
  }

  if (inCode) closeCode()
  closeList()
  return html.join('')
}
