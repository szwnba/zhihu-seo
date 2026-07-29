const navItems = [
  { id: "dashboard", label: "仪表盘", icon: "📊" },
  { id: "crawl", label: "数据采集", icon: "🕷️" },
  { id: "keywords", label: "关键词", icon: "🔑" },
  { id: "baidu", label: "百度指数", icon: "📈" },
  { id: "clusters", label: "聚类分析", icon: "🧩" },
  { id: "competitor", label: "竞品监控", icon: "🔍" },
  { id: "content", label: "内容矩阵", icon: "📝" },
]

export default function Sidebar({
  activeTab,
  onTabChange,
}: {
  activeTab: string
  onTabChange: (tab: string) => void
}) {
  return (
    <aside className="w-56 bg-white border-r border-gray-200 p-4">
      <nav className="space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
              activeTab === item.id
                ? "bg-primary-50 text-primary-700 font-medium"
                : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
