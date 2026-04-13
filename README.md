# Daily Report Cloud

这个项目现在不是单纯“把链接推到微信”，而是一个手机优先的每日小文系统：

- 微信推送里直接给论文/项目的内容、理论线索、应用价值和阅读建议
- 每条条目自动生成一个适合手机看的“小文页”
- 每天再生成一个总览页，推送里优先放自己的小文链接，原始论文站点和 GitHub 只做二跳入口
- 全部由 GitHub Actions 定时生成和部署，所以电脑关机也不影响

## 当前方案

- 云端调度：GitHub Actions
- 页面托管：GitHub Pages
- 微信通道默认：PushPlus
- 备选通道：企业微信机器人
- 默认定时：每天北京时间 08:30
  - GitHub Actions 对应 UTC cron：`30 0 * * *`

## 目录

- `scripts/research_briefing.py`
  - 采集论文和 GitHub Trending
  - 补充摘要/README 信息
  - 生成长报告、手机摘要、静态小文页
  - 支持直接推送
- `scripts/mobile_digest_helpers.py`
  - 负责“小文”内容组织、摘要生成和静态站点输出
- `config/default_watchlist.json`
  - 默认期刊、Trending 语言、GitHub 相关性关键词和筛选阈值
- `.github/workflows/daily-report.yml`
  - 云端定时生成、Pages 部署和微信推送
- `site/`
  - 自动生成的静态小文站点

## GitHub Secrets

至少配置：

- `PUSHPLUS_TOKEN`

可选配置：

- `WECOM_BOT_WEBHOOK`
- `CROSSREF_MAILTO`

可选 GitHub Repository Variable：

- `PUBLIC_BASE_URL`
  - 如果你以后想改成自定义域名或别的托管地址，可以用它覆盖默认的 GitHub Pages URL

## 本地测试

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/research_briefing.py collect --days 1 --max-papers 4 --max-repos 4 --public-base-url "https://example.com/"
python scripts/research_briefing.py run --days 1 --push-provider pushplus --dry-run --token dummy --public-base-url "https://example.com/"
```

测试后重点看：

- `artifacts/*-mobile.md`
  - 推送内容是否已经是“手机可读的小文摘要”
- `site/index.html`
  - 站点首页是否能按日期进入
- `site/daily/<date>/`
  - 是否生成了当日总览页和每条项目详情页

如果当天 GitHub Trending 没有通过相关性阈值的仓库，系统会保留空结果，而不是为了凑数把泛 AI 热门项目塞进手机日报。

## GitHub 相关性调参

- `github_candidate_pool_size`
  - 先从 GitHub Trending 扩大抓取候选池，再做相关性排序，避免只被全站最热但不相关的仓库占满
- `github_min_relevance_score`
  - 通过关键词打分做硬过滤；分数不够的项目不会进入日报
- `github_allowed_relevance_labels`
  - 默认只允许 `直接相关` 和 `中度相关`
- `github_required_keywords_any`
  - 再加一道“核心机器人关键词”门槛；如果条目只命中 `agent`、`rl` 这类泛 AI 词，而没有命中机器人主线词，就不会进入日报
- `github_keywords`
  - 你可以按自己的研究方向提高或降低关键词权重，比如更偏操作、触觉、人形或 sim2real

## 真正上线

1. 把 `D:\robot\daily-report-cloud` 作为独立 Git 仓库推到 GitHub。
2. 在仓库 `Settings > Secrets and variables > Actions` 中添加 `PUSHPLUS_TOKEN`。
3. 在仓库 `Settings > Pages` 中启用 GitHub Pages。
   Source 选 GitHub Actions。
4. 允许 Actions 对仓库内容写入。
   这个项目会把生成好的 `site/` 更新回仓库，以保留每日历史页面。
5. 手动执行一次 `workflow_dispatch`，确认：
   - Pages 正常部署
   - 微信收到的消息优先指向自己的小文页

## 结果

只要 GitHub Actions 在跑：

- 电脑关机不影响推送
- 手机里先看我替你整理好的内容
- 想深挖时再点自己的小文页
- 实在需要再跳原始论文站点或 GitHub
