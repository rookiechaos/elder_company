# 图标文件说明

## ⚠️ 重要提示

以下图标文件需要创建才能完整支持PWA功能：

- `icon-192x192.png` - 必需
- `icon-512x512.png` - 必需  
- `badge-72x72.png` - 可选（已使用icon-192x192.png作为后备）

## 快速创建方法

### 使用在线工具（推荐）
1. 访问 https://realfavicongenerator.net/ 或 https://www.pwabuilder.com/imageGenerator
2. 上传一个512x512的源图标
3. 下载生成的图标文件
4. 将文件放置到 `frontend/public/` 目录

### 使用Python脚本（如果安装了Pillow）
```python
from PIL import Image, ImageDraw, ImageFont

# 创建简单的占位图标
def create_icon(size, filename):
    img = Image.new('RGB', (size, size), color='#f5e6e8')
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的"EC"文字
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size//3)
    except:
        font = ImageFont.load_default()
    
    text = "EC"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='#e8b4b8', font=font)
    
    img.save(filename)

create_icon(192, 'icon-192x192.png')
create_icon(512, 'icon-512x512.png')
```

### 临时占位方案

在创建正式图标之前，可以：
1. 使用纯色背景图片
2. 使用简单的文字图标
3. 从现有logo生成

## 当前状态

- ✅ manifest.json已配置图标路径
- ✅ Service Worker已更新使用icon作为badge后备
- ⚠️ 图标文件需要创建

详细说明请查看 `ICON_GUIDE.md`
