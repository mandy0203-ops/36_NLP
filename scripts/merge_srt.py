import re
import os

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines, but handle potential whitespace variations
    blocks = re.split(r'\n\s*\n', content.strip())
    parsed_blocks = []
    
    for block in blocks:
        if not block.strip():
            continue
        lines = block.split('\n')
        if len(lines) >= 3:
            index = lines[0].strip()
            timestamp = lines[1].strip()
            text = '\n'.join(lines[2:])
            parsed_blocks.append({
                'index': index,
                'timestamp': timestamp,
                'text': text
            })
    return parsed_blocks

def write_srt(blocks, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, block in enumerate(blocks, 1):
            f.write(f"{i}\n")
            f.write(f"{block['timestamp']}\n")
            f.write(f"{block['text']}\n\n")

def main():
    original_srt = "/Users/xiangyun/Desktop/tars-001/02-inputs/EP49_Friends_Boundaries.srt"
    reference_srt = "/Users/xiangyun/Desktop/tars-001/02-inputs/reference_subs.srt"
    
    print(f"Reading {original_srt}...")
    original_blocks = parse_srt(original_srt)
    
    print(f"Reading {reference_srt}...")
    reference_blocks = parse_srt(reference_srt)
    
    # Keep first 11 blocks from original
    teaser_blocks = original_blocks[:11]
    
    # Use all blocks from reference
    # Note: We assume reference starts from the beginning of the main content
    # If reference has its own intro that overlaps, we might need to adjust.
    # Based on user request "fix typos", we assume reference is the "correct" version of the main content.
    # The user said "reference file... correct typos".
    # The plan was: "Reads reference_subs.srt... Renumbers items... Combines".
    
    merged_blocks = teaser_blocks + reference_blocks
    
    print(f"Merged {len(teaser_blocks)} blocks from original and {len(reference_blocks)} blocks from reference.")
    print(f"Total blocks: {len(merged_blocks)}")
    
    write_srt(merged_blocks, original_srt)
    print(f"Overwrote {original_srt}")

if __name__ == "__main__":
    main()
