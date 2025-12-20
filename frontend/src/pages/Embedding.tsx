import { useState } from 'react'
import apiClient from '../api/client'

function Embedding() {
  const [text, setText] = useState('')
  const [embedding, setEmbedding] = useState<number[]>([])
  const [dimensions, setDimensions] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('テキストを入力してください')
      return
    }

    setLoading(true)
    setError('')
    setEmbedding([])

    try {
      const res = await apiClient.post('/embedding/generate', {
        text,
        model: 'text-embedding-004',
      })
      setEmbedding(res.data.embedding)
      setDimensions(res.data.dimensions)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">エンベディング生成</h2>
      <div className="mb-6">
        <label htmlFor="text" className="block text-sm font-medium text-gray-300 mb-2">
          テキスト
        </label>
        <textarea
          id="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="エンベディングを生成したいテキストを入力してください"
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

      {embedding.length > 0 && (
        <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">エンベディング結果</h3>
          <p className="text-gray-300 mb-4">次元数: {dimensions}</p>
          <div className="text-gray-300 whitespace-pre-wrap break-words max-h-[500px] overflow-y-auto">
            {embedding.slice(0, 10).map((val, idx) => (
              <span key={idx}>{val.toFixed(4)}, </span>
            ))}
            ... (全{embedding.length}次元)
          </div>
        </div>
      )}
    </div>
  )
}

export default Embedding

