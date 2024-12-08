import os
import re
import yaml
from datetime import datetime

# 定义目录路径
directory = 'iCocoa.github.io/content/posts/'

# 遍历目录下的所有文件
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式提取 front matter
        match = re.match(r'---(.*?)---', content, re.DOTALL)
        if match:
            front_matter = match.group(1)
            # 解析 YAML
            data = yaml.safe_load(front_matter)
            
            # 更新或添加字段
            data['title'] = data.get('title', 'article title')
            data['date'] = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            data['description'] = data.get('description', 'Example article description')
            data['categories'] = data.get('categories', [])
            if "Tech" not in data['categories']:
                data['categories'].append("Tech")
            data['tags'] = data.get('tags', ['Test', 'Another test'])
            data['sidebar'] = 'left'
            data['hiddenFromHomePage'] = False
            
            # 将更新后的 front matter 转换回 YAML 格式
            new_front_matter = yaml.dump(data, sort_keys=False, allow_unicode=True)
            new_content = f'---\n{new_front_matter}---\n' + content[match.end():]
            
            # 将更新后的内容写回文件
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)

print("所有文件的 front matter 已更新。")