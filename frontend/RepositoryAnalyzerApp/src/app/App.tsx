import { Routes, Route, Outlet } from "react-router-dom";
import Welcome from "../pages/welcome";
import "../App.css";

function Shell() {
  return (
    <main className="container">
      <header>Repository Analyzer</header>
      <Outlet />
    </main>
  )
}


function App() {
  return (
    <Routes>
      <Route element = {<Shell />}>
        <Route path="/" element={<Welcome />} />
      </Route>
    </Routes>
  )
}

export default App;
