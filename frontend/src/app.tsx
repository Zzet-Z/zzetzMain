import { Route, Routes } from "react-router-dom";
import { HomePage } from "./routes/home-page";
import { SessionPage } from "./routes/session-page";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/session/:token" element={<SessionPage />} />
    </Routes>
  );
}
