import { Routes, Route } from 'react-router';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<div>Login placeholder</div>} />
      <Route path="/*" element={<div>App placeholder</div>} />
    </Routes>
  );
}
