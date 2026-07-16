import os
import re

d = 'src/content/docs/agents'
for f in os.listdir(d):
    if f.endswith('.mdx'):
        path = os.path.join(d, f)
        content = open(path, 'r', encoding='utf-8').read()
        
        # If it already has correct frontmatter, skip
        if content.startswith('---'):
            # It might have broken frontmatter like `---\ntitle: "title"\n---\n\n---`
            # Let's clean it all up
            pass
            
        # Extract title from the first H1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).replace('"', "'") if title_match else f.replace('.mdx', '')
        
        # Remove any existing broken frontmatter (anything before the first '#')
        clean_content = content[content.find('#'):] if '#' in content else content
        
        new_content = f'---\ntitle: "{title}"\n---\n\n' + clean_content
        open(path, 'w', encoding='utf-8').write(new_content)
        print(f"Fixed {f}")
