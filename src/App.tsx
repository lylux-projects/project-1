import React from "react";
import Navbar from "./components/Navbar";
import ProductConfigurator from "./components/ProductConfigurator";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <ProductConfigurator />
      <Footer />
    </div>
  );
}

export default App;
