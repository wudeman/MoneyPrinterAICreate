# MoneyPrinterAICreate 前端项目

## 项目说明

这是一个基于 Vue 3 + TypeScript + Vite 的前端项目，用于与 MoneyPrinterAICreate 后端服务进行交互。

## 技术栈

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Axios

## 项目结构

```
sites/
├── public/           # 静态资源
├── src/
│   ├── assets/       # 项目资源文件
│   ├── components/   # 通用组件
│   ├── views/        # 页面组件
│   ├── router/       # 路由配置
│   ├── stores/       # Pinia 状态管理
│   ├── services/     # API 服务
│   ├── types/        # TypeScript 类型定义
│   ├── App.vue       # 根组件
│   └── main.ts       # 入口文件
├── .env              # 环境变量
├── index.html        # HTML 入口
├── package.json      # 项目配置
├── tsconfig.json     # TypeScript 配置
└── vite.config.ts    # Vite 配置
```

## 功能模块

1. **首页** - 视频生成功能
   - 视频主题和风格设置
   - 视频脚本编辑
   - 音频和字幕设置
   - 任务管理和状态查询

2. **模型管理** - 大语言模型配置
   - 添加、编辑、删除模型
   - 配置模型参数（API Key、Base URL等）

## 开发指南

### 安装依赖

```bash
cd sites
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器默认运行在 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

构建后的文件将输出到 `dist` 目录。

## API 代理配置

开发环境下，API 请求通过 Vite 代理转发到后端服务：

- 前端请求：`http://localhost:3000/api/v1/...`
- 代理到：`http://localhost:8000/api/v1/...`

## 部署说明

1. 构建前端项目：
   ```bash
   npm run build
   ```

2. 将 `dist` 目录下的文件复制到后端的静态文件目录

3. 确保后端 CORS 配置已正确设置，允许前端域名访问

## 注意事项

1. 确保后端服务已启动并运行在 http://localhost:8000
2. 开发环境中，前端通过 API 代理访问后端
3. 生产环境中，建议将前端静态文件部署在与后端相同的域名下，或正确配置 CORS
4. 所有 API 调用都遵循 RESTful 风格，通过 Axios 进行请求