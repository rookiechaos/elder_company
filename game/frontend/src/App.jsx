import { useState } from 'react'
import './App.css'

function App() {
  const [selectedGame, setSelectedGame] = useState(null)

  const games = [
    {
      id: 'memory',
      name: '记忆配对',
      description: '翻牌配对游戏，训练记忆力和注意力',
      icon: '🧠'
    },
    {
      id: 'story',
      name: '故事接龙',
      description: '轮流添加句子，共同创作故事',
      icon: '📖'
    },
    {
      id: 'number',
      name: '数字拼图',
      description: '数字排序和计算游戏',
      icon: '🔢'
    },
    {
      id: 'music',
      name: '音乐节奏',
      description: '跟随音乐节奏点击屏幕',
      icon: '🎵'
    },
    {
      id: 'picture',
      name: '图片分类',
      description: '将图片按照类别分类',
      icon: '🖼️'
    }
  ]

  return (
    <div className="app">
      <header className="app-header">
        <h1>Elder Company 协同游戏</h1>
        <p>老人和看护者一起玩的移动端小游戏</p>
      </header>

      <main className="game-list">
        {games.map(game => (
          <div
            key={game.id}
            className="game-card"
            onClick={() => setSelectedGame(game.id)}
          >
            <div className="game-icon">{game.icon}</div>
            <h2>{game.name}</h2>
            <p>{game.description}</p>
          </div>
        ))}
      </main>

      {selectedGame && (
        <div className="game-placeholder">
          <p>游戏 "{games.find(g => g.id === selectedGame)?.name}" 开发中...</p>
          <button onClick={() => setSelectedGame(null)}>返回</button>
        </div>
      )}

      <footer className="app-footer">
        <p>版本 1.0.0 | Elder Company 2026</p>
      </footer>
    </div>
  )
}

export default App
