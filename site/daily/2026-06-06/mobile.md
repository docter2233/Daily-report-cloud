# 今日具身智能快报 2026-06-06

先看今日总览: [手机详情页](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/index.html)

## 论文

1. HANDOFF: Humanoid Agentic Task-Space Whole-Body Control via Distilled Complementary Teach…
- 主旨: 这篇论文关注人形/足式运动控制，方法路线偏向机械臂操控。
- 方法: 方法上，这篇工作更接近问题建模 + 感知/控制联合设计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕动力学/几何结构、策略或控制律、状态表征或世界模型。
- 实验: 包含真实机器人或真实环境验证。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/papers/paper-01-handoff-humanoid-agentic-task-space-whole-body-control-via-distilled-com.html) | [合法入口](https://arxiv.org/pdf/2606.06493v1)
2. OSMO: Open-Source Tactile Glove for Human-to-Robot Skill Transfer
- 主旨: 这篇论文关注触觉感知闭环，方法路线偏向触觉反馈。
- 方法: 方法上，这篇工作更接近触觉反馈路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 目前只有标题和元数据，无法负责任地还原具体推导，只能保留研究方向判断。
- 实验: 摘要没有展开完整实验表，但可以确认作者至少做了方法有效性验证。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/papers/paper-02-osmo-open-source-tactile-glove-for-human-to-robot-skill-transfer.html) | [合法入口](https://doi.org/10.1109/lra.2026.3692034)

## GitHub 项目

1. QwenLM/Qwen3-VL
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像agent 范式参考。
- 推荐理由: 今天在 Trending 里新增 17 star。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/repos/repo-01-qwenlm-qwen3-vl.html) | [源地址](https://github.com/QwenLM/Qwen3-VL)
2. BoosterRobotics/booster_gym
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/repos/repo-02-boosterrobotics-booster-gym.html) | [源地址](https://github.com/BoosterRobotics/booster_gym)
3. luckyrobots/luckyrobots
- 定位: 这是一个偏仿真平台或训练环境的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-06-06/repos/repo-03-luckyrobots-luckyrobots.html) | [源地址](https://github.com/luckyrobots/luckyrobots)

推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。