import { useState } from 'react'
import apiClient from '../api/client'

function Agent() {
  const [prompt, setPrompt] = useState('')
  const [tools, setTools] = useState<string[]>([])
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChat = async () => {
    if (!prompt.trim()) {
      setError('プロンプトを入力してください')
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const res = await apiClient.post('/agent/chat', {
        prompt,
        tools: tools.length > 0 ? tools : undefined,
        model: 'gemini-3-pro-preview',
      })
      setResponse(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const toggleTool = (tool: string) => {
    setTools((prev) =>
      prev.includes(tool) ? prev.filter((t) => t !== tool) : [...prev, tool]
    )
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">エージェント（ツール使用可能）</h2>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          使用するツール
        </label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={tools.includes('google_search')}
              onChange={() => toggleTool('google_search')}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-2"
            />
            Google検索
          </label>
          <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
            <input
              type="checkbox"
              checked={tools.includes('google_maps')}
              onChange={() => toggleTool('google_maps')}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-2"
            />
            Google Maps
          </label>
        </div>
      </div>
      <div className="mb-6">
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
          プロンプト
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 最新のAI技術について調べて"
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
        />
      </div>
      <button
        onClick={handleChat}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
      >
        {loading ? '実行中...' : '実行'}
      </button>

      {error && (
        <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {response && (
        <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">結果</h3>
          <p className="text-gray-300 mb-4">
            使用されたツール: {response.tools_used?.join(', ') || 'なし'}
          </p>
          <div className="text-gray-300 whitespace-pre-wrap break-words max-h-[500px] overflow-y-auto">
            {response.response}
          </div>
        </div>
      )}
    </div>
  )
}

export default Agent

