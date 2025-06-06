// src/components/ProductTypeSelector.tsx
import React, { useState, useEffect } from "react";
import { apiService, Category } from "../services/api";
import Navbar from "./Navbar"; // Import your existing Navbar component

interface ProductTypeSelectorProps {
  onSelectCategory: (categorySlug: string) => void;
}

const ProductTypeSelector: React.FC<ProductTypeSelectorProps> = ({
  onSelectCategory,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCategories();
      setCategories(data);
    } catch (err) {
      setError("Failed to load product categories");
      console.error("Error loading categories:", err);
    } finally {
      setLoading(false);
    }
  };

  // Map category slugs to your existing icons
  const getCategoryIcon = (slug: string) => {
    const iconMap: Record<string, string> = {
      downlight: "🔽", // Replace with your actual icon components
      uplight: "🔼",
      "wall-light": "📍",
      projector: "📽️",
      "exterior-harsh": "🌦️",
      "facade-lighting": "🏢",
      track: "🚂",
    };
    return iconMap[slug] || "💡";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Navbar />
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="text-xl">Loading product types...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white">
        <Navbar />
        <div className="flex justify-center items-center min-h-[60vh]">
          <div className="text-red-500 text-xl">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Use your existing Navbar component */}
      <Navbar />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-light text-gray-900 mb-4">
            SELECT PRODUCT TYPE
          </h2>
        </div>

        {/* Product Type Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {categories.slice(0, 4).map((category) => (
            <div
              key={category.id}
              className="text-center cursor-pointer group hover:transform hover:scale-105 transition-all duration-300"
              onClick={() => onSelectCategory(category.slug)}
            >
              <div className="bg-gray-50 rounded-lg p-8 mb-4 group-hover:bg-gray-100 transition-colors">
                <div className="text-6xl mb-4">
                  {getCategoryIcon(category.slug)}
                </div>
              </div>
              <h3 className="text-lg font-medium text-gray-900 uppercase tracking-wide">
                {category.name}
              </h3>
              {category.description && (
                <p className="text-sm text-gray-600 mt-2">
                  {category.description}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Bottom Navigation Row - Only if there are more than 4 categories */}
        {categories.length > 4 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {categories.slice(4).map((category) => (
              <div
                key={category.id}
                className="text-center cursor-pointer group hover:transform hover:scale-105 transition-all duration-300"
                onClick={() => onSelectCategory(category.slug)}
              >
                <div className="bg-gray-50 rounded-lg p-8 mb-4 group-hover:bg-gray-100 transition-colors">
                  <div className="text-6xl mb-4">
                    {getCategoryIcon(category.slug)}
                  </div>
                </div>
                <h3 className="text-lg font-medium text-gray-900 uppercase tracking-wide">
                  {category.name}
                </h3>
                {category.description && (
                  <p className="text-sm text-gray-600 mt-2">
                    {category.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductTypeSelector;
