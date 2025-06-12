// src/components/ProductConfigurator.tsx
import React, { useState, useEffect } from "react";
import ProductTypeCard from "./ProductTypeCard";
import { Info } from "lucide-react";
import { apiService, Category } from "../services/api";

// Import your local images
import DownlightImg from "../images/Downlight.png";
import UplightImg from "../images/Uplight.png";
import WallLightImg from "../images/Wall Light.png";
import ProjectorImg from "../images/Projector.png";
import ExteriorImg from "../images/ExteriorORHarshEnvironment.png";
import FacadeLightingImg from "../images/FacadeLighting.png";
import TrackImg from "../images/Track.png";

interface ProductConfiguratorProps {
  onSelectCategory?: (categorySlug: string) => void;
}

const ProductConfigurator: React.FC<ProductConfiguratorProps> = ({
  onSelectCategory,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Map category slugs to your existing images
  const getImageForCategory = (slug: string): string => {
    const imageMap: Record<string, string> = {
      downlight: DownlightImg,
      uplight: UplightImg,
      "wall-light": WallLightImg,
      projector: ProjectorImg,
      "exterior-harsh": ExteriorImg,
      "facade-lighting": FacadeLightingImg,
      track: TrackImg,
    };
    return imageMap[slug] || DownlightImg; // Default fallback
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCategories();
      setCategories(data);
      setError(null);
    } catch (err) {
      console.error("Error loading categories:", err);
      setError("Failed to load product categories");
      // Fallback to static data if API fails
      setCategories([
        {
          id: 1,
          name: "DOWNLIGHT",
          slug: "downlight",
          description: "",
          display_order: 1,
        },
        {
          id: 2,
          name: "UPLIGHT",
          slug: "uplight",
          description: "",
          display_order: 2,
        },
        {
          id: 3,
          name: "WALL LIGHT",
          slug: "wall-light",
          description: "",
          display_order: 3,
        },
        {
          id: 4,
          name: "PROJECTOR",
          slug: "projector",
          description: "",
          display_order: 4,
        },
        {
          id: 5,
          name: "EXTERIOR / HARSH ENVIRONMENT",
          slug: "exterior-harsh",
          description: "",
          display_order: 5,
        },
        {
          id: 6,
          name: "FACADE LIGHTING",
          slug: "facade-lighting",
          description: "",
          display_order: 6,
        },
        {
          id: 7,
          name: "TRACK",
          slug: "track",
          description: "",
          display_order: 7,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (category: Category) => {
    if (onSelectCategory) {
      onSelectCategory(category.slug);
    } else {
      // Default behavior - could navigate to a new page or show products
      console.log("Selected category:", category.name);
      // You can add navigation logic here
    }
  };

  if (loading) {
    return (
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="text-xl text-gray-600">
              Loading product types...
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white py-16">
      <div className="container mx-auto px-4">
        <div className="mb-12 flex items-center justify-center">
          <h1 className="text-4xl font-light tracking-wide text-center text-gray-900">
            SELECT PRODUCT TYPE
          </h1>
          <Info size={20} className="ml-2 text-[#D4B88C]" />
        </div>

        {error && (
          <div className="mb-8 text-center">
            <div className="text-red-500 text-sm">
              {error} - Using offline data
            </div>
          </div>
        )}

        {/* First row - 4 items */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {categories.slice(0, 4).map((category) => (
            <ProductTypeCard
              key={category.id}
              type={category.name}
              imageUrl={getImageForCategory(category.slug)}
              onClick={() => handleCategoryClick(category)}
            />
          ))}
        </div>

        {/* Second row - remaining items */}
        {categories.length > 4 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-8">
            {categories.slice(4).map((category) => (
              <ProductTypeCard
                key={category.id}
                type={category.name}
                imageUrl={getImageForCategory(category.slug)}
                onClick={() => handleCategoryClick(category)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductConfigurator;
