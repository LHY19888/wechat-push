# 企业微信定时推送系统

电脑关机也能自动推送消息到企业微信群，基于 GitHub Actions 云端运行。

## 推送时间表

| 时间 | 内容 | 脚本 |
|------|------|------|
| 每天 8:30 | 📚 ICT晨读·项目基础 | ict_push.py morning |
| 每天 9:30 | 📡 行业资讯·早报 | news.py 早报 |
| 每天 12:30 | 📚 ICT午学·项目全流程 | ict_push.py noon |
| 每天 17:00 | 📡 行业资讯·晚报 + 📚 ICT晚课·招投标 | news.py 晚报 + ict_push.py evening |
| 每天 23:30 | 📚 ICT夜读·专业名词 | ict_push.py night |

## 部署步骤（5步搞定）

### 第1步：登录 GitHub
打开 https://github.com 并登录你的账号

### 第2步：创建新仓库
1. 点击右上角 **+** → **New repository**
2. Repository name 填：`wechat-push`
3. 选择 **Public**（公开，免费无限额度）
4. 勾选 **Add a README file**
5. 点击 **Create repository**

### 第3步：上传文件
1. 在仓库页面点击 **Add file** → **Upload files**
2. 把以下文件/文件夹拖进去：
   - `scripts/` 文件夹（含 webhook.py, ict_content.py, ict_push.py, news.py）
   - `.github/workflows/` 文件夹（含5个yml文件）
3. 点击 **Commit changes**

> 注意：要保留文件夹结构。先创建 `scripts` 文件夹（上传时新建），再上传文件。

### 第4步：设置 Webhook 密钥
1. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name 填：`WEBHOOK_URL`
4. Secret 填：
   ```
   https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ed942ad7-11da-4de4-86c5-32bb0cb06b01
   ```
5. 点击 **Add secret**

### 第5步：启用 Actions
1. 进入仓库 → **Actions** 标签页
2. 如果提示，点击 **I understand my workflows, go ahead and enable them**
3. 在左侧可以看到5个workflow，说明已启用

## 验证是否成功

1. 进入 **Actions** 页面
2. 选择任意一个workflow（如"ICT晨读-项目基础"）
3. 点击 **Run workflow** → **Run workflow**
4. 等待1-2分钟，查看运行结果（绿色✅表示成功）
5. 检查企业微信群是否收到消息

## 常见问题

### Q: 推送时间不准时？
A: GitHub Actions 的 cron 调度可能有 5-15 分钟延迟，属正常现象。

### Q: Actions 运行失败怎么办？
A: 进入 Actions 页面，点击失败的运行记录，查看日志排查原因。最常见原因是 WEBHOOK_URL 未设置或设置错误。

### Q: 如何修改推送内容？
A: 编辑 `scripts/ict_content.py` 中的对应主题内容，提交更改即可。

### Q: 如何暂停推送？
A: 进入 Actions 页面，点击对应workflow，点击 **Disable workflow**。

### Q: 免费额度够用吗？
A: Public 仓库免费无限分钟。Private 仓库每月2000分钟，本项目每天6次约12分钟，每月约360分钟，完全够用。

## 文件结构

```
├── .github/workflows/     # GitHub Actions 工作流
│   ├── ict-morning.yml    # 8:30 ICT晨读
│   ├── industry-morning.yml # 9:30 行业早报
│   ├── ict-noon.yml       # 12:30 ICT午学
│   ├── evening.yml        # 17:00 行业晚报+ICT晚课
│   └── ict-night.yml      # 23:30 ICT夜读
├── scripts/               # Python脚本
│   ├── webhook.py         # Webhook发送工具
│   ├── ict_content.py     # ICT知识内容库(44个主题)
│   ├── ict_push.py        # ICT知识推送脚本
│   └── news.py            # 行业资讯抓取推送脚本
└── README.md              # 说明文档
```
