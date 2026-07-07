# 今日具身智能快报 2026-07-07

先看今日总览: [手机详情页](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/index.html)

## 论文

1. Deform360: A Massive Multi-view Visuotactile Dataset for Deformable World Models
- 主旨: 这篇论文关注可变形物体操作，方法路线偏向触觉反馈、世界模型、检索增强、几何/深度估计。
- 方法: 方法上，这篇工作更接近触觉反馈、世界模型、检索增强、几何/深度估计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕动力学/几何结构、状态表征或世界模型。
- 实验: 包含真实机器人或真实环境验证；在公开基准或数据集上评估；做了消融或分析实验。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/papers/paper-01-deform360-a-massive-multi-view-visuotactile-dataset-for-deformable-world.html) | [合法入口](https://arxiv.org/pdf/2607.05390v1)
2. U-KGNav: Unified Zero-Shot Goal-Oriented Navigation via Knowledge Graph
- 主旨: 这篇论文关注导航规划与场景决策，方法路线偏向导航与规划。
- 方法: 方法上，这篇工作更接近问题建模 + 感知/控制联合设计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 目前只有标题和元数据，无法负责任地还原具体推导，只能保留研究方向判断。
- 实验: 摘要没有展开完整实验表，但可以确认作者至少做了方法有效性验证。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/papers/paper-02-u-kgnav-unified-zero-shot-goal-oriented-navigation-via-knowledge-graph.html) | [合法入口](https://doi.org/10.1109/lra.2026.3706925)

## GitHub 项目

1. BoosterRobotics/booster_gym
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/repos/repo-01-boosterrobotics-booster-gym.html) | [源地址](https://github.com/BoosterRobotics/booster_gym)
2. luckyrobots/luckyrobots
- 定位: 这是一个偏仿真平台或训练环境的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/repos/repo-02-luckyrobots-luckyrobots.html) | [源地址](https://github.com/luckyrobots/luckyrobots)
3. xwx555/DynamicGraspLab
- 定位: 这是一个偏仿真平台或训练环境的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-07-07/repos/repo-03-xwx555-dynamicgrasplab.html) | [源地址](https://github.com/xwx555/DynamicGraspLab)

推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。