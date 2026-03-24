# 数据源登记模板

> 规则：新增数据源前先登记；每次抓取后更新状态。

| source_id | source_name | source_type | entry_url | access_mode | robots_ok | auth_required | priority | status | notes |
|---|---|---|---|---|---|---|---|---|---|
| src_crossref | Crossref | api | https://api.crossref.org/works | api | yes | no | p0 | active | 先做这个 |
| src_openalex | OpenAlex | api | https://api.openalex.org/works | api | yes | no | p1 | pending | 第二阶段 |
| src_manual_example | Railway Manual Site | web | https://example.com/manuals | html | pending | pending | p2 | pending | 需确认条款 |

## 字段说明

- `source_type`: api / html / pdf_index / rss
- `access_mode`: api / crawler / browser
- `status`: active / pending / blocked / retired
