"""
設定管理
"""
import os
from dotenv import load_dotenv

load_dotenv()

# GEMINI_API_KEYまたはGOOGLE_API_KEYのいずれかから読み込む
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEYまたはGOOGLE_API_KEY環境変数が設定されていません")

# デフォルトモデル設定
DEFAULT_TEXT_MODEL = "gemini-2.5-flash"
DEFAULT_CHAT_MODEL = "gemini-3-pro-preview"  # チャット & 思考用
DEFAULT_ANALYSIS_MODEL = "gemini-3-pro-preview"  # 画像・動画分析、リサーチ、開発スタジオ用
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image"  # 画像生成はNano Bananaを使用
DEFAULT_IMAGE_ANALYSIS_MODEL = "gemini-2.5-flash-image"  # 画像分析・編集用
DEFAULT_VIDEO_MODEL = "veo-3.1-fast-generate-preview"  # 動画生成はVeo APIを使用
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"  # TTS用モデル
DEFAULT_PRODUCTIVITY_MODEL = "gemini-3-pro"  # タスク & ナレッジ用

