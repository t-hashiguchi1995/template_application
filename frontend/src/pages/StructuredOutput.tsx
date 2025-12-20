import { useState } from 'react'
import apiClient from '../api/client'

function StructuredOutput() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('プロンプトを入力してください')
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const res = await apiClient.post('/structured-output/generate', {
        prompt,
        schema: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            summary: { type: 'string' },
            tags: {
              type: 'array',
              items: { type: 'string' },
            },
            rating: { type: 'number', minimum: 0, maximum: 10 },
          },
          required: ['title', 'summary'],
        },
        model: 'gemini-3-pro',
      })
      setResponse(res.data.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">構造化出力</h2>
      <div className="mb-6">
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
          プロンプト
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: 映画「インターステラー」について説明してください"
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
        />
      </div>
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
      >
        {loading ? '生成中...' : '生成'}
      </button>

      {error && (
        <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {response && (
        <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">構造化された結果</h3>
          <div className="text-gray-300 whitespace-pre-wrap break-words max-h-[500px] overflow-y-auto font-mono text-sm">
            {JSON.stringify(response, null, 2)}
          </div>
        </div>
      )}
    </div>
  )
}

export default StructuredOutput

