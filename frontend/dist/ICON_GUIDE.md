# PWA图标创建指南

## 需要的图标文件

为了完整支持PWA功能，需要创建以下图标文件：

1. **icon-192x192.png** - 192x192像素，用于Android主屏幕图标
2. **icon-512x512.png** - 512x512像素，用于Android启动画面和高质量显示
3. **badge-72x72.png** - 72x72像素，用于推送通知徽章（可选，已使用icon-192x192.png作为后备）

## 图标设计要求

### 品牌色彩
- 主题色: `#f5e6e8` (浅粉色)
- 强调色: `#e8b4b8` (粉红色)
- 背景色: `#faf9f7` (米白色)

### 设计规范
- **Maskable图标**: 图标应支持maskable，确保在不同设备上正确显示
- **安全区域**: 图标内容应在安全区域内（约80%的中心区域）
- **简洁设计**: 图标应简洁明了，在小尺寸下也能清晰识别
- **品牌一致性**: 图标应体现"照护协同"的理念

### 建议设计元素
- 可以使用心形、手、或照护相关的图标
- 结合"E"或"EC"字母设计
- 使用柔和的渐变色（#f5e6e8 到 #e8b4b8）

## 创建方法

### 方法1: 使用在线工具
1. 访问 [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
2. 上传一个高分辨率图标（至少512x512）
3. 自动生成所有需要的尺寸

### 方法2: 使用设计工具
1. 使用 Figma、Sketch 或 Adobe Illustrator 创建图标
2. 导出为PNG格式
3. 确保尺寸精确（192x192, 512x512）

### 方法3: 使用命令行工具
```bash
# 安装 pwa-asset-generator
npm install -g pwa-asset-generator

# 从源图标生成所有尺寸
pwa-asset-generator source-icon.png public/ --icon-only
```

## 文件位置

所有图标文件应放置在：
```
elder_company/frontend/public/
├── icon-192x192.png
├── icon-512x512.png
└── badge-72x72.png (可选)
```

## 验证

创建图标后，请验证：
1. 文件大小合理（建议每个图标 < 100KB）
2. 图标在不同设备上显示正常
3. PWA安装后图标正确显示
4. 支持maskable格式（如果使用）

## 临时解决方案

在创建正式图标之前，可以使用以下临时方案：
- 使用纯色背景 + 文字
- 使用简单的几何图形
- 使用品牌logo的简化版本

## 注意事项

- 图标文件必须存在，否则PWA安装会失败
- 确保图标文件路径与manifest.json中的路径一致
- 定期更新图标以保持品牌一致性
