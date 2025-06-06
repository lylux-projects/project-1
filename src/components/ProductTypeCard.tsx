// src/components/ProductTypeCard.tsx
import React from "react";

interface ProductTypeCardProps {
  type: string;
  imageUrl: string;
  onClick?: () => void;
}

const ProductTypeCard: React.FC<ProductTypeCardProps> = ({
  type,
  imageUrl,
  onClick,
}) => {
  return (
    <div
      className="group cursor-pointer transition-all duration-300 hover:transform hover:scale-105"
      onClick={onClick}
    >
      <div className="bg-gray-50 rounded-lg p-8 mb-4 group-hover:bg-gray-100 transition-colors">
        <div className="flex justify-center items-center h-48">
          <img
            src={imageUrl}
            alt={type}
            className="max-h-full max-w-full object-contain"
          />
        </div>
      </div>
      <h3 className="text-lg font-medium text-gray-900 uppercase tracking-wide text-center">
        {type}
      </h3>
    </div>
  );
};

export default ProductTypeCard;
