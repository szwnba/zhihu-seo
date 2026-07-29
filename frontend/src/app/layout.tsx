import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Zhihu SEO Gold Miner",
  description: "知乎长尾关键词挖掘与内容矩阵规划平台",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  )
}
