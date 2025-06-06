// src/App.tsx
import React, { useState, useEffect } from "react";
import ProductConfigurator from "./components/ProductConfigurator";
import DetailedProductConfigurator from "./components/DetailedProductConfigurator";
import Navbar from "./components/Navbar"; // Import the proper Navbar
import Footer from "./components/Footer"; // Import Footer for consistency
import { apiService, Product } from "./services/api";

type AppState = "category-selection" | "product-list" | "product-config";

const App: React.FC = () => {
  const [currentState, setCurrentState] =
    useState<AppState>("category-selection");
  const [selectedCategorySlug, setSelectedCategorySlug] = useState<
    string | null
  >(null);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(
    null
  );
  const [categoryProducts, setCategoryProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCategorySelect = async (categorySlug: string) => {
    try {
      setLoading(true);
      setError(null);
      setSelectedCategorySlug(categorySlug);

      // Load products for this category
      const products = await apiService.getProductsByCategory(categorySlug);
      setCategoryProducts(products);

      // If only one product, go directly to configuration
      if (products.length === 1) {
        setSelectedProductId(products[0].id);
        setCurrentState("product-config");
      } else if (products.length > 1) {
        setCurrentState("product-list");
      } else {
        // No products found - show message
        setError(`No products found for ${categorySlug}`);
      }
    } catch (error) {
      console.error("Error loading category products:", error);
      setError("Failed to load products for this category");
    } finally {
      setLoading(false);
    }
  };

  const handleProductSelect = (productId: number) => {
    setSelectedProductId(productId);
    setCurrentState("product-config");
  };

  const handleBackToCategories = () => {
    setCurrentState("category-selection");
    setSelectedCategorySlug(null);
    setSelectedProductId(null);
    setCategoryProducts([]);
    setError(null);
  };

  const handleBackToProducts = () => {
    setCurrentState("product-list");
    setSelectedProductId(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#D4B88C] mx-auto mb-4"></div>
          <div className="text-xl text-gray-600">Loading...</div>
        </div>
      </div>
    );
  }

  // Category Selection View
  if (currentState === "category-selection") {
    return (
      <div className="min-h-screen bg-white">
        {/* Use your proper Navbar component */}
        <Navbar />

        {/* Error Display */}
        {error && (
          <div className="container mx-auto px-4 mb-6">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="text-red-800">{error}</div>
            </div>
          </div>
        )}

        {/* Product Configurator */}
        <ProductConfigurator onSelectCategory={handleCategorySelect} />

        {/* Footer */}
        <Footer />
      </div>
    );
  }

  // Product List View (for categories with multiple products)
  if (currentState === "product-list") {
    return (
      <div className="min-h-screen bg-white">
        {/* Use your proper Navbar component */}
        <Navbar />

        {/* Main Content */}
        <div className="container mx-auto px-4 py-8">
          <button
            onClick={handleBackToCategories}
            className="text-[#D4B88C] hover:text-[#B8966F] mb-6 transition-colors"
          >
            ← Back to Categories
          </button>

          <h1 className="text-3xl font-light text-gray-900 mb-2">
            Select {selectedCategorySlug?.replace("-", " ").toUpperCase()}{" "}
            Product
          </h1>
          <p className="text-gray-600 mb-8">
            Choose a specific product to configure
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {categoryProducts.map((product) => (
              <div
                key={product.id}
                className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer group"
                onClick={() => handleProductSelect(product.id)}
              >
                <div className="p-6">
                  {product.product_image_url && (
                    <div className="h-48 mb-4 bg-gray-50 rounded flex items-center justify-center">
                      <img
                        src={product.product_image_url}
                        alt={product.name}
                        className="max-h-full max-w-full object-contain"
                      />
                    </div>
                  )}
                  <h3 className="text-lg font-medium text-gray-900 mb-2 group-hover:text-[#D4B88C] transition-colors">
                    {product.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {product.description}
                  </p>
                  <div className="text-sm text-gray-500">
                    Part Code: {product.base_part_code}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <Footer />
      </div>
    );
  }

  // Product Configuration View
  if (currentState === "product-config" && selectedProductId) {
    return (
      <DetailedProductConfigurator
        productId={selectedProductId}
        onBack={
          categoryProducts.length > 1
            ? handleBackToProducts
            : handleBackToCategories
        }
      />
    );
  }

  // Fallback
  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-center">
      <div className="text-center">
        <div className="text-xl text-gray-600 mb-4">Something went wrong</div>
        <button
          onClick={handleBackToCategories}
          className="text-[#D4B88C] hover:text-[#B8966F]"
        >
          Return to Categories
        </button>
      </div>
    </div>
  );
};

export default App;
