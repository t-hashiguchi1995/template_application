import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import TextGeneration from './pages/TextGeneration'
import ImageGeneration from './pages/ImageGeneration'
import VideoGeneration from './pages/VideoGeneration'
import AudioGeneration from './pages/AudioGeneration'
import Embedding from './pages/Embedding'
import FunctionCalling from './pages/FunctionCalling'
import StructuredOutput from './pages/StructuredOutput'
import DocumentAnalysis from './pages/DocumentAnalysis'
import Agent from './pages/Agent'

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const location = useLocation()
  const isActive = location.pathname === to || (to === '/text' && location.pathname === '/')
  
  return (
    <Link
      to={to}
      className={`
        px-4 py-2 rounded-lg transition-colors duration-200
        ${isActive 
          ? 'bg-gray-800 text-white font-medium' 
          : 'text-gray-400 hover:text-white hover:bg-gray-800'
        }
      `}
    >
      {children}
    </Link>
  )
}

function App() {
  return (
    <Router>
      <div className="flex flex-col h-screen bg-gray-950">
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4">
          <h1 className="text-2xl font-bold text-white mb-4">Gemini API Demo</h1>
          <ul className="flex flex-wrap gap-2">
            <li><NavLink to="/text">テキスト生成</NavLink></li>
            <li><NavLink to="/image">画像生成</NavLink></li>
            <li><NavLink to="/video">動画生成</NavLink></li>
            <li><NavLink to="/audio">音声</NavLink></li>
            <li><NavLink to="/embedding">エンベディング</NavLink></li>
            <li><NavLink to="/function-calling">関数呼び出し</NavLink></li>
            <li><NavLink to="/structured-output">構造化出力</NavLink></li>
            <li><NavLink to="/document">ドキュメント分析</NavLink></li>
            <li><NavLink to="/agent">エージェント</NavLink></li>
          </ul>
        </nav>
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<TextGeneration />} />
              <Route path="/text" element={<TextGeneration />} />
              <Route path="/image" element={<ImageGeneration />} />
              <Route path="/video" element={<VideoGeneration />} />
              <Route path="/audio" element={<AudioGeneration />} />
              <Route path="/embedding" element={<Embedding />} />
              <Route path="/function-calling" element={<FunctionCalling />} />
              <Route path="/structured-output" element={<StructuredOutput />} />
              <Route path="/document" element={<DocumentAnalysis />} />
              <Route path="/agent" element={<Agent />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App

