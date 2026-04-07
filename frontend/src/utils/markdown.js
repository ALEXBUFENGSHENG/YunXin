import MarkdownIt from 'markdown-it'
import MarkdownItKatex from 'markdown-it-katex'
import MarkdownItTaskLists from 'markdown-it-task-lists'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

md.use(MarkdownItKatex)
md.use(MarkdownItTaskLists, { enabled: true })

export const renderMarkdown = (text) => md.render(text || '')
