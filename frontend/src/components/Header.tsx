export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">知</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">
            Zhihu SEO Gold Miner
          </h1>
          <span className="badge-blue">v0.1.0</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="badge-green">免费版</span>
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-gray-600 text-sm font-medium">U</span>
          </div>
        </div>
      </div>
    </header>
  )
}
