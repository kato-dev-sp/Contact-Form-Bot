import React from 'react';
import MainPage from './MainPage';  // MainPage をインポート
import 'uikit/dist/css/uikit.min.css';  // UIKitのCSSをインポート

function App() {
    return (
        <div className="App">
            <MainPage />  {/* MainPageコンポーネントを表示 */}
        </div>
    );
}

export default App;
