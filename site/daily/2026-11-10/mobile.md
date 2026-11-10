# 今日具身智能快报 2026-11-10

先看今日总览: [手机详情页](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/index.html)

## 论文

1. PCTac: Mechanochromic Photonic-Crystal Tactile Sensor for Dexterous Manipulation
- 主旨: 这篇论文关注触觉感知闭环，方法路线偏向扩散模型、触觉反馈、几何/深度估计。
- 方法: 方法上，这篇工作更接近扩散模型、触觉反馈、几何/深度估计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕动力学/几何结构、策略或控制律、生成式序列建模。
- 实验: 摘要没有展开完整实验表，但可以确认作者至少做了方法有效性验证。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/papers/paper-01-pctac-mechanochromic-photonic-crystal-tactile-sensor-for-dexterous-manip.html) | [合法入口](https://arxiv.org/pdf/2611.12383v1)
2. LA-WBC: Learning-Driven Adaptation of Whole-Body Control for Safe Locomotion on Uncertain…
- 主旨: 这篇论文关注机械臂操控，方法路线偏向强化学习、约束建模、Sim2Real。
- 方法: 方法上，这篇工作更接近强化学习、约束建模、Sim2Real路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕约束建模、动力学/几何结构、策略或控制律。
- 实验: 包含真实机器人或真实环境验证；含仿真实验。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/papers/paper-02-la-wbc-learning-driven-adaptation-of-whole-body-control-for-safe-locomot.html) | [合法入口](https://doi.org/10.1109/lra.2026.3745006)

## GitHub 项目

1. google-deepmind/mujoco
- 定位: 这是一个偏仿真平台或训练环境的开源仓库，更像工具链/基础设施。
- 推荐理由: 今天在 Trending 里新增 574 star。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/repos/repo-01-google-deepmind-mujoco.html) | [源地址](https://github.com/google-deepmind/mujoco)
2. Z-Robotics-Lab/Z-Mobile-manip
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工程灵感源。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/repos/repo-02-z-robotics-lab-z-mobile-manip.html) | [源地址](https://github.com/Z-Robotics-Lab/Z-Mobile-manip)
3. BoosterRobotics/booster_gym
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-10/repos/repo-03-boosterrobotics-booster-gym.html) | [源地址](https://github.com/BoosterRobotics/booster_gym)

推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。