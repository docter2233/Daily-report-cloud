# 今日具身智能快报 2026-04-22

先看今日总览: [手机详情页](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/index.html)

## 论文

1. Mask World Model: Predicting What Matters for Robust Robot Policy Learning
- 主旨: 这篇论文关注高层任务理解与技能编排，方法路线偏向扩散模型、世界模型、检索增强。
- 方法: 方法上，这篇工作更接近扩散模型、世界模型、检索增强路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕目标函数或损失设计、动力学/几何结构、策略或控制律。
- 实验: 包含真实机器人或真实环境验证；含仿真实验；在公开基准或数据集上评估。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/papers/paper-01-mask-world-model-predicting-what-matters-for-robust-robot-policy-learnin.html) | [合法入口](https://arxiv.org/pdf/2604.19683v1)
2. Koopman-Based Online Identification With Sim2Real Transfer for Hydrodynamic Modeling of T…
- 主旨: 这篇论文关注仿真到真实迁移，方法路线偏向Sim2Real。
- 方法: 方法上，这篇工作更接近Sim2Real路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 目前只有标题和元数据，无法负责任地还原具体推导，只能保留研究方向判断。
- 实验: 摘要没有展开完整实验表，但可以确认作者至少做了方法有效性验证。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/papers/paper-02-koopman-based-online-identification-with-sim2real-transfer-for-hydrodyna.html) | [合法入口](https://doi.org/10.1109/lra.2026.3682620)

## GitHub 项目

1. QwenLM/Qwen3-VL
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像agent 范式参考。
- 推荐理由: 今天在 Trending 里新增 15 star。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/repos/repo-01-qwenlm-qwen3-vl.html) | [源地址](https://github.com/QwenLM/Qwen3-VL)
2. BoosterRobotics/booster_gym
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/repos/repo-02-boosterrobotics-booster-gym.html) | [源地址](https://github.com/BoosterRobotics/booster_gym)
3. luckyrobots/luckyrobots
- 定位: 这是一个偏仿真平台或训练环境的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-04-22/repos/repo-03-luckyrobots-luckyrobots.html) | [源地址](https://github.com/luckyrobots/luckyrobots)

推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。