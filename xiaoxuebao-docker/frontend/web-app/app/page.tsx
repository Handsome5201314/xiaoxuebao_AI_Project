'use client'

import { useState, useEffect } from 'react'
import { Layout, Typography, Input, Button, Card, Row, Col, Space, message, Spin, Alert, Tabs, Tag } from 'antd'
import { SearchOutlined, HeartOutlined, BookOutlined, UserOutlined, LoadingOutlined, StarOutlined, ClockCircleOutlined } from '@ant-design/icons'
import axios from 'axios'
import { motion } from 'framer-motion'

const { Header, Content, Footer } = Layout
const { Title, Paragraph } = Typography
const { TextArea } = Input

export default function HomePage() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [searchHistory, setSearchHistory] = useState([])
  const [categories, setCategories] = useState([])
  const [activeTab, setActiveTab] = useState('ask')
  const [systemStatus, setSystemStatus] = useState({ healthy: true, message: '' })

  // 检查系统状态
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const response = await axios.get('/api/health')
        setSystemStatus({ healthy: true, message: '系统运行正常' })
      } catch (error) {
        setSystemStatus({ healthy: false, message: '系统连接异常' })
      }
    }
    
    checkSystemStatus()
    
    // 加载分类列表
    loadCategories()
    
    // 加载搜索历史
    loadSearchHistory()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await axios.get('/api/knowledge/categories')
      setCategories(response.data)
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const loadSearchHistory = () => {
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
    setSearchHistory(history)
  }

  const saveSearchHistory = (query: string) => {
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
    const newHistory = [query, ...history.filter((item: string) => item !== query)].slice(0, 10)
    localStorage.setItem('searchHistory', JSON.stringify(newHistory))
    setSearchHistory(newHistory)
  }

  const handleAsk = async () => {
    if (!question.trim()) {
      message.warning('请输入您的问题')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('/api/knowledge/search', {
        query: question.trim(),
        limit: 10
      })
      
      setAnswer(response.data.results?.[0]?.content || '未找到相关信息')
      setSources(response.data.results || [])
      saveSearchHistory(question.trim())
      message.success('搜索完成')
    } catch (error) {
      console.error('提问失败:', error)
      message.error('搜索失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const quickQuestions = [
    '什么是急性淋巴细胞白血病？',
    '化疗后恶心呕吐怎么办？',
    '儿童白血病的护理要点',
    '白血病患者的饮食建议'
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
            ❄️ 小雪宝
          </div>
          <div style={{ color: 'white', marginLeft: '16px', fontSize: '16px' }}>
            白血病AI关爱助手
          </div>
        </div>
        
        {/* 系统状态指示器 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Tag color={systemStatus.healthy ? 'green' : 'red'}>
            {systemStatus.healthy ? '系统正常' : '系统异常'}
          </Tag>
        </div>
      </Header>

      <Content style={{ padding: '24px', background: '#f5f5f5' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          {/* 欢迎区域 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card style={{ marginBottom: '24px', textAlign: 'center' }}>
              <Title level={2} style={{ color: '#1890ff' }}>
                🌟 欢迎使用小雪宝AI助手
              </Title>
              <Paragraph style={{ fontSize: '16px', color: '#666' }}>
                我们为白血病患者、家属及临床医生提供智能、可靠、富有同理心的信息支持
              </Paragraph>
            </Card>
          </motion.div>

          {/* 系统状态提示 */}
          {!systemStatus.healthy && (
            <Alert
              message="系统状态异常"
              description={systemStatus.message}
              type="warning"
              showIcon
              style={{ marginBottom: '24px' }}
            />
          )}

          {/* 主要功能标签页 */}
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'ask',
                label: '💬 智能问答',
                children: (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* 问答内容 */}
                  </motion.div>
                )
              },
              {
                key: 'search',
                label: '🔍 知识搜索',
                children: (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* 搜索内容 */}
                  </motion.div>
                )
              },
              {
                key: 'categories',
                label: '📚 知识分类',
                children: (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* 分类内容 */}
                  </motion.div>
                )
              },
              {
                key: 'history',
                label: '🕒 搜索历史',
                children: (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* 历史内容 */}
                  </motion.div>
                )
              }
            ]}
          />

          {/* 问答区域 */}
          {activeTab === 'ask' && (
            <Card title="💬 智能问答" style={{ marginBottom: '24px' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <TextArea
                  placeholder="请输入您的问题，例如：什么是急性淋巴细胞白血病？"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows={4}
                  style={{ fontSize: '16px' }}
                />
                <Button
                  type="primary"
                  icon={loading ? <LoadingOutlined /> : <SearchOutlined />}
                  onClick={handleAsk}
                  loading={loading}
                  size="large"
                  style={{ width: '120px' }}
                >
                  {loading ? '搜索中...' : '提问'}
                </Button>
              </Space>

              {/* 快速问题 */}
              <div style={{ marginTop: '16px' }}>
                <Paragraph strong>💡 快速问题：</Paragraph>
                <Space wrap>
                  {quickQuestions.map((q, index) => (
                    <Button
                      key={index}
                      size="small"
                      onClick={() => setQuestion(q)}
                      style={{ marginBottom: '8px' }}
                    >
                      {q}
                    </Button>
                  ))}
                </Space>
              </div>
            </Card>
          )}

          {/* 知识搜索 */}
          {activeTab === 'search' && (
            <Card title="🔍 知识搜索" style={{ marginBottom: '24px' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Input.Search
                  placeholder="搜索知识库内容..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onSearch={handleAsk}
                  loading={loading}
                  size="large"
                  enterButton="搜索"
                />
                
                {/* 分类筛选 */}
                <div>
                  <Paragraph strong>📂 按分类筛选：</Paragraph>
                  <Space wrap>
                    {categories.map((category: any) => (
                      <Tag
                        key={category.id}
                        color="blue"
                        style={{ cursor: 'pointer' }}
                        onClick={() => {
                          setQuestion(category.name)
                          handleAsk()
                        }}
                      >
                        {category.name}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </Space>
            </Card>
          )}

          {/* 知识分类 */}
          {activeTab === 'categories' && (
            <Card title="📚 知识分类" style={{ marginBottom: '24px' }}>
              <Row gutter={[16, 16]}>
                {categories.map((category: any) => (
                  <Col xs={24} sm={12} md={8} lg={6} key={category.id}>
                    <Card
                      hoverable
                      style={{ textAlign: 'center', height: '120px' }}
                      bodyStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}
                      onClick={() => {
                        setQuestion(category.name)
                        setActiveTab('search')
                      }}
                    >
                      <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                        {category.icon || '📁'}
                      </div>
                      <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                        {category.name}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                        {category.description}
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          )}

          {/* 搜索历史 */}
          {activeTab === 'history' && (
            <Card title="🕒 搜索历史" style={{ marginBottom: '24px' }}>
              {searchHistory.length > 0 ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {searchHistory.map((item: string, index: number) => (
                    <Card
                      key={index}
                      size="small"
                      hoverable
                      style={{ cursor: 'pointer' }}
                      onClick={() => {
                        setQuestion(item)
                        setActiveTab('ask')
                      }}
                    >
                      <Space>
                        <ClockCircleOutlined />
                        <span>{item}</span>
                      </Space>
                    </Card>
                  ))}
                </Space>
              ) : (
                <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
                  暂无搜索历史
                </div>
              )}
            </Card>
          )}

          {/* 回答区域 */}
          {answer && (
            <Card title="🤖 AI回答" style={{ marginBottom: '24px' }}>
              <div style={{ 
                background: '#f9f9f9', 
                padding: '16px', 
                borderRadius: '8px',
                fontSize: '16px',
                lineHeight: '1.6'
              }}>
                {answer}
              </div>
              
              {sources.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <Paragraph strong>📚 参考资料：</Paragraph>
                  {sources.map((source, index) => (
                    <div key={index} style={{ 
                      background: '#fff', 
                      padding: '8px 12px', 
                      margin: '4px 0',
                      borderRadius: '4px',
                      border: '1px solid #e8e8e8'
                    }}>
                      <div style={{ fontWeight: 'bold' }}>{source.title}</div>
                      <div style={{ color: '#666', fontSize: '14px' }}>
                        {source.content_preview}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* 功能模块 */}
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={8}>
              <Card 
                hoverable
                style={{ textAlign: 'center', height: '200px' }}
                bodyStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}
              >
                <HeartOutlined style={{ fontSize: '48px', color: '#ff4d4f', marginBottom: '16px' }} />
                <Title level={4}>儿童关爱</Title>
                <Paragraph>专为儿童白血病患者设计的关爱模块</Paragraph>
              </Card>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <Card 
                hoverable
                style={{ textAlign: 'center', height: '200px' }}
                bodyStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}
              >
                <BookOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
                <Title level={4}>知识库</Title>
                <Paragraph>权威的医疗知识和诊疗指南</Paragraph>
              </Card>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <Card 
                hoverable
                style={{ textAlign: 'center', height: '200px' }}
                bodyStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}
              >
                <UserOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
                <Title level={4}>医生工具</Title>
                <Paragraph>为临床医生提供的专业工具</Paragraph>
              </Card>
            </Col>
          </Row>
        </div>
      </Content>

      <Footer style={{ textAlign: 'center', background: '#f0f0f0' }}>
        <Paragraph style={{ color: '#666' }}>
          ⚠️ 重要声明：本工具提供的所有信息仅供参考和教育目的，不能替代专业医生的诊断和治疗建议。
        </Paragraph>
        <Paragraph style={{ color: '#999', fontSize: '14px' }}>
          © 2025 小雪宝AI助手 - 让科技温暖生命，用AI点亮希望
        </Paragraph>
      </Footer>
    </Layout>
  )
}
