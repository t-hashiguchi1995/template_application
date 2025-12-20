import { useState } from 'react'
import apiClient from '../api/client'

function DocumentAnalysis() {
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    if (!file) {
      setError('ファイルを選択してください')
      return
    }

    setLoading(true)
    setError('')
    setResponse('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('prompt', prompt || 'このドキュメントの内容を要約してください')

      const res = await apiClient.post('/document/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setResponse(res.data.analysis)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-8 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">ドキュメント分析</h2>
      <div className="mb-6">
        <label htmlFor="file" className="block text-sm font-medium text-gray-300 mb-2">
          ファイル（PDF、DOCX、TXT等）
        </label>
        <input
          id="file"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-gray-800 file:text-white hover:file:bg-gray-700 cursor-pointer"
        />
      </div>
      <div className="mb-6">
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-300 mb-2">
          プロンプト（オプション）
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例: このドキュメントの要点を3つ挙げてください"
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[120px]"
        />
      </div>
      <button
        onClick={handleAnalyze}
        disabled={loading || !file}
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed disabled:text-gray-400 transition-colors duration-200"
      >
        {loading ? '分析中...' : '分析'}
      </button>

      {error && (
        <div className="mt-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {response && (
        <div className="mt-6 p-6 bg-gray-800 border border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-4">分析結果</h3>
          <div className="text-gray-300 whitespace-pre-wrap break-words max-h-[500px] overflow-y-auto">
            {response}
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentAnalysis

