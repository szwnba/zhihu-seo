"use client"

import { useState } from "react"

const stats = [
  { label: "已采集回答", value: "0", change: "+0", icon: "📄" },
  { label: "提取关键词", value: "0", change: "+0", icon: "🔑" },
  { label: "关键词聚类", value: "0", change: "+0", icon: "🧩" },
  { label: "内容方案", value: "0", change: "+0", icon: "📝" },
]

const recentTasks = [
  { id: 1, type: "采集任务", target: "SEO优化收藏夹", status: "completed", time: "2小时前" },
  { id: 2, type: "关键词提取", target: "100条高赞回答", status: "completed", time: "1小时前" },
  { id: 3, type: "聚类分析", target: "50个关键词", status: "running", time: "进行中" },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">仪表盘</h2>
        <p className="text-gray-500 mt-1">概览你的知乎 SEO 数据挖掘进度</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center justify-between">
              <span className="text-2xl">{stat.icon}</span>
              <span className="badge-green">{stat.change}</span>
            </div>
            <div className="mt-3">
              <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* 快速操作 */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">快速操作</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center">
            <span className="text-2xl block mb-2">🕷️</span>
            <span className="font-medium text-gray-700">新建采集任务</span>
            <p className="text-sm text-gray-500 mt-1">从知乎收藏夹抓取高赞回答</p>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center">
            <span className="text-2xl block mb-2">🔑</span>
            <span className="font-medium text-gray-700">提取关键词</span>
            <p className="text-sm text-gray-500 mt-1">从文本中挖掘长尾关键词</p>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center">
            <span className="text-2xl block mb-2">📝</span>
            <span className="font-medium text-gray-700">生成内容矩阵</span>
            <p className="text-sm text-gray-500 mt-1">智能规划内容集群</p>
          </button>
        </div>
      </div>

      {/* 最近任务 */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">最近任务</h3>
        <div className="space-y-3">
          {recentTasks.map((task) => (
            <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="badge-blue">{task.type}</span>
                <span className="text-gray-700">{task.target}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className={`badge ${task.status === "completed" ? "badge-green" : "badge-yellow"}`}>
                  {task.status === "completed" ? "已完成" : "进行中"}
                </span>
                <span className="text-sm text-gray-500">{task.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
