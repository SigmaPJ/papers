# AGENTS.md

本目录是罗重威（清华博二，patch-clamp 电生理 + 电刺激神经调控方向）的论文精读库。任何 agent 进入本目录工作前，先读完本文件。

## 接管速查

- 每个一级子目录 = 一篇论文，按 `期刊 - 年份 - 第一作者 - 标题` 命名（**强制规范，不允许 `paper.pdf` 这类通用名**）
- 主产出：每篇论文文件夹下的 `说明文档 - 作者 年份.html`，用于图文并茂阅读和放置互联网引用链接
- 辅助产出：`discussion - 作者 年份.md` 可作为 Markdown 底稿/备份，但不要只交 Markdown 而漏掉 HTML
- 研究方向集中：电场/电流刺激下细胞膜电位响应、伪迹机制、差分测量、深部脑刺激、tFUS、心肌细胞与神经元电生理
- 即将发表 IEEE TIM 差分测量论文，所以"差分电极/共模抑制/伪迹"类话题是热点

## 单篇论文的标准布局

```
期刊 - 年份 - 作者 - 标题/
├── 期刊 - 年份 - 作者 - 标题.pdf      # PDF 与文件夹同名
├── 说明文档 - 作者 年份.html          # 图文并茂说明文档（主产出）
├── discussion - 作者 年份.md          # Markdown 底稿/备份
├── figures/                           # 从 PDF 提取的图，命名如 Fig1.png
├── wechat_assets/                     # 可选：公众号推文用图
└── 公众号文章 - 作者 年份 主题.md     # 可选：公众号草稿
```

新建论文文件夹时遵循此布局；不要发明新结构。

## HTML 说明文档与引用链接约定

- 论文精读、学校介绍、人物介绍、项目介绍等说明类材料，默认以 HTML 为主；HTML 里应直接嵌入本地图、图注、术语解释和外部引用链接。
- 可联网时，主动给关键事实加来源链接。论文优先放 DOI、ScienceDirect/PubMed/期刊页；学校/人物优先放官网、机构主页、实验室主页；试剂/染料/仪器/软件优先放厂家或官方文档。
- 链接不能替代解释。英文术语、试剂型号、染料名、仪器型号、软件名第一次出现时，要先用中文解释是什么、做什么、为什么相关，再给链接。
- 不要堆英文术语。必要英文保留在括号里，例如“电位敏感染料（VSD, voltage-sensitive dye）”。
- HTML 中本地图像用相对路径引用 `figures/FigN.png`；对话里需要预览图片时仍遵守 `/Volumes/G$/LZW_sharing/tmp/` 的英文路径 staging 约定。

## 该用的 skill

- **paper-reader / paper-figure-extractor** — 读论文、提取图、写 HTML 说明文档和 Markdown 底稿
- **wechat-publisher** — 把 discussion 转成公众号推文
- **matplotlib-bindsize** — 复现/重画论文里的图（A4 排版、scale bar 等）
- **phd-weekly-report** — 周报写作（Markdown ↔ LaTeX）

agent 之间的约定：能用上述 skill 就别手搓流程。

## 磁盘路径与图片预览约定

本项目所有正式资源（PDF、figures、discussion、公众号草稿）都在中文路径下。**直接用中文路径在对话里嵌入图片预览会乱码**，必须走以下流程：

1. 正式文件**保留**在原中文路径，不要为了预览动它们
2. 预览前先在 `/Volumes/G$/LZW_sharing/tmp/` 下创建纯英文路径的副本（`cp`）或软链（`ln -s`）
3. 用这个英文路径嵌入预览
4. **每次内容更新换新文件名**（加时间戳/版本号），避免客户端缓存命中旧版

回复图片改动结果时，简洁三段式：
- 第一行：`文件已更新` + 正式输出路径（中文）
- 第二行：`英文预览已更新` + `/Volumes/G$/LZW_sharing/tmp/` 下的预览路径
- 然后直接嵌入预览图，最后一句话点出改动的脚本/文件

## 计算资源约定

`/Volumes/G$/...`、`/Volumes/C$/...`、`/Volumes/H$/...` 都是 **Windows 服务器盘 SMB 挂载**的视图，文件实际在服务器上。

**文件读写：** 直接用 `/Volumes/...` 路径操作即可，本地和服务器看到的是同一份文件。本地路径 ↔ 服务器路径直接换前缀：`/Volumes/G$/foo` ↔ `G:\foo`。

**计算：** 写代码、跑训练、重处理数据 → **走 SSH 到服务器**，不要在本地跑。本地只适合看图、改文档、跑 5 秒级小脚本。

**SSH 通道（已配密钥免密）：**
- `ssh windows-luo` — luozhongwei 账号，**默认用这个**
- `ssh windows-server` — Administrator 账号，要管理员权限时用

**跑 Python 的标准模板：**

```bash
# 用具体 conda env 的 python.exe（推荐）
ssh windows-luo 'G:\Users\luozhongwei\anaconda3\envs\<env>\python.exe <script.py>'

# 或激活后跑
ssh windows-luo 'cmd /c "conda activate <env> && python <script.py>"'
```

可用 conda envs：`default` / `gpu_ml_env` / `neuron_env` / `pipette_env` / `screenshot_env`（在 `G:\Users\luozhongwei\anaconda3\envs\`）。



## 用户上下文（快速对齐）

- 解释新概念时，可类比 patch-clamp、等效电路、差分测量这些他熟悉的框架
- tFUS、scalp EEG、IHC、光遗传学、GABAergic 中间神经元亚型——这些用户相对不熟，讨论时多解释
- 中文沟通；回复要简洁，不要长篇总结

## 跨 agent 协作纪律

- **本文件是项目唯一的常驻索引**。临时性的工作日志不要写进这里——如有需要，建在对应论文文件夹里。
- 改动了**目录结构、命名规范、预览路径约定、新增了通用 skill 用法**，必须在同一次工作里同步更新本文件。
- 不要在本文件里堆砌"今天读了哪几篇"这种动态记录，那是 discussion.md 的事。
