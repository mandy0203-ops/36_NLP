import os
import shutil

# Define paths
source_dir = "03-outputs/youtube_downloader/downloads"
target_dir = "03-outputs/course_ai_agent_toolbox"

# Ensure target directory exists
os.makedirs(target_dir, exist_ok=True)

# Lesson Data
lessons = [
    {
        "title": "课程介绍：你的APP不非得是APP(小白也可以做AI Agent)",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/744215/lessons/2785168",
        "video_id": None,
        "note": "本節課無影片內容。"
    },
    {
        "title": "001 你的APP不非得是APP · 第一课",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/744215/lessons/2785170",
        "video_id": "MdxYAGwaysQ",
        "note": "影片 ID: MdxYAGwaysQ"
    },
    {
        "title": "002 你的APP不非得是APP · 第二课",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/811238/lessons/2820432",
        "video_id": "84RT3yHaJA8",
        "note": "影片 ID: 84RT3yHaJA8"
    },
    {
        "title": "003 你的APP不非得是APP · 第三课",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/811239/lessons/2881926",
        "video_id": "FZt6wC_Cj5g",
        "note": "影片 ID: FZt6wC_Cj5g"
    },
    {
        "title": "004 你的APP不非得是APP · 第四课",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/811240/lessons/2955033",
        "video_id": "5LtS4_UBeFM",
        "note": "影片 ID: 5LtS4_UBeFM"
    },
    {
        "title": "005 你的APP不非得是APP · 第五课",
        "url": "https://member.pathunfold.com/c/ai-agent-app-app/sections/811241/lessons/3084617",
        "video_id": "Vt726TJzS-M",
        "note": "影片 ID: Vt726TJzS-M"
    }
]

# Move videos and create text files
print("Starting organization...")

# Get list of downloaded files
if os.path.exists(source_dir):
    downloaded_files = os.listdir(source_dir)
    for filename in downloaded_files:
        src = os.path.join(source_dir, filename)
        dst = os.path.join(target_dir, filename)
        if os.path.isfile(src):
            shutil.move(src, dst)
            print(f"Moved video: {filename}")
else:
    print(f"Source directory {source_dir} does not exist. Skipping video move.")

for lesson in lessons:
    safe_title = lesson["title"].replace("/", "_").replace(":", "：")
    
    # 1. Create Text File
    text_filename = f"{safe_title}.md"
    text_path = os.path.join(target_dir, text_filename)
    
    content = f"""# {lesson['title']}

**課程連結**: {lesson['url']}

## 課程筆記
{lesson['note']}

---
*此文件由 AI Agent 自動生成，影片檔案請見同目錄下的視頻文件。*
"""
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created text note: {text_filename}")

print("Organization complete.")
