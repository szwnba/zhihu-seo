"use client"

import { useState } from "react"

export default function ClusterPanel() {
  const [keywords, setKeywords] = useState("")
  const [nClusters, setNClusters] = useState(5)
  const [loading, setLoading] = useState(false)
  const [clusters, setClusters] = useState<any[]>([])

  const handleCluster = async () => {
    if (!keywords) return
    setLoading(true)
    try {
      const keywordList = keywords
        .split("\n")
        .map((k) => k.trim())
        .filter(Boolean)

      const res = await fetch("/api/v1/clusters/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keywords: keywordList,
          n_clusters: nClusters,
        }),
      })
      const data = await res.json()
      setClusters(data.clusters || [])
    } catch (e) {
      setClusters([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">聚类分析</h2>
        <p className="text-gray-500 mt-1">对关键词进行智能聚类，发现主题集群</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">聚类设置</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              关键词列表（每行一个）
            </label>
            <textarea
              className="input min-h-[150px]"
              placeholder="SEO优化&#10;长尾关键词&#10;内容营销&#10;关键词挖掘&#10;..."
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              聚类数量
            </label>
            <input
              type="number"
              className="input"
              value={nClusters}
              onChange={(e) => setNClusters(Number(e.target.value))}
              min={2}
              max={20}
            />
          </div>
          <button
            className="btn-primary w-full"
            onClick={handleCluster}
            disabled={loading || !keywords}
          >
            {loading ? "聚类中..." : "开始聚类"}
          </button>
        </div>
      </div>

      {clusters.length > 0 && (
        <div className="space-y-4">
          {clusters.map((cluster) => (
            <div key={cluster.cluster_id} className="card">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">
                  🧩 {cluster.name}
                </h4>
                <span className="badge-blue">{cluster.keyword_count} 个关键词</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {cluster.keywords.map((kw: string, i: number) => (
                  <span key={i} className="badge bg-gray-100 text-gray-700">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
