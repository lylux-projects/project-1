import React from "react";
import { Search, Bookmark } from "lucide-react";
import Logo from "./Logo";

const Navbar: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-100">
      <div className="container mx-auto px-4">
        <div className="py-6">
          <div className="flex justify-between items-center">
            <Logo />
            <nav className="hidden md:flex space-x-8">
              <NavItem text="PRODUCTS" isNew />
              <NavItem text="COLLECTIONS" />
              <NavItem text="FINISHES" />
              <NavItem text="PROJECTS" />
              <NavItem text="TECH HUB" />
              <NavItem text="ABOUT US" />
              <NavItem text="SUSTAINABILITY" />
              <NavItem text="CONTACT" />
            </nav>
            <div className="flex items-center space-x-4">
              <button className="bg-[#D4B88C] text-white px-6 py-2.5 text-sm font-medium rounded-full hover:bg-[#c4a77c] transition-colors">
                CONFIGURE PRODUCT
              </button>
              <button className="text-gray-600 hover:text-[#D4B88C] transition-colors">
                <Search size={20} />
              </button>
              <button className="text-gray-600 hover:text-[#D4B88C] transition-colors">
                <Bookmark size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="border-t border-gray-100">
        <div className="container mx-auto px-4">
          <div className="py-3">
            <nav className="flex items-center space-x-2 text-sm text-gray-500">
              <span>HOME</span>
              <span>&gt;</span>
              <span>ACCESSORIES</span>
              <span>&gt;</span>
              <span>ALL PRODUCTS</span>
              <span>&gt;</span>
              <span className="text-[#D4B88C] font-medium">CONFIGURE</span>
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
};

const NavItem: React.FC<{ text: string; isNew?: boolean }> = ({
  text,
  isNew,
}) => {
  return (
    <div className="relative group">
      <a
        href="#\"
        className="text-gray-800 text-sm hover:text-[#D4B88C] transition-colors"
      >
        {text}
      </a>
      {isNew && (
        <span className="absolute -top-2 -right-6 text-xs text-[#D4B88C]">
          NEW
        </span>
      )}
    </div>
  );
};

export default Navbar;
