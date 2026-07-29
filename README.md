# Zhihu SEO Gold Miner

知乎长尾关键词挖掘与内容矩阵规划平台

## 功能特性

- 🕷️ **知乎爬虫** - 自动抓取收藏夹高赞回答，支持登录态和反爬策略
- 🔑 **关键词提取** - 基于 jieba + TF-IDF/TextRank 的中文 NLP 引擎
- 🧩 **智能聚类** - K-Means 聚类算法自动发现主题集群
- 📈 **百度搜索量** - 查询关键词搜索量、竞争度和相关词
- 🔍 **竞品监控** - 分析竞品关键词布局，发现 Keyword Gap
- 📝 **内容矩阵** - 智能生成支柱页 + 长尾文章 + 内部链接结构
- 👤 **用户系统** - JWT 认证 + 三档套餐（Free/Pro/Enterprise）

## 技术栈

### 后端
- Python 3.12 + FastAPI
- SQLAlchemy + SQLite
- jieba（中文分词）+ scikit-learn（聚类）
- JWT 认证 + bcrypt 加密

### 前端
- Next.js 14 + TypeScript
- Tailwind CSS

## 快速开始

### 后端
```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问: http://localhost:8000/docs

## 部署

- 前端：Vercel（推荐）
- 后端：Railway 或 Render
- 数据库：Supabase（PostgreSQL）

## 版本

v0.1.0 - MVP 版本
