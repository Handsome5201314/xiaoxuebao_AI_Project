import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '小雪宝 - 白血病AI关爱助手',
  description: '为白血病患者、家属及临床医生提供智能、可靠、富有同理心的信息支持与自我管理平台',
  keywords: '白血病,AI助手,医疗知识,儿童关爱,医生工具',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div id="root">
          {children}
        </div>
      </body>
    </html>
  )
}
