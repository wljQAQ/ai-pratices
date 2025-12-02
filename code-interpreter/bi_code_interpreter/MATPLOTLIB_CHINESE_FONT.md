# Matplotlib 中文字体配置指南

## 问题描述

使用matplotlib生成图表时，中文显示为方块（口字）乱码。

## 原因

matplotlib默认使用的字体不包含中文字符，需要手动配置支持中文的字体。

## 解决方案

### 方案1: 使用rcParams配置（推荐⭐⭐⭐⭐⭐）

在绘图代码的开头添加：

```python
import matplotlib.pyplot as plt

# 配置中文字体
plt.rcParams['font.sans-serif'] = [
    'Arial Unicode MS',  # macOS
    'SimHei',            # Windows
    'Microsoft YaHei',   # Windows
    'PingFang SC',       # macOS
    'Heiti TC',          # macOS
    'WenQuanYi Zen Hei'  # Linux
]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
```

**工作原理**:
- matplotlib会按顺序尝试列表中的字体
- 自动选择系统中第一个可用的字体
- 跨平台兼容（Windows/macOS/Linux）

### 方案2: 查看系统可用字体

如果方案1不生效，可以查看系统中实际可用的中文字体：

```python
import matplotlib.font_manager as fm

# 列出所有可用字体
fonts = fm.findSystemFonts()
print(f"共找到 {len(fonts)} 个字体")

# 查找包含中文的字体
chinese_fonts = []
for font in fonts:
    try:
        font_obj = fm.FontProperties(fname=font)
        font_name = font_obj.get_name()
        # 常见中文字体关键词
        if any(keyword in font_name.lower() for keyword in 
               ['simhei', 'simsun', 'microsoftyahei', 'microsoft yahei', 
                'pingfang', 'heiti', 'wenquanyi', 'arial unicode']):
            chinese_fonts.append(font_name)
    except:
        pass

print("\n可用的中文字体:")
for font in set(chinese_fonts):
    print(f"  - {font}")
```

### 方案3: 指定字体文件路径（精确控制）

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 指定字体文件
font_path = '/System/Library/Fonts/PingFang.ttc'  # macOS示例
font_prop = fm.FontProperties(fname=font_path)

# 在绘图时使用
plt.title('标题', fontproperties=font_prop)
plt.xlabel('X轴', fontproperties=font_prop)
plt.ylabel('Y轴', fontproperties=font_prop)
```

## 完整示例

### 基础柱状图

```python
import matplotlib.pyplot as plt
import numpy as np

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
categories = ['苹果', '香蕉', '橙子', '葡萄']
values = [23, 45, 56, 78]

# 绘图
plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='skyblue')
plt.xlabel('水果类型', fontsize=12)
plt.ylabel('销售量', fontsize=12)
plt.title('水果销售情况统计', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)

# 保存
plt.savefig('./fruit_sales.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ 图表已保存，中文正常显示")
```

### 多子图示例

```python
import matplotlib.pyplot as plt
import numpy as np

# 全局配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 子图1: 柱状图
axes[0, 0].bar(['第一季度', '第二季度', '第三季度', '第四季度'], [100, 120, 140, 160])
axes[0, 0].set_title('季度销售额')
axes[0, 0].set_ylabel('金额（万元）')

# 子图2: 折线图
x = np.arange(1, 13)
axes[0, 1].plot(x, np.random.randint(50, 100, 12), marker='o')
axes[0, 1].set_title('月度趋势')
axes[0, 1].set_xlabel('月份')
axes[0, 1].set_ylabel('数量')

# 子图3: 饼图
labels = ['产品A', '产品B', '产品C', '产品D']
sizes = [30, 25, 20, 25]
axes[1, 0].pie(sizes, labels=labels, autopct='%1.1f%%')
axes[1, 0].set_title('产品占比')

# 子图4: 散点图
axes[1, 1].scatter(np.random.rand(50), np.random.rand(50), alpha=0.5)
axes[1, 1].set_title('数据分布')
axes[1, 1].set_xlabel('X轴')
axes[1, 1].set_ylabel('Y轴')

plt.tight_layout()
plt.savefig('./dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ 多子图仪表盘已生成")
```

## 常见问题

### Q1: 为什么设置后还是乱码？

**A**: 可能的原因：
1. 系统中没有安装指定的中文字体
2. 字体名称拼写错误
3. 需要清除matplotlib缓存

**解决**:
```bash
# 清除matplotlib缓存
rm -rf ~/.matplotlib/fontlist-*.json
```

### Q2: macOS上推荐哪个字体？

**A**: 按优先级：
1. `Arial Unicode MS` - 最全面
2. `PingFang SC` - 系统默认，现代
3. `Heiti TC` - 黑体，传统

### Q3: Windows上推荐哪个字体？

**A**: 按优先级：
1. `Microsoft YaHei` - 微软雅黑，最常用
2. `SimHei` - 黑体
3. `SimSun` - 宋体

### Q4: 负号显示为方块怎么办？

**A**: 添加这行配置：
```python
plt.rcParams['axes.unicode_minus'] = False
```

### Q5: Jupyter Notebook中不生效？

**A**: 确保在导入matplotlib后、绘图前配置：
```python
import matplotlib.pyplot as plt

# 必须在这里配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 然后再绘图
plt.plot([1, 2, 3], [1, 2, 3])
```

## 在CODE_GENERATOR中的应用

现在我们的代码生成器会自动在可视化代码中添加中文字体配置：

```python
# 自动生成的代码包含
import matplotlib.pyplot as plt

# 配置中文字体（自动添加）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei',
                                     'PingFang SC', 'Heiti TC', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# 后续绘图代码...
```

## 最佳实践

1. ✅ **在文件开头统一配置**: 所有使用matplotlib的代码开头就配置
2. ✅ **使用字体列表**: 支持多平台自动适配
3. ✅ **配置负号处理**: 避免负号显示异常
4. ✅ **测试多平台**: 确保Windows/macOS/Linux都能正常显示
5. ✅ **添加说明注释**: 让其他开发者知道为什么要配置

## 总结

**核心代码（复制即用）**:

```python
import matplotlib.pyplot as plt

# 解决中文乱码（跨平台）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei',
                                     'PingFang SC', 'Heiti TC', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号问题

# 开始绘图...
```

这样就能在所有平台上正常显示中文了！✅
