import React from "react";
import Logo from "./Logo";

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 pt-16 pb-8 border-t border-gray-100">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div>
            <Logo />
            <p className="text-sm text-gray-600 mt-4">
              Unit 2, the Center, Heart's Way,
              <br />
              Leeds, LS10 1EW, UK
            </p>
          </div>

          <div>
            <h3 className="text-[#D4B88C] text-sm font-medium mb-4">
              PRODUCTS
            </h3>
            <ul className="text-sm text-gray-600 space-y-3">
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Downlights
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Uplights
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Wall Lights
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Projectors
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-[#D4B88C] text-sm font-medium mb-4">
              TERMS & CONDITIONS
            </h3>
            <ul className="text-sm text-gray-600 space-y-3">
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Terms of Use
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Warranty
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-[#D4B88C] transition-colors">
                  Returns
                </a>
              </li>
            </ul>
          </div>

          <div className="flex space-x-4">
            <img
              src="https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
              alt="Certification"
              className="h-16 w-16 object-contain bg-white p-2 rounded-lg shadow-sm"
            />
            <img
              src="https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
              alt="Certification"
              className="h-16 w-16 object-contain bg-white p-2 rounded-lg shadow-sm"
            />
            <img
              src="https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
              alt="Certification"
              className="h-16 w-16 object-contain bg-white p-2 rounded-lg shadow-sm"
            />
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200 text-xs text-gray-500">
          <p>© 2025 Lylux. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
