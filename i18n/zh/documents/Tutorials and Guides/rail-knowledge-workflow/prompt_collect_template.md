# Prompt 模板：采集器生成

你是资深 Python 数据工程师。请基于以下约束生成一个可运行的采集器：

- 目标来源：{{source_name}}
- 入口：{{entry_url}}
- 输出：标准 JSON 列表
- 字段：title, authors, doi, abstract, published_at, source_url, doc_type
- 要求：
  1) 失败重试 3 次
  2) 请求间隔可配置
  3) 记录结构化日志
  4) 不使用过度抽象
  5) 代码附最小运行示例

请按以下结构输出：
1. 文件结构
2. 完整代码
3. 运行命令
4. 常见错误与修复
