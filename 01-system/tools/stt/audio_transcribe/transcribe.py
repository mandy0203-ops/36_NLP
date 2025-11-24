#!/usr/bin/env python3
"""
Audio Transcription Tool - 主程式
專業的語音轉錄工具，支援雙 STT 引擎、自訂詞典、智能格式化
"""
import os
import sys
import argparse
from pathlib import Path

# 添加模組路徑
sys.path.insert(0, str(Path(__file__).parent))

from modules.stt_engine import STTEngine
from modules.formatter import Formatter
from modules.output_manager import OutputManager

def print_header():
    """顯示工具標題"""
    print("=" * 60)
    print("🎙️  Audio Transcription Tool v1.0")
    print("=" * 60)
    print()

def get_file_info(audio_path):
    """取得檔案資訊"""
    size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    return {
        'path': audio_path,
        'name': Path(audio_path).stem,
        'size_mb': size_mb
    }

def select_engine(stt_engine, file_info):
    """互動式選擇引擎"""
    engines = stt_engine.get_available_engines()
    
    print(f"📁 檔案資訊")
    print(f"   檔案：{Path(file_info['path']).name}")
    print(f"   大小：{file_info['size_mb']:.1f} MB")
    print()
    
    print("🤖 可用的 STT 引擎：")
    print()
    
    available_engines = []
    
    for i, (key, info) in enumerate(engines.items(), 1):
        if not info['available']:
            continue
        
        available_engines.append(key)
        
        print(f"[{i}] {info['name']}")
        print(f"    ✅ {' / '.join(info['pros'])}")
        for con in info['cons']:
            print(f"    ⚠️  {con}")
        print()
    
    if not available_engines:
        print("❌ 錯誤：沒有可用的引擎")
        print("請檢查 API Keys 設定")
        sys.exit(1)
    
    # 詢問選擇
    while True:
        try:
            choice = input(f"請選擇引擎 [1-{len(available_engines)}]（預設：1）: ").strip()
            if not choice:
                choice = "1"
            
            idx = int(choice) - 1
            if 0 <= idx < len(available_engines):
                selected = available_engines[idx]
                print(f"\n✅ 已選擇：{engines[selected]['name']}")
                print()
                return selected
            else:
                print(f"請輸入 1-{len(available_engines)} 之間的數字")
        except ValueError:
            print("請輸入有效的數字")
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="專業語音轉錄工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s --input audio.mp3
  %(prog)s --input audio.mp3 --engine elevenlabs
  %(prog)s --input audio.mp3 --output-name "EP01"
        """
    )
    
    parser.add_argument('--input', required=True, help='輸入音檔路徑')
    parser.add_argument('--engine', choices=['elevenlabs', 'groq'], help='指定 STT 引擎（跳過選擇）')
    parser.add_argument('--output-name', help='自訂輸出資料夾名稱')
    parser.add_argument('--skip-format', action='store_true', help='跳過格式化')
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not os.path.exists(args.input):
        print(f"❌ 錯誤：找不到檔案 {args.input}")
        sys.exit(1)
    
    print_header()
    
    # 初始化
    config_path = Path(__file__).parent / "config.yaml"
    rules_path = Path(__file__).parent / "formatting_rules.yaml"
    dict_path = Path(__file__).parent / "custom_dict.yaml"
    
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    stt_engine = STTEngine(config_path)
    formatter = Formatter(rules_path, dict_path)
    output_mgr = OutputManager(config)
    
    # 取得檔案資訊
    file_info = get_file_info(args.input)
    
    # 選擇引擎
    if args.engine:
        engine = args.engine
        print(f"🤖 使用引擎：{engine}")
        print()
    else:
        engine = select_engine(stt_engine, file_info)
    
    # 階段 1：轉錄
    print("📝 階段 1：語音轉錄")
    print("-" * 60)
    
    try:
        transcription = stt_engine.transcribe(args.input, engine)
        print("✅ 轉錄完成")
        print()
    except Exception as e:
        print(f"❌ 轉錄失敗：{e}")
        sys.exit(1)
    
    # 階段 2：格式化
    formatted_srt = None
    formatted_text = None
    
    if not args.skip_format:
        print("✨ 階段 2：智能格式化")
        print("-" * 60)
        
        try:
            # 格式化 SRT
            formatted_srt = formatter.format_srt(transcription['segments'])
            
            # 格式化純文字
            formatted_text = formatter.format_text(transcription['text'])
            
            print("✅ 格式化完成")
            print()
        except Exception as e:
            print(f"⚠️  格式化失敗：{e}")
            print("將繼續產生未格式化版本")
            print()
    
    # 階段 3：輸出
    print("💾 階段 3：儲存檔案")
    print("-" * 60)
    
    try:
        # 創建輸出資料夾
        output_folder = output_mgr.create_output_folder(
            file_info['name'],
            args.output_name
        )
        
        # 處理原始音檔
        audio_dest = output_mgr.handle_audio(args.input, output_folder)
        
        # 儲存轉錄結果
        files = output_mgr.save_transcription(
            output_folder,
            file_info['name'],
            transcription,
            formatted_text
        )
        
        # 儲存格式化 SRT
        if formatted_srt:
            formatted_srt_path = output_mgr.save_formatted_srt(
                output_folder,
                file_info['name'],
                formatted_srt
            )
            files['srt_formatted'] = formatted_srt_path
        
        # 生成 metadata
        metadata_info = {
            'engine': engine,
            'model': config['engines'][engine]['model'],
            'original_file': args.input,
            'file_size': f"{file_info['size_mb']:.1f} MB",
            'formatting_applied': not args.skip_format,
            'custom_dict_used': True,
            'output_files': {k: str(v.name) for k, v in files.items()}
        }
        
        metadata_path = output_mgr.generate_metadata(output_folder, metadata_info)
        
        print(f"✅ 檔案已儲存至：{output_folder}")
        print()
        print("📁 已產生檔案：")
        print(f"   ✅ {file_info['name']}.srt（原始字幕）")
        print(f"   ✅ {file_info['name']}.txt（原始文字）")
        if formatted_srt:
            print(f"   ✅ {file_info['name']}_formatted.srt（格式化字幕）⭐")
        if formatted_text:
            print(f"   ✅ {file_info['name']}_formatted.txt（格式化文字）⭐")
        print(f"   ✅ _metadata.yaml（轉錄資訊）")
        print()
        
        print("=" * 60)
        print("🎉 轉錄完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 儲存失敗：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
