"use client"

import { useState } from "react"

export default function BaiduPanel() {
  const [keyword, setKeyword] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleQuery = async () => {
    if (!keyword) return
    setLoading(true)
    try {
      // 模拟数据
      setResult({
        keyword,
        search_volume: Math.floor(Math.random() * 5000) + 100,
        is_accurate: false,
        competitor_count: Math.floor(Math.random() * 1000000) + 100000,
        competition_score: Math.floor(Math.random() * 100),
        related_keywords: [
          keyword + "方法",
          keyword + "教程",
          keyword + "工具",
          keyword + "推荐",
          keyword + "技巧",
        ],
      })
    } catch (e) {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const getCompetitionBadge = (score: number) => {
    if (score >= 70) return "badge-red"
    if (score >= 40) return "badge-yellow"
    return "badge-green"
  }

  const getCompetitionLabel = (score: number) => {
    if (score >= 70) return "高竞争"
    if (score >= 40) return "中竞争"
    return "低竞争"
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">百度搜索量查询</h2>
        <p className="text-gray-500 mt-1">查询关键词搜索量、竞争度和相关词</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">搜索量查询</h3>
        <div className="flex gap-3">
          <input
            type="text"
            className="input flex-1"
            placeholder="输入关键词，如：SEO优化"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
          />
          <button
            className="btn-primary"
            onClick={handleQuery}
            disabled={loading || !keyword}
          >
            {loading ? "查询中..." : "查询"}
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {result.search_volume.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 mt-1">月搜索量</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">
                {(result.competitor_count / 10000).toFixed(0)}万
              </div>
              <div className="text-sm text-gray-500 mt-1">竞争对手</div>
            </div>
            <div className="card text-center">
              <div className="flex flex-col items-center">
                <div className="text-3xl font-bold text-primary-600">
                  {result.competition_score}
                </div>
                <div className={`badge ${getCompetitionBadge(result.competition_score)} mt-1`}>
                  {getCompetitionLabel(result.competition_score)}
                </div>
              </div>
              <div className="text-sm text-gray-500 mt-1">竞争度</div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">📎 相关关键词</h3>
            <div className="flex flex-wrap gap-2">
              {result.related_keywords.map((kw: string, i: number) => (
                <button
                  key={i}
                  className="badge bg-gray-100 text-gray-700 hover:bg-primary-50 hover:text-primary-700 cursor-pointer transition-colors"
                  onClick={() => { setKeyword(kw); }}
                >
                  {kw}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">💡 SEO 建议</h3>
            <div className="space-y-2">
              {result.competition_score < 40 && (
                <div className="flex items-start gap-2">
                  <span>🟢</span>
                  <span className="text-gray-700">竞争较低，建议优先布局此关键词</span>
                </div>
              )}
              {result.search_volume > 1000 && (
                <div className="flex items-start gap-2">
                  <span>📈</span>
                  <span className="text-gray-700">搜索量较高，有较大流量潜力</span>
                </div>
              )}
              <div className="flex items-start gap-2">
                <span>📝</span>
                <span className="text-gray-700">建议创建 2000+ 字的深度内容</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
