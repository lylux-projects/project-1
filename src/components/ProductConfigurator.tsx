import React from "react";
import ProductTypeCard from "./ProductTypeCard";
import { Info } from "lucide-react";

// Import your local images
import DownlightImg from "../images/Downlight.png";
import UplightImg from "../images/Uplight.png";
import WallLightImg from "../images/Wall Light.png";
import ProjectorImg from "../images/Projector.png";
import ExteriorImg from "../images/ExteriorORHarshEnvironment.png";
import FacadeLightingImg from "../images/FacadeLighting.png";
import TrackImg from "../images/Track.png";

const productTypes = [
  {
    type: "DOWNLIGHT",
    imageUrl: DownlightImg,
  },
  {
    type: "UPLIGHT",
    imageUrl: UplightImg,
  },
  {
    type: "WALL LIGHT",
    imageUrl: WallLightImg,
  },
  {
    type: "PROJECTOR",
    imageUrl: ProjectorImg,
  },
  {
    type: "EXTERIOR / HARSH ENVIRONMENT",
    imageUrl: ExteriorImg,
  },
  {
    type: "FACADE LIGHTING",
    imageUrl: FacadeLightingImg,
  },
  {
    type: "TRACK",
    imageUrl: TrackImg,
  },
];

const ProductConfigurator: React.FC = () => {
  return (
    <div className="bg-white py-16">
      <div className="container mx-auto px-4">
        <div className="mb-12 flex items-center justify-center">
          <h1 className="text-4xl font-light tracking-wide text-center text-gray-900">
            SELECT PRODUCT TYPE
          </h1>
          <Info size={20} className="ml-2 text-[#D4B88C]" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {productTypes.slice(0, 4).map((product, index) => (
            <ProductTypeCard
              key={index}
              type={product.type}
              imageUrl={product.imageUrl}
            />
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-8">
          {productTypes.slice(4).map((product, index) => (
            <ProductTypeCard
              key={index + 4}
              type={product.type}
              imageUrl={product.imageUrl}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProductConfigurator;
