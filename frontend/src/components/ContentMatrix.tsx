"use client"

import { useState } from "react"

export default function ContentMatrix() {
  const [loading, setLoading] = useState(false)
  const [matrix, setMatrix] = useState<any>(null)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      // 模拟数据
      setMatrix({
        summary: {
          total_keywords: 50,
          total_clusters: 5,
          estimated_articles: 30,
        },
        pillar_pages: [
          { title: "SEO优化完全指南", target_keyword: "SEO优化" },
          { title: "长尾关键词挖掘方法", target_keyword: "长尾关键词" },
        ],
        content_clusters: [
          {
            cluster_name: "SEO基础",
            articles: [
              { title: "什么是SEO优化", target_keyword: "SEO优化" },
              { title: "SEO关键词密度", target_keyword: "关键词密度" },
            ],
          },
        ],
      })
    } catch (e) {
      setMatrix(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">内容矩阵</h2>
        <p className="text-gray-500 mt-1">智能规划内容集群，建立主题权威</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">生成内容矩阵</h3>
        <p className="text-gray-600 mb-4">
          基于关键词聚类结果，自动生成内容矩阵蓝图，包括支柱页、长尾文章和内部链接结构。
        </p>
        <button
          className="btn-primary"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? "生成中..." : "生成内容矩阵"}
        </button>
      </div>

      {matrix && (
        <>
          {/* 摘要 */}
          <div className="grid grid-cols-3 gap-4">
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">{matrix.summary.total_keywords}</div>
              <div className="text-sm text-gray-500 mt-1">关键词</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">{matrix.summary.total_clusters}</div>
              <div className="text-sm text-gray-500 mt-1">聚类</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-600">{matrix.summary.estimated_articles}</div>
              <div className="text-sm text-gray-500 mt-1">预估文章</div>
            </div>
          </div>

          {/* 支柱页 */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">📌 支柱页 (Pillar Pages)</h3>
            <div className="space-y-3">
              {matrix.pillar_pages.map((page: any, i: number) => (
                <div key={i} className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="font-medium text-gray-900">{page.title}</div>
                  <div className="text-sm text-gray-500 mt-1">目标关键词: {page.target_keyword}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 内容集群 */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">📝 内容集群</h3>
            <div className="space-y-4">
              {matrix.content_clusters.map((cluster: any, i: number) => (
                <div key={i} className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">🧩 {cluster.cluster_name}</h4>
                  <div className="space-y-2">
                    {cluster.articles.map((article: any, j: number) => (
                      <div key={j} className="flex items-center gap-2 text-sm text-gray-600">
                        <span className="text-gray-400">→</span>
                        <span>{article.title}</span>
                        <span className="badge-blue">{article.target_keyword}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
