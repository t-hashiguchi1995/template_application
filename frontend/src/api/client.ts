import axios from 'axios'

// 環境変数からAPI URLを取得、なければデフォルト値を使用
const getBaseURL = () => {
  // Viteでは、環境変数はビルド時に静的に置き換えられる
  // import.meta.env.VITE_API_URLが未定義の場合は、デフォルト値を使用
  const envUrl = import.meta.env.VITE_API_URL
  
  // デバッグ用ログ
  console.log('Environment check:', {
    VITE_API_URL: envUrl,
    type: typeof envUrl,
    isUndefined: envUrl === undefined,
    isEmpty: envUrl === '',
    isTruthy: !!envUrl,
  })
  
  // ブラウザからアクセスする場合
  if (typeof window !== 'undefined') {
    // 環境変数が設定されている場合（undefinedでも空文字列でもない）
    if (envUrl && envUrl.trim() !== '') {
      const url = envUrl.endsWith('/api') ? envUrl : `${envUrl}/api`
      console.log('Using environment variable:', url)
      return url
    }
    // 環境変数が設定されていない場合は、デフォルトでバックエンドのURLを使用
    // vite previewではプロキシが動作しないため、直接バックエンドURLを指定
    const defaultUrl = 'http://localhost:8800/api'
    console.log('Using default URL:', defaultUrl)
    return defaultUrl
  }
  // SSR環境など、ブラウザ以外の場合は環境変数を使用
  if (envUrl && envUrl.trim() !== '') {
    return envUrl.endsWith('/api') ? envUrl : `${envUrl}/api`
  }
  return 'http://localhost:8800/api'
}

const apiClient = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60秒のタイムアウト
})

// リクエストインターセプター（デバッグ用）
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
    })
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// レスポンスインターセプター（デバッグ用）
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      data: response.data,
    })
    return response
  },
  (error) => {
    console.error('API Response Error:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
    })
    return Promise.reject(error)
  }
)

export default apiClient

