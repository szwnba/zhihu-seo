"use client"

import { useState } from "react"

export default function KeywordPanel() {
  const [text, setText] = useState("")
  const [method, setMethod] = useState("tfidf")
  const [topK, setTopK] = useState(20)
  const [loading, setLoading] = useState(false)
  const [keywords, setKeywords] = useState<any[]>([])

  const handleExtract = async () => {
    if (!text) return
    setLoading(true)
    try {
      const res = await fetch("/api/v1/keywords/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, method, top_k: topK }),
      })
      const data = await res.json()
      setKeywords(data.keywords || [])
    } catch (e) {
      setKeywords([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">关键词提取</h2>
        <p className="text-gray-500 mt-1">从文本中自动提取长尾关键词</p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">提取设置</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              输入文本
            </label>
            <textarea
              className="input min-h-[150px]"
              placeholder="粘贴知乎回答内容或任意中文文本..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                提取方法
              </label>
              <select
                className="input"
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="tfidf">TF-IDF</option>
                <option value="textrank">TextRank</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                提取数量
              </label>
              <input
                type="number"
                className="input"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                min={5}
                max={100}
              />
            </div>
          </div>
          <button
            className="btn-primary w-full"
            onClick={handleExtract}
            disabled={loading || !text}
          >
            {loading ? "提取中..." : "提取关键词"}
          </button>
        </div>
      </div>

      {keywords.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            提取结果 ({keywords.length}个关键词)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 font-medium text-gray-500">#</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-500">关键词</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-500">权重</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-500">词性</th>
                </tr>
              </thead>
              <tbody>
                {keywords.map((kw, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3 text-gray-500">{i + 1}</td>
                    <td className="py-2 px-3 font-medium">{kw.keyword}</td>
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-500 rounded-full"
                            style={{ width: `${Math.min(100, kw.weight * 200)}%` }}
                          />
                        </div>
                        <span className="text-gray-600">{kw.weight}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3">
                      <span className="badge-blue">{kw.pos}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
