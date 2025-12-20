import { useState } from 'react'
import apiClient from '../api/client'

function TextGeneration() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('プロンプトを入力してください')
      return
    }

    setLoading(true)
    setError('')
    setResponse('')

    try {
      console.log('API Request:', {
        url: '/text/generate',
        baseURL: apiClient.defaults.baseURL,
        prompt,
        model: 'gemini-3-pro-preview',
      })
      
      const res = await apiClient.post('/text/generate', {
        prompt,
        model: 'gemini-3-pro-preview',
      })
      
      console.log('API Response:', res.data)
      setResponse(res.data.text)
    } catch (err: any) {
      console.error('API Error:', err)
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText,
        config: err.config,
      })
      
      let errorMessage = 'エラーが発生しました'
      if (err.response) {
        // サーバーからのエラーレスポンス
        errorMessage = err.response.data?.detail || err.response.data?.message || `サーバーエラー: ${err.response.status} ${err.response.statusText}`
      } else if (err.request) {
        // リクエストは送信されたが、レスポンスが受信されなかった
        errorMessage = 'サーバーに接続できませんでした。バックエンドが起動しているか確認してください。'
      } else {
        // リクエストの設定中にエラーが発生
        errorMessage = err.message || 'リクエストの送信に失敗しました'
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">テキスト生成</h2>
      <div className="mb-6">
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
          プロンプト
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="生成したいテキストのプロンプトを入力してください"
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
          <h3 className="text-lg font-semibold text-white mb-4">生成結果</h3>
          <div className="text-gray-300 whitespace-pre-wrap break-words max-h-[500px] overflow-y-auto">
            {response}
          </div>
        </div>
      )}
    </div>
  )
}

export default TextGeneration

