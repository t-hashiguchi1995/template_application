import { useState } from 'react'
import apiClient from '../api/client'

type AspectRatio = '1:1' | '2:3' | '3:2' | '3:4' | '4:3' | '4:5' | '5:4' | '9:16' | '16:9' | '21:9'
type Resolution = '1K' | '2K' | '4K'

type Tab = 'generate' | 'edit' | 'compose' | 'chat'

function ImageGeneration() {
  const [activeTab, setActiveTab] = useState<Tab>('generate')
  
  // 画像生成
  const [prompt, setPrompt] = useState('')
  const [model, setModel] = useState('gemini-2.5-flash-image')
  const [aspectRatio, setAspectRatio] = useState<AspectRatio | ''>('')
  const [resolution, setResolution] = useState<Resolution | ''>('')
  const [imageUrl, setImageUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 画像編集
  const [editPrompt, setEditPrompt] = useState('')
  const [editFile, setEditFile] = useState<File | null>(null)
  const [editPreview, setEditPreview] = useState('')
  const [editModel, setEditModel] = useState('gemini-3-pro-image-preview')
  const [editAspectRatio, setEditAspectRatio] = useState<AspectRatio | ''>('')
  const [editResolution, setEditResolution] = useState<Resolution | ''>('')
  const [editedImageUrl, setEditedImageUrl] = useState('')
  const [editLoading, setEditLoading] = useState(false)
  const [editError, setEditError] = useState('')

  // 複数画像合成
  const [composePrompt, setComposePrompt] = useState('')
  const [composeFiles, setComposeFiles] = useState<File[]>([])
  const [composePreviews, setComposePreviews] = useState<string[]>([])
  const [composeModel, setComposeModel] = useState('gemini-3-pro-image-preview')
  const [composeAspectRatio, setComposeAspectRatio] = useState<AspectRatio | ''>('')
  const [composeResolution, setComposeResolution] = useState<Resolution | ''>('')
  const [composedImageUrl, setComposedImageUrl] = useState('')
  const [composeLoading, setComposeLoading] = useState(false)
  const [composeError, setComposeError] = useState('')

  // マルチターン編集
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant', text?: string, imageUrl?: string }>>([])
  const [chatModel, setChatModel] = useState('gemini-3-pro-image-preview')
  const [chatAspectRatio, setChatAspectRatio] = useState<AspectRatio | ''>('')
  const [chatResolution, setChatResolution] = useState<Resolution | ''>('')
  const [chatSessionId, setChatSessionId] = useState<string | null>(null)
  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('プロンプトを入力してください')
      return
    }

    setLoading(true)
    setError('')
    setImageUrl('')

    try {
      // Nano Bananaモデルを確実に使用（imagen-4.0などの古いモデルを排除）
      const selectedModel = model || 'gemini-2.5-flash-image'
      
      // 無効なモデル名をチェック
      if (selectedModel.includes('imagen')) {
        setError('imagenモデルはサポートされていません。Nano Bananaモデルを使用してください。')
        setLoading(false)
        return
      }

      const payload: any = {
        prompt,
        model: selectedModel,
      }
      if (aspectRatio) payload.aspect_ratio = aspectRatio
      if (resolution) payload.resolution = resolution

      console.log('画像生成リクエスト:', payload) // デバッグ用
      const res = await apiClient.post('/image/generate', payload)
      setImageUrl(res.data.image_url)
    } catch (err: any) {
      console.error('画像生成エラー:', err) // デバッグ用
      const errorDetail = err.response?.data?.detail || 'エラーが発生しました'
      setError(errorDetail)
      
      // エラーメッセージにNano Bananaモデルへの誘導を追加
      if (errorDetail.includes('imagen') || errorDetail.includes('サポートされていません')) {
        setError(`${errorDetail}\n\n💡 Nano Bananaモデル（gemini-2.5-flash-image または gemini-3-pro-image-preview）を選択してください。`)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, type: 'edit' | 'compose') => {
    const files = e.target.files
    if (!files) return

    if (type === 'edit') {
      const file = files[0]
      setEditFile(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setEditPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    } else {
      const fileArray = Array.from(files)
      setComposeFiles(fileArray)
      const readers = fileArray.map(file => {
        const reader = new FileReader()
        return new Promise<string>((resolve) => {
          reader.onload = (e) => resolve(e.target?.result as string)
          reader.readAsDataURL(file)
        })
      })
      Promise.all(readers).then(previews => setComposePreviews(previews))
    }
  }

  const handleEdit = async () => {
    if (!editPrompt.trim()) {
      setEditError('プロンプトを入力してください')
      return
    }
    if (!editFile) {
      setEditError('画像を選択してください')
      return
    }

    setEditLoading(true)
    setEditError('')
    setEditedImageUrl('')

    try {
      const formData = new FormData()
      formData.append('file', editFile)
      formData.append('prompt', editPrompt)
      formData.append('model', editModel)
      if (editAspectRatio) formData.append('aspect_ratio', editAspectRatio)
      if (editResolution) formData.append('resolution', editResolution)

      const res = await apiClient.post('/image/edit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setEditedImageUrl(res.data.image_url)
    } catch (err: any) {
      setEditError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setEditLoading(false)
    }
  }

  const handleCompose = async () => {
    if (!composePrompt.trim()) {
      setComposeError('プロンプトを入力してください')
      return
    }
    if (composeFiles.length === 0) {
      setComposeError('画像を選択してください')
      return
    }

    setComposeLoading(true)
    setComposeError('')
    setComposedImageUrl('')

    try {
      const formData = new FormData()
      composeFiles.forEach(file => {
        formData.append('files', file)
      })
      formData.append('prompt', composePrompt)
      formData.append('model', composeModel)
      if (composeAspectRatio) formData.append('aspect_ratio', composeAspectRatio)
      if (composeResolution) formData.append('resolution', composeResolution)

      const res = await apiClient.post('/image/compose', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setComposedImageUrl(res.data.image_url)
    } catch (err: any) {
      setComposeError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setComposeLoading(false)
    }
  }

  const handleChatSend = async () => {
    if (!chatMessage.trim()) {
      setChatError('メッセージを入力してください')
      return
    }

    setChatLoading(true)
    setChatError('')
    const userMessage = chatMessage
    setChatMessage('')
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }])

    try {
      const payload: any = {
        message: userMessage,
        model: chatModel,
        session_id: chatSessionId,
      }
      if (chatAspectRatio) payload.aspect_ratio = chatAspectRatio
      if (chatResolution) payload.resolution = chatResolution

      const res = await apiClient.post('/image/chat', payload)
      
      if (!chatSessionId) {
        setChatSessionId(res.data.session_id)
      }

      setChatHistory(prev => [...prev, {
        role: 'assistant',
        text: res.data.text,
        imageUrl: res.data.image_url,
      }])
    } catch (err: any) {
      setChatError(err.response?.data?.detail || 'エラーが発生しました')
      setChatHistory(prev => prev.slice(0, -1)) // ユーザーメッセージを削除
    } finally {
      setChatLoading(false)
    }
  }

  const renderSelect = <T extends string>(
    label: string,
    value: T | '',
    options: T[],
    onChange: (value: T | '') => void,
    optionLabels?: Record<string, string>
  ) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-300 mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T | '')}
        className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">デフォルト</option>
        {options.map(opt => (
          <option key={opt} value={opt}>
            {optionLabels?.[opt] || opt}
          </option>
        ))}
      </select>
    </div>
  )

  const modelLabels: Record<string, string> = {
    'gemini-2.5-flash-image': 'Nano Banana (高速・効率的)',
    'gemini-3-pro-image-preview': 'Nano Banana Pro (高品質・思考モード)',
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">Nano Banana 画像生成</h2>
      
      {/* タブ */}
      <div className="flex gap-2 mb-6 border-b border-gray-700">
        {(['generate', 'edit', 'compose', 'chat'] as Tab[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium transition-colors duration-200 ${
              activeTab === tab
                ? 'text-white border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab === 'generate' && '画像生成'}
            {tab === 'edit' && '画像編集'}
            {tab === 'compose' && '画像合成'}
            {tab === 'chat' && 'マルチターン編集'}
          </button>
        ))}
      </div>

      {/* 画像生成タブ */}
      {activeTab === 'generate' && (
        <div>
          <div className="mb-6">
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
              プロンプト <span className="text-red-400">*</span>
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="生成したい画像の説明を入力してください（例: 夕焼けの海辺に佇む少女）"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
            />
          </div>

          <div className="mb-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">生成設定</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Nano Banana モデル <span className="text-blue-400">*</span>
              </label>
              <select
                value={model}
                onChange={(e) => {
                  const newModel = e.target.value
                  console.log('モデル変更:', newModel) // デバッグ用
                  setModel(newModel)
                }}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="gemini-2.5-flash-image">Nano Banana (高速・効率的)</option>
                <option value="gemini-3-pro-image-preview">Nano Banana Pro (高品質・思考モード)</option>
              </select>
              <p className="text-xs text-gray-400 mt-1">
                現在選択中: {modelLabels[model] || model}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {renderSelect('アスペクト比', aspectRatio, ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'], setAspectRatio)}
              {renderSelect('解像度', resolution, ['1K', '2K', '4K'], setResolution)}
            </div>
            <p className="text-xs text-gray-400 mt-2">
              💡 アスペクト比と解像度は省略可能です。省略時はモデルのデフォルト値が使用されます。
            </p>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
          >
            {loading ? '生成中...' : '画像を生成'}
          </button>

          {error && (
            <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
              {error}
            </div>
          )}

          {imageUrl && (
            <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">生成された画像</h3>
              <img src={imageUrl} alt="Generated" className="max-w-full rounded-lg" />
            </div>
          )}
        </div>
      )}

      {/* 画像編集タブ */}
      {activeTab === 'edit' && (
        <div>
          <div className="mb-6">
            <label htmlFor="edit-file" className="block text-sm font-medium text-gray-300 mb-2">
              編集する画像を選択 <span className="text-red-400">*</span>
            </label>
            <input
              id="edit-file"
              type="file"
              accept="image/*"
              onChange={(e) => handleFileSelect(e, 'edit')}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
            />
            {editPreview && (
              <div className="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
                <p className="text-sm text-gray-300 mb-2">プレビュー:</p>
                <img src={editPreview} alt="Preview" className="max-w-xs rounded-lg" />
              </div>
            )}
          </div>

          <div className="mb-6">
            <label htmlFor="edit-prompt" className="block text-sm font-medium text-gray-300 mb-2">
              編集プロンプト <span className="text-red-400">*</span>
            </label>
            <textarea
              id="edit-prompt"
              value={editPrompt}
              onChange={(e) => setEditPrompt(e.target.value)}
              placeholder="どのように編集したいか説明してください（例: 背景を青に変更、猫を追加など）"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
            />
          </div>

          <div className="mb-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">編集設定</h3>
            {renderSelect('Nano Banana モデル', editModel, ['gemini-2.5-flash-image', 'gemini-3-pro-image-preview'], setEditModel, modelLabels)}
            <div className="grid grid-cols-2 gap-4 mt-4">
              {renderSelect('アスペクト比', editAspectRatio, ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'], setEditAspectRatio)}
              {renderSelect('解像度', editResolution, ['1K', '2K', '4K'], setEditResolution)}
            </div>
          </div>

          <button
            onClick={handleEdit}
            disabled={editLoading || !editFile || !editPrompt.trim()}
            className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
          >
            {editLoading ? '編集中...' : '画像を編集'}
          </button>

          {editError && (
            <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
              {editError}
            </div>
          )}

          {editedImageUrl && (
            <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">編集された画像</h3>
              <img src={editedImageUrl} alt="Edited" className="max-w-full rounded-lg" />
            </div>
          )}
        </div>
      )}

      {/* 画像合成タブ */}
      {activeTab === 'compose' && (
        <div>
          <div className="mb-6">
            <label htmlFor="compose-files" className="block text-sm font-medium text-gray-300 mb-2">
              合成する画像を選択（複数選択可） <span className="text-red-400">*</span>
            </label>
            <input
              id="compose-files"
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => handleFileSelect(e, 'compose')}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
            />
            {composePreviews.length > 0 && (
              <div className="mt-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
                <p className="text-sm text-gray-300 mb-2">選択された画像 ({composePreviews.length}枚):</p>
                <div className="flex gap-4 flex-wrap">
                  {composePreviews.map((preview, idx) => (
                    <img key={idx} src={preview} alt={`Preview ${idx + 1}`} className="max-w-xs rounded-lg" />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="mb-6">
            <label htmlFor="compose-prompt" className="block text-sm font-medium text-gray-300 mb-2">
              合成プロンプト <span className="text-red-400">*</span>
            </label>
            <textarea
              id="compose-prompt"
              value={composePrompt}
              onChange={(e) => setComposePrompt(e.target.value)}
              placeholder="画像をどのように合成したいか説明してください（例: これらの人物のオフィス集合写真を作成）"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
            />
          </div>

          <div className="mb-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">合成設定</h3>
            {renderSelect('Nano Banana モデル', composeModel, ['gemini-2.5-flash-image', 'gemini-3-pro-image-preview'], setComposeModel, modelLabels)}
            <div className="grid grid-cols-2 gap-4 mt-4">
              {renderSelect('アスペクト比', composeAspectRatio, ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'], setComposeAspectRatio)}
              {renderSelect('解像度', composeResolution, ['1K', '2K', '4K'], setComposeResolution)}
            </div>
          </div>

          <button
            onClick={handleCompose}
            disabled={composeLoading || composeFiles.length === 0 || !composePrompt.trim()}
            className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
          >
            {composeLoading ? '合成中...' : '画像を合成'}
          </button>

          {composeError && (
            <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
              {composeError}
            </div>
          )}

          {composedImageUrl && (
            <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">合成された画像</h3>
              <img src={composedImageUrl} alt="Composed" className="max-w-full rounded-lg" />
            </div>
          )}
        </div>
      )}

      {/* マルチターン編集タブ */}
      {activeTab === 'chat' && (
        <div>
          <div className="mb-6 p-4 bg-gray-800 border border-gray-700 rounded-lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">チャット設定</h3>
            {renderSelect('Nano Banana モデル', chatModel, ['gemini-2.5-flash-image', 'gemini-3-pro-image-preview'], setChatModel, modelLabels)}
            <div className="grid grid-cols-2 gap-4 mt-4">
              {renderSelect('アスペクト比', chatAspectRatio, ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'], setChatAspectRatio)}
              {renderSelect('解像度', chatResolution, ['1K', '2K', '4K'], setChatResolution)}
            </div>
            <p className="text-xs text-gray-400 mt-2">
              💡 会話形式で画像の生成と編集を続けます。前の会話のコンテキストが保持されます。
            </p>
          </div>

          <div className="mb-6 h-96 overflow-y-auto bg-gray-800 border border-gray-700 rounded-lg p-4">
            {chatHistory.length === 0 ? (
              <p className="text-gray-400 text-center">会話を開始してください</p>
            ) : (
              chatHistory.map((msg, idx) => (
                <div key={idx} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-white'
                  }`}>
                    {msg.text && <p>{msg.text}</p>}
                    {msg.imageUrl && (
                      <img src={msg.imageUrl} alt="Generated" className="mt-2 max-w-full rounded-lg" />
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleChatSend()}
              placeholder="メッセージを入力..."
              className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleChatSend}
              disabled={chatLoading}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
            >
              {chatLoading ? '送信中...' : '送信'}
            </button>
          </div>

          {chatError && (
            <div className="mt-4 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
              {chatError}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ImageGeneration
