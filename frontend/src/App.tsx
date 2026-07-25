import "./styles/app.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";

function App() {
  return (
    <div className="app">
      <Header />

      <div className="content">
        <Sidebar />
        <Chat />
      </div>
    </div>
  );
}

export default App;