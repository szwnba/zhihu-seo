"use client"

import { useState } from "react"

export default function CompetitorPanel() {
  const [domain, setDomain] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleAnalyze = async () => {
    if (!domain) return
    setLoading(true)
    try {
      // 模拟数据
      setResult({
        domain,
        total_keywords_found: 15,
        keywords: [
          { keyword: "SEO优化", source: "title" },
          { keyword: "长尾关键词", source: "title" },
          { keyword: "内容营销", source: "title" },
        ],
        content_structure: {
          headings: { h1: 3, h2: 12, h3: 25 },
          has_blog: true,
        },
        recommendations: [
          "建立支柱页 + 长尾文章的内容集群结构",
          "每周更新 2-3 篇高质量长尾文章",
        ],
      })
    } catch (e) {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">竞品监控</h2>
        <p className="text-gray-500 mt-1">分析竞品关键词布局，发现 SEO 机会</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">分析竞品网站</h3>
        <div className="flex gap-3">
          <input
            type="text"
            className="input flex-1"
            placeholder="输入竞品域名，如：example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          />
          <button
            className="btn-primary"
            onClick={handleAnalyze}
            disabled={loading || !domain}
          >
            {loading ? "分析中..." : "开始分析"}
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {result.total_keywords_found}
              </div>
              <div className="text-sm text-gray-500 mt-1">发现关键词</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {result.content_structure.headings.h2}
              </div>
              <div className="text-sm text-gray-500 mt-1">H2 标题数</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {result.content_structure.has_blog ? "✅" : "❌"}
              </div>
              <div className="text-sm text-gray-500 mt-1">内容中心</div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">竞品关键词</h3>
            <div className="flex flex-wrap gap-2">
              {result.keywords.map((kw: any, i: number) => (
                <span key={i} className="badge-blue">{kw.keyword}</span>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">优化建议</h3>
            <div className="space-y-2">
              {result.recommendations.map((rec: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-primary-500">💡</span>
                  <span className="text-gray-700">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
