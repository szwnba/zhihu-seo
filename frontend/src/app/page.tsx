"use client"

import { useState } from "react"
import Header from "@/components/Header"
import Sidebar from "@/components/Sidebar"
import Dashboard from "@/components/Dashboard"
import CrawlPanel from "@/components/CrawlPanel"
import KeywordPanel from "@/components/KeywordPanel"
import BaiduPanel from "@/components/BaiduPanel"
import ClusterPanel from "@/components/ClusterPanel"
import CompetitorPanel from "@/components/CompetitorPanel"
import ContentMatrix from "@/components/ContentMatrix"

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard")

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />
      case "crawl":
        return <CrawlPanel />
      case "keywords":
        return <KeywordPanel />
      case "baidu":
        return <BaiduPanel />
      case "clusters":
        return <ClusterPanel />
      case "competitor":
        return <CompetitorPanel />
      case "content":
        return <ContentMatrix />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="flex-1 p-6 overflow-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}
