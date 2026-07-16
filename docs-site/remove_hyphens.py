import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to parse the markdown and only replace hyphens outside of:
    # 1. Frontmatter
    # 2. Code blocks (```...```)
    # 3. Inline code (`...`)
    # 4. Links ([...](...))
    
    # A simple state machine or regex approach?
    # Actually, we can use a regex replacement with a function, keeping track of indices, 
    # but it's easier to just split by code blocks and frontmatter.
    
    # Let's split by ``` code blocks
    parts = re.split(r'(```.*?```)', content, flags=re.DOTALL)
    
    for i in range(len(parts)):
        if parts[i].startswith('```'):
            continue
            
        # Split by inline code
        inline_parts = re.split(r'(`[^`]+`)', parts[i])
        for j in range(len(inline_parts)):
            if inline_parts[j].startswith('`') and inline_parts[j].endswith('`'):
                continue
                
            # Replace Em dash (—) and En dash (–) with space
            text = inline_parts[j]
            text = re.sub(r'([a-zA-Z0-9])[—–]([a-zA-Z0-9])', r'\1 \2', text)
            
            # Replace hyphen (-) between alphanumeric characters with space
            # Be careful not to replace in URLs (http:// or https://)
            # A hacky way is to temporarily mask URLs
            urls = re.findall(r'https?://[^\s)\]]+', text)
            for idx, url in enumerate(urls):
                text = text.replace(url, f"__URL_{idx}__")
                
            # Now replace hyphen between words
            text = re.sub(r'([a-zA-Z0-9])-([a-zA-Z0-9])', r'\1 \2', text)
            
            # Unmask URLs
            for idx, url in enumerate(urls):
                text = text.replace(f"__URL_{idx}__", url)
                
            inline_parts[j] = text
            
        parts[i] = ''.join(inline_parts)
        
    final_content = ''.join(parts)
    
    # Fix frontmatter --- which might have been affected if it had alphanumeric around it (it doesn't, it's just ---)
    # But wait, what if the user wants `RTI-Agent` to remain? The prompt says "removed it from all the document", so I'll replace it everywhere.
    
    if final_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Updated {filepath}")

docs_dir = 'src/content/docs'
for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith('.mdx'):
            process_file(os.path.join(root, file))
