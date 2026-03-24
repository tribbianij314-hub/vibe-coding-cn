# 铁路知识数据库：从 0 到 1 实战流程（单人版）

> 目标用户：完全没有经验、但希望搭建一个可持续更新的铁路知识数据库的人。

---

## 1. 你将做出的成果

完成本流程后，你将拥有：

1. 一个可执行的目标与范围文档。
2. 一个可扩展的数据源登记表。
3. 一套统一数据库表结构（PostgreSQL）。
4. 一个可运行的采集脚本（以 Crossref 为起点）。
5. 一套去重、质检、复盘流程。
6. 一组可复用 Prompt 模板。

---

## 2. 先理解方法：为什么要这样做

本流程遵循以下原则：

- 先规划、后编码。
- 先跑通一个数据源，再逐步扩展。
- 文档与提示词是资产，不是临时记录。
- 每天都要有可验证产物和复盘。

一句话：**把一次抓数据，做成可持续的数据工程能力。**

---

## 3. 总体架构（先看全貌）

```text
数据源（API/网页/PDF）
  -> 采集层（fetchers）
  -> 解析层（parsers）
  -> 标准化层（normalizers）
  -> 去重层（dedup）
  -> 存储层（PostgreSQL + 原文文件）
  -> 检索层（SQL / 全文检索）
  -> 复盘层（日报 + Prompt 资产）
```

---

## 4. 工具清单（最小可用）

### 4.1 必需工具

- Python 3.11+
- PostgreSQL 15+
- pip / venv
- Git

### 4.2 Python 依赖（第一阶段）

- `httpx`：请求 API 与网页
- `beautifulsoup4`：解析 HTML
- `pydantic`：数据模型校验
- `psycopg[binary]`：写入 PostgreSQL
- `python-dotenv`：环境变量
- `rapidfuzz`：标题相似度去重

### 4.3 第二阶段再加

- `playwright`：动态网页采集
- `pymupdf`：PDF 文本提取
- `prefect`/`apscheduler`：定时调度

---

## 5. 项目结构（直接照抄）

```text
rail-knowledge/
  docs/
    00_goal_non_goal.md
    01_source_registry.md
    02_data_quality.md
    03_run_log.md
  prompts/
    prompt_collect.md
    prompt_parse.md
    prompt_dedup.md
    prompt_review.md
  sql/
    001_init.sql
  src/
    main.py
    settings.py
    models.py
    db.py
    sources/
      crossref.py
    pipeline/
      ingest.py
      dedup.py
  data/
    raw/
    exports/
```

---

## 6. 8 天入门执行计划（建议）

### Day 1：目标与边界

- 填写 `docs/00_goal_non_goal.md`。
- 确定第一批只抓 1 个来源：Crossref。

验收：你可以一口气说清“抓什么、不抓什么”。

### Day 2：搭建环境

- 创建虚拟环境。
- 安装依赖。
- 建立 PostgreSQL 数据库。

验收：`python -V`、数据库连接成功。

### Day 3：创建数据表

- 执行 `sql/001_init.sql`。
- 手动插入 1 条测试数据。

验收：能查到该记录。

### Day 4：写第一个采集器

- 在 `src/sources/crossref.py` 实现关键词检索。
- 保存原始响应到 `data/raw/`。

验收：成功抓取 50 条记录。

### Day 5：写标准化入库

- 将原始字段映射到统一表结构。
- 写入 `documents` 表。

验收：数据库中至少 50 条结构化记录。

### Day 6：做去重

- DOI 精确去重。
- 标题模糊匹配去重。

验收：重复数据明显下降并可解释。

### Day 7：做检索与导出

- SQL 按关键词/年份/类型查询。
- 导出 CSV。

验收：可稳定导出查询结果。

### Day 8：复盘与模板化

- 写 `docs/03_run_log.md`。
- 优化 Prompt 模板。

验收：下一轮可直接复用。

---

## 7. 每日工作模板（固定动作）

每天只做四件事：

1. 今日目标（10 分钟）
2. 单模块开发（90~120 分钟）
3. 最小测试（30 分钟）
4. 复盘沉淀（20 分钟）

如果你时间有限，宁可减少功能，也不要省略复盘。

---

## 8. 数据源扩展顺序（建议）

1. Crossref（元数据）
2. OpenAlex（关联关系）
3. 各铁路机构公开技术文档页面
4. 公开标准目录页面
5. 期刊官网公开摘要页面

说明：每增加一个来源，必须先更新 `01_source_registry.md`。

---

## 9. 质量规则（最小版）

每条记录至少包含：

- `title`
- `source_url`
- `source_name`
- `doc_type`
- `collected_at`

若字段缺失则标记 `quality_status = pending`，不得默默丢弃。

---

## 10. 风险与合规

- 优先采集公开元数据，谨慎处理版权全文。
- 遵守网站 robots、ToS 与频率限制。
- 对每条记录保留来源链接与采集时间。

---

## 11. 你下一步立刻执行什么

按顺序执行：

1. 复制本目录中的模板文件。
2. 填写目标与数据源登记表。
3. 执行 SQL 初始化数据库。
4. 运行最小采集脚本抓取第一批数据。
5. 做一次复盘并记录问题。

先跑通，再做强。
