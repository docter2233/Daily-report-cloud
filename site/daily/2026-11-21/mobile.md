# 今日具身智能快报 2026-11-21

先看今日总览: [手机详情页](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/index.html)

## 论文

1. PhyDEX: A Benchmark for Physical Reasoning in Vision-Language-Action Models via Dynamic E…
- 主旨: 这篇论文关注人形/足式运动控制，方法路线偏向机械臂操控。
- 方法: 方法上，这篇工作更接近问题建模 + 感知/控制联合设计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕目标函数或损失设计、动力学/几何结构。
- 实验: 在公开基准或数据集上评估；做了消融或分析实验。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/papers/paper-01-phydex-a-benchmark-for-physical-reasoning-in-vision-language-action-mode.html) | [合法入口](https://arxiv.org/pdf/2611.26565v1)
2. MambaRGS: Referring Grasp Synthesis via Text-Image Cross-State Modulation and Rotation-Ad…
- 主旨: 这篇论文关注机械臂操控，方法路线偏向Transformer、几何/深度估计。
- 方法: 方法上，这篇工作更接近Transformer、几何/深度估计路线，但公开摘要没有把实现细节展开到可直接复现的程度。
- 理论: 公开摘要没有展开完整公式，但可以确认作者的理论抓手主要围绕动力学/几何结构、状态表征或世界模型、生成式序列建模。
- 实验: 包含真实机器人或真实环境验证；在公开基准或数据集上评估。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/papers/paper-02-mambargs-referring-grasp-synthesis-via-text-image-cross-state-modulation.html) | [合法入口](https://doi.org/10.1109/lra.2026.3748672)

## GitHub 项目

1. Z-Robotics-Lab/Z-Mobile-manip
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工程灵感源。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/repos/repo-01-z-robotics-lab-z-mobile-manip.html) | [源地址](https://github.com/Z-Robotics-Lab/Z-Mobile-manip)
2. BoosterRobotics/booster_gym
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/repos/repo-02-boosterrobotics-booster-gym.html) | [源地址](https://github.com/BoosterRobotics/booster_gym)
3. openrobokit/graspkit
- 定位: 这是一个偏机器人中间件/系统集成的开源仓库，更像工具链/基础设施。
- 推荐理由: 这不是当天最热的全站 Trending，但它更贴近机器人研究主线，被作为研究向补位推荐。
- 可用点: 对机器人研究是可直接复用的主线资源。
- 小文: [手机解读](https://docter2233.github.io/Daily-report-cloud/daily/2026-11-21/repos/repo-03-openrobokit-graspkit.html) | [源地址](https://github.com/openrobokit/graspkit)

推送里优先给出中文小文和判断结论，原始论文站点与 GitHub 只作为二跳入口。