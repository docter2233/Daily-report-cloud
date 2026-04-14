# 机器人具身智能日报 - 2026-04-14

- 统计窗口: 2026-04-14 至 2026-04-14
- 生成时间: 2026-04-14T11:46:53+08:00
- 论文数: 10
- GitHub 热点仓库数: 0

- 每日详情页: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/index.html

## 论文速读

### 1. Diffusion-Based mmWave Radar Point Cloud Enhancement Driven by Range Images
- 方向: 机器人通用方法
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Millimeter-wave (mmWave) radar has attracted significant attention in robotics and autonomous driving due to its robustness in harsh environments.
- 理论: 方法线上更接近 Diffusion / 检索增强 / 几何/深度估计。Traditional mmWave radar enhancement approaches often struggle to leverage the effectiveness of diffusion models in super-resolution, largely due to the unnatural range-azimuth heatmap (RAH) or bird's eye view (BEV) representation.
- 应用: 对机器人系统设计、实验选题和工程落地都有一定参考价值。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-01-diffusion-based-mmwave-radar-point-cloud-enhancement-driven-by-range-ima.html
- 原始来源: https://doi.org/10.1109/lra.2026.3673977

### 2. Visual Sculpting: Visually-Aligned Planning Representations for Long-Horizon Robot Clay Sculpting
- 方向: 机械臂操控
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Clay sculpting is a nuanced, artistic task involving dexterous manipulation with long-horizon planning to achieve high-level goals.
- 理论: 方法线上更接近 该方向常见技术。Prior deformable object manipulation work either requires retraining a policy per goal or relies on dynamics models which represent state as sparse point clouds which do not capture important clay features, such as textures, well.
- 应用: 更偏向抓取、装配、接触丰富操作等真实机械臂任务。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-02-visual-sculpting-visually-aligned-planning-representations-for-long-hori.html
- 原始来源: https://doi.org/10.1109/lra.2026.3673896

### 3. Distributed Safe Navigation for Multi-Robot Systems With Fixed-Time Convergence and Deadlock Resolution
- 方向: 导航与规划
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：This letter addresses the problem of distributed safe navigation for multi-robot systems (MRSs), proposing a comprehensive framework that unifies safety-critical control, real-time navigation, and deadlock resolution.
- 理论: 方法线上更接近 约束建模。This letter addresses the problem of distributed safe navigation for multi-robot systems (MRSs), proposing a comprehensive framework that unifies safety-critical control, real-time navigation, and deadlock resolution.
- 应用: 更适合长时序任务编排、复杂场景导航和系统级决策。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-03-distributed-safe-navigation-for-multi-robot-systems-with-fixed-time-conv.html
- 原始来源: https://doi.org/10.1109/lra.2026.3671566

### 4. Distributed Lloyd-Based Algorithm for Uncertainty-Aware Multi-Robot Under-Canopy Flocking
- 方向: 仿真到真实迁移
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：In this letter, we present a distributed algorithm for flocking in complex environments that operates at constant altitude, without explicit communication, no a priori information about the environment, and by using only on-board sensing and computation capabilities.
- 理论: 方法线上更接近 约束建模。In this letter, we present a distributed algorithm for flocking in complex environments that operates at constant altitude, without explicit communication, no a priori information about the environment, and by using only on-board sensing and computation capabilities.
- 应用: 更适合把仿真中的策略稳定迁移到真实机器人平台。
- 阅读建议: 有开放获取入口，手机深读成本相对更低。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-04-distributed-lloyd-based-algorithm-for-uncertainty-aware-multi-robot-unde.html
- 原始来源: https://doi.org/10.1109/lra.2026.3673985

### 5. Rethinking Transparent Object Grasping: Depth Completion With Monocular Depth Estimation and Instance Mask
- 方向: 机械臂操控
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Accurate depth maps are essential for robotic grasping.
- 理论: 方法线上更接近 几何/深度估计。Existing end-to-end methods aim to predict depth directly from RGB-D inputs.
- 应用: 更偏向抓取、装配、接触丰富操作等真实机械臂任务。
- 阅读建议: 有开放获取入口，手机深读成本相对更低。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-05-rethinking-transparent-object-grasping-depth-completion-with-monocular-d.html
- 原始来源: https://arxiv.org/pdf/2508.02507

### 6. $\pi$-BA: Probabilistic Neural Bundle Adjustment With Iterative Cycle Optimization for Driving Scene Reconstruction
- 方向: 机器人通用方法
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Urban scene reconstruction under noisy camera poses remains a critical challenge for autonomous driving.
- 理论: 方法线上更接近 约束建模 / 几何/深度估计。While recent neural dense Bundle Adjustment (BA) methods have shown promising results in specific settings, their performance often degrades in real-world urban scenarios due to noisy correspondences and imbalanced optimization between camera poses and scene parameters, which leads the scene representation to overfit to erroneous geometric constraints, causing the system to converge to suboptimal local minima.
- 应用: 对机器人系统设计、实验选题和工程落地都有一定参考价值。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-06-pi-ba-probabilistic-neural-bundle-adjustment-with-iterative-cycle-optimi.html
- 原始来源: https://doi.org/10.1109/lra.2026.3669066

### 7. Continual Reinforcement Learning Framework for Scalable Collision Avoidance and Mitigation System With Packing Strategy
- 方向: 导航与规划
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Collision Avoidance and Mitigation System (CAMS) in autonomous driving systems is crucial for ensuring safety by formulating strategies to address various collisions and planning the trajectory accordingly.
- 理论: 方法线上更接近 强化学习。Although recent learning-based motion planning methods for CAMS have shown promising results for specific collision scenarios, the question of how to continually scale up their knowledge across different driving environments has not yet been thoroughly investigated.
- 应用: 更适合长时序任务编排、复杂场景导航和系统级决策。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-07-continual-reinforcement-learning-framework-for-scalable-collision-avoida.html
- 原始来源: https://doi.org/10.1109/lra.2026.3678453

### 8. Lightweight Kinematic and Static Modeling of Cable-Driven Continuum Robots via Actuation-Space Energy Formulation
- 方向: 机械臂操控
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Continuum robots, inspired by octopus arms and elephant trunks, combine dexterity with intrinsic compliance, making them well suited for unstructured and confined environments.
- 理论: 方法线上更接近 该方向常见技术。We propose the Lightweight Actuation-Space Energy Modeling (LASEM) framework for cable-driven continuum robots, which formulates actuation potential energy directly in actuation space.
- 应用: 更偏向抓取、装配、接触丰富操作等真实机械臂任务。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-08-lightweight-kinematic-and-static-modeling-of-cable-driven-continuum-robo.html
- 原始来源: https://doi.org/10.1109/lra.2026.3674005

### 9. Design and Implementation of an Uncrewed Aerial-Aquatic Vehicle With Antenna Retractor
- 方向: 足式与人形运动
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Uncrewed aerial-aquatic vehicles (UAAVs) can operate in both aerial and aquatic domains and repeatedly cross domains, thereby presenting considerable application prospects.
- 理论: 方法线上更接近 该方向常见技术。Uncrewed aerial-aquatic vehicles (UAAVs) can operate in both aerial and aquatic domains and repeatedly cross domains, thereby presenting considerable application prospects.
- 应用: 更适合行走、跑跳、抗扰和平衡恢复等运动控制问题。
- 阅读建议: 建议先看我整理的小文，再决定是否跳原文。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-09-design-and-implementation-of-an-uncrewed-aerial-aquatic-vehicle-with-ant.html
- 原始来源: https://doi.org/10.1109/lra.2026.3669797

### 10. A Bi-Directional Adaptive Framework for Agile UAV Landing
- 方向: 导航与规划
- 证据等级: 摘要支撑
- 内容: 这篇工作首先强调：Autonomous landing on mobile platforms is crucial for extending quadcopter operational flexibility, yet conventional methods are often too inefficient for highly dynamic scenarios.
- 理论: 方法线上更接近 约束建模。Autonomous landing on mobile platforms is crucial for extending quadcopter operational flexibility, yet conventional methods are often too inefficient for highly dynamic scenarios.
- 应用: 更适合长时序任务编排、复杂场景导航和系统级决策。
- 阅读建议: 有开放获取入口，手机深读成本相对更低。
- 小文: https://docter2233.github.io/Daily-report-cloud/daily/2026-04-14/papers/paper-10-a-bi-directional-adaptive-framework-for-agile-uav-landing.html
- 原始来源: https://arxiv.org/pdf/2601.03037

## GitHub 项目速读

- 无命中结果。
