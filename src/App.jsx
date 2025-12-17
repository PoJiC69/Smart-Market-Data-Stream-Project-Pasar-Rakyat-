import React from "react";
import Dashboard from "./views/Dashboard";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

export default function App() {
  return (
    <div className="app-root">
      <Sidebar />
      <div className="main">
        <Header />
        <main className="content">
          <Dashboard />
        </main>
      </div>
    </div>
  );
}