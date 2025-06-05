import React from "react";

interface ProductTypeCardProps {
  type: string;
  imageUrl: string;
}

const ProductTypeCard: React.FC<ProductTypeCardProps> = ({
  type,
  imageUrl,
}) => {
  return (
    <div className="bg-white rounded-xl overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-gray-100 group">
      <div className="p-8 flex items-center justify-center h-48 bg-gray-50 group-hover:bg-gray-100 transition-colors">
        <img
          src={imageUrl}
          alt={type}
          className="max-h-full max-w-full object-contain"
        />
      </div>
      <div className="text-center py-4 border-t border-gray-100">
        <h3 className="text-[#D4B88C] text-sm tracking-wider font-medium">
          {type}
        </h3>
      </div>
    </div>
  );
};

export default ProductTypeCard;
