"use client"

import { useState } from "react"

export default function CrawlPanel() {
  const [url, setUrl] = useState("")
  const [minVotes, setMinVotes] = useState(100)
  const [maxPages, setMaxPages] = useState(10)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async () => {
    if (!url) return
    setLoading(true)
    try {
      const res = await fetch("/api/v1/crawl/bookmark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bookmark_url: url,
          min_votes: minVotes,
          max_pages: maxPages,
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setResult({ error: "请求失败" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">数据采集</h2>
        <p className="text-gray-500 mt-1">从知乎收藏夹中抓取高赞回答</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">新建采集任务</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              收藏夹 URL
            </label>
            <input
              type="url"
              className="input"
              placeholder="https://www.zhihu.com/collection/xxxxxxx"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                最小赞同数
              </label>
              <input
                type="number"
                className="input"
                value={minVotes}
                onChange={(e) => setMinVotes(Number(e.target.value))}
                min={0}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                最大分页数
              </label>
              <input
                type="number"
                className="input"
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                min={1}
                max={50}
              />
            </div>
          </div>
          <button
            className="btn-primary w-full"
            onClick={handleSubmit}
            disabled={loading || !url}
          >
            {loading ? "采集中..." : "开始采集"}
          </button>
        </div>
      </div>

      {result && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">采集结果</h3>
          <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">采集历史</h3>
        <div className="text-center py-8 text-gray-500">
          <span className="text-4xl block mb-2">📋</span>
          <p>暂无采集历史</p>
        </div>
      </div>
    </div>
  )
}
