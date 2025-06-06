// src/components/DetailedProductConfigurator.tsx
import React, { useState, useEffect } from "react";
import { ArrowLeft, Download, ShoppingCart, Save } from "lucide-react";
import { apiService, ProductDetails, UserConfiguration } from "../services/api";

interface DetailedProductConfiguratorProps {
  productId: number;
  onBack: () => void;
}

const DetailedProductConfigurator: React.FC<
  DetailedProductConfiguratorProps
> = ({ productId, onBack }) => {
  const [productDetails, setProductDetails] = useState<ProductDetails | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Configuration state
  const [selectedVariantId, setSelectedVariantId] = useState<number | null>(
    null
  );
  const [selectedOptions, setSelectedOptions] = useState<
    Record<string, number>
  >({});
  const [selectedAccessories, setSelectedAccessories] = useState<number[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [currentPartCode, setCurrentPartCode] = useState<string>("");

  useEffect(() => {
    loadProductDetails();
  }, [productId]);

  useEffect(() => {
    if (productDetails && selectedVariantId) {
      // Set default options
      const defaults: Record<string, number> = {};
      productDetails.configuration_categories.forEach((category) => {
        const defaultOption = category.options.find((opt) => opt.is_default);
        if (defaultOption) {
          defaults[category.category_name] = defaultOption.id;
        }
      });
      setSelectedOptions(defaults);
    }
  }, [productDetails, selectedVariantId]);

  useEffect(() => {
    if (selectedVariantId && Object.keys(selectedOptions).length > 0) {
      updatePriceAndPartCode();
    }
  }, [selectedVariantId, selectedOptions, selectedAccessories]);

  const loadProductDetails = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProductDetails(productId);
      setProductDetails(data);

      // Set default variant (first one)
      if (data.variants.length > 0) {
        setSelectedVariantId(data.variants[0].id);
      }
    } catch (err) {
      setError("Failed to load product details");
      console.error("Error loading product details:", err);
    } finally {
      setLoading(false);
    }
  };

  const updatePriceAndPartCode = () => {
    if (!productDetails || !selectedVariantId) return;

    const selectedVariant = productDetails.variants.find(
      (v) => v.id === selectedVariantId
    );
    if (!selectedVariant) return;

    let totalPrice = selectedVariant.base_price;
    let partCodeSuffix = "";

    // Add option prices and build part code
    Object.entries(selectedOptions).forEach(([categoryName, optionId]) => {
      const category = productDetails.configuration_categories.find(
        (cat) => cat.category_name === categoryName
      );
      const option = category?.options.find((opt) => opt.id === optionId);
      if (option) {
        totalPrice += option.price_modifier;
        if (option.part_code_suffix) {
          partCodeSuffix += `-${option.part_code_suffix}`;
        }
      }
    });

    setCurrentPrice(totalPrice);
    setCurrentPartCode(
      `${productDetails.product.base_part_code}${partCodeSuffix}`
    );
  };

  const generateDatasheetContent = () => {
    if (!productDetails || !selectedVariantId) return "";

    const selectedVariant = productDetails.variants.find(
      (v) => v.id === selectedVariantId
    );

    const selectedOptionsDetails = Object.entries(selectedOptions).map(
      ([categoryName, optionId]) => {
        const category = productDetails.configuration_categories.find(
          (cat) => cat.category_name === categoryName
        );
        const option = category?.options.find((opt) => opt.id === optionId);
        return {
          category: category?.category_label || categoryName,
          option: option?.option_label || "Unknown",
        };
      }
    );

    const selectedAccessoriesDetails = selectedAccessories
      .map((accId) => {
        const accessory = productDetails.accessories.find(
          (a) => a.id === accId
        );
        return accessory
          ? {
              id: accessory.id,
              name: accessory.name,
              description: accessory.description,
              part_code: accessory.part_code,
              price: accessory.price || 0,
              image_url: accessory.image_url || "", // INCLUDE THIS
              accessory_category: accessory.accessory_category || "",
            }
          : null;
      })
      .filter(Boolean);

    return `
PRODUCT DATASHEET
================

Product: ${productDetails.product.name}
Description: ${productDetails.product.description}
Part Code: ${currentPartCode}
Date: ${new Date().toLocaleDateString()}

SELECTED CONFIGURATION
=====================

Power Rating: ${selectedVariant?.variant_name || "Not selected"}
${selectedVariant ? `- System Output: ${selectedVariant.system_output}lm` : ""}
${selectedVariant ? `- System Power: ${selectedVariant.system_power}W` : ""}
${selectedVariant ? `- Efficiency: ${selectedVariant.efficiency}lm/W` : ""}
${
  selectedVariant
    ? `- Base Price: $${selectedVariant.base_price.toFixed(2)}`
    : ""
}

CONFIGURATION OPTIONS
====================
${selectedOptionsDetails
  .map((item) => `${item.category}: ${item.option}`)
  .join("\n")}

${
  selectedAccessoriesDetails.length > 0
    ? `
SELECTED ACCESSORIES
===================
${selectedAccessoriesDetails
  .map(
    (acc) =>
      `- ${acc.name} (${acc.partCode})
  Description: ${acc.description}`
  )
  .join("\n\n")}
`
    : ""
}

${
  productDetails.features.length > 0
    ? `
PRODUCT FEATURES
===============
${productDetails.features
  .map((feature) => `${feature.feature_label}: ${feature.feature_value}`)
  .join("\n")}
`
    : ""
}

PRICING SUMMARY
==============
Base Price: ${selectedVariant?.base_price.toFixed(2) || "0.00"}
Configuration Options: ${(
      currentPrice - (selectedVariant?.base_price || 0)
    ).toFixed(2)}
      
TOTAL PRICE: ${currentPrice.toFixed(2)}

---
Generated by Product Configurator
${new Date().toLocaleString()}
    `.trim();
  };

  const handleDownloadDatasheet = async () => {
    if (!productDetails || !selectedVariantId) {
      alert("Please select a product variant first");
      return;
    }

    try {
      // Find the selected variant
      const selectedVariant = productDetails.variants.find(
        (v) => v.id === selectedVariantId
      );

      if (!selectedVariant) {
        alert("Selected variant not found");
        return;
      }

      // Build selected options with full details for PDF
      const selectedOptionsWithDetails: Record<string, any> = {};
      Object.entries(selectedOptions).forEach(([categoryName, optionId]) => {
        const category = productDetails.configuration_categories.find(
          (cat) => cat.category_name === categoryName
        );
        const option = category?.options.find((opt) => opt.id === optionId);
        if (option && category) {
          selectedOptionsWithDetails[category.category_label] = {
            option_label: option.option_label,
            price_modifier: option.price_modifier,
            part_code_suffix: option.part_code_suffix || "",
          };
        }
      });

      // Get selected accessories details
      const selectedAccessoriesDetails = selectedAccessories
        .map((accId) => {
          const accessory = productDetails.accessories.find(
            (a) => a.id === accId
          );
          return accessory
            ? {
                id: accessory.id,
                name: accessory.name,
                description: accessory.description,
                part_code: accessory.part_code,
              }
            : null;
        })
        .filter(Boolean);

      // CRITICAL FIX: Include visual_assets and product in the PDF request
      const pdfRequest = {
        product_name: productDetails.product.name,
        base_part_code: productDetails.product.base_part_code,
        final_part_code: currentPartCode,
        variants: productDetails.variants.map((variant) => ({
          id: variant.id,
          variant_name: variant.variant_name,
          system_output: variant.system_output,
          system_power: variant.system_power,
          efficiency: variant.efficiency,
          base_price: variant.base_price,
          part_code_suffix: variant.part_code_suffix || "",
        })),
        selected_variant_id: selectedVariantId,
        selected_options: selectedOptionsWithDetails,
        accessories: selectedAccessoriesDetails,
        // CRITICAL: Include visual_assets and product data
        visual_assets: productDetails.visual_assets || {},
        product: productDetails.product || {},
      };

      // Enhanced debugging
      console.log("=== FRONTEND PDF REQUEST DEBUG ===");
      console.log("Full PDF request:", pdfRequest);
      console.log("Visual assets being sent:", pdfRequest.visual_assets);
      console.log(
        "Certifications being sent:",
        pdfRequest.visual_assets?.certifications
      );
      console.log(
        "Number of certifications:",
        pdfRequest.visual_assets?.certifications?.length || 0
      );

      // Log each certification
      if (pdfRequest.visual_assets?.certifications) {
        pdfRequest.visual_assets.certifications.forEach((cert, i) => {
          console.log(`Frontend cert ${i}:`, cert);
        });
      }

      // Call the backend PDF generation endpoint
      const response = await fetch(
        "http://localhost:8000/api/products/generate-datasheet",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(pdfRequest),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`
        );
      }

      // Get the PDF blob
      const pdfBlob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `${productDetails.product.name.replace(
          /[^a-zA-Z0-9]/g,
          "_"
        )}_datasheet.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      console.log("PDF download completed successfully");
    } catch (error) {
      console.error("Error generating PDF datasheet:", error);
      alert(`Failed to generate PDF datasheet: ${error.message}`);
    }
  };

  const handleOptionChange = (categoryName: string, optionId: number) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [categoryName]: optionId,
    }));
  };

  const handleAccessoryToggle = (accessoryId: number) => {
    setSelectedAccessories((prev) =>
      prev.includes(accessoryId)
        ? prev.filter((id) => id !== accessoryId)
        : [...prev, accessoryId]
    );
  };

  const handleSaveConfiguration = async () => {
    if (!selectedVariantId) return;

    const configuration: UserConfiguration = {
      product_id: productId,
      variant_id: selectedVariantId,
      selected_options: selectedOptions,
      selected_accessories: selectedAccessories,
      configuration_name: `${productDetails?.product.name} Configuration`,
    };

    try {
      await apiService.saveConfiguration(configuration);
      alert("Configuration saved successfully!");
    } catch (err) {
      console.error("Error saving configuration:", err);
      alert("Failed to save configuration");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-xl text-gray-600">Loading product details...</div>
      </div>
    );
  }

  if (error || !productDetails) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">
            {error || "Product not found"}
          </div>
          <button
            onClick={onBack}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to Product Types
          </button>
        </div>
      </div>
    );
  }

  const selectedVariant = productDetails.variants.find(
    (v) => v.id === selectedVariantId
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={onBack}
            className="flex items-center text-[#D4B88C] hover:text-[#B8966F] mb-4 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Product Types
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-light text-gray-900 mb-2">
                {productDetails.product.name}
              </h1>
              <p className="text-gray-600 max-w-2xl">
                {productDetails.product.description}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-1">Part Code</div>
              <div className="font-mono text-lg font-medium text-gray-900 bg-gray-100 px-3 py-1 rounded">
                {currentPartCode || "Select options..."}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-3 space-y-6">
            {/* Power Rating Selection */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-xl font-medium text-gray-900 mb-6">
                Select Power Rating
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {productDetails.variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariantId(variant.id)}
                    className={`p-6 border-2 rounded-lg text-center transition-all ${
                      selectedVariantId === variant.id
                        ? "border-[#D4B88C] bg-[#D4B88C]/10"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="text-lg font-semibold text-gray-900">
                      {variant.variant_name}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {variant.system_output}lm | {variant.system_power}W
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      Efficiency: {variant.efficiency}lm/W
                    </div>
                    <div className="text-lg font-semibold text-[#D4B88C] mt-2">
                      ${variant.base_price.toFixed(2)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Configuration Options */}
            {productDetails.configuration_categories.map((category) => (
              <div
                key={category.id}
                className="bg-white rounded-lg shadow-sm border p-6"
              >
                <h3 className="text-xl font-medium text-gray-900 mb-6">
                  {category.category_label}
                  {category.is_required && (
                    <span className="text-red-500 ml-1">*</span>
                  )}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {category.options.map((option) => (
                    <button
                      key={option.id}
                      onClick={() =>
                        handleOptionChange(category.category_name, option.id)
                      }
                      className={`p-4 border-2 rounded-lg text-center transition-all ${
                        selectedOptions[category.category_name] === option.id
                          ? "border-[#D4B88C] bg-[#D4B88C]/10"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="font-medium text-gray-900">
                        {option.option_label}
                      </div>
                      {option.price_modifier !== 0 && (
                        <div className="text-sm text-[#D4B88C] font-medium mt-1">
                          {option.price_modifier > 0 ? "+" : ""}$
                          {option.price_modifier.toFixed(2)}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* Accessories */}
            {productDetails.accessories.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-xl font-medium text-gray-900 mb-6">
                  Optional Accessories
                </h3>
                <div className="space-y-4">
                  {productDetails.accessories.map((accessory) => (
                    <label
                      key={accessory.id}
                      className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedAccessories.includes(accessory.id)}
                        onChange={() => handleAccessoryToggle(accessory.id)}
                        className="h-5 w-5 text-[#D4B88C] rounded focus:ring-[#D4B88C]"
                      />

                      {/* Add accessory image */}
                      {accessory.image_url && (
                        <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center">
                          <img
                            src={accessory.image_url}
                            alt={accessory.name}
                            className="max-w-full max-h-full object-contain"
                            onError={(e) => {
                              // Hide image if it fails to load
                              e.currentTarget.style.display = "none";
                            }}
                          />
                        </div>
                      )}

                      <div className="flex-1">
                        <div className="font-medium text-gray-900">
                          {accessory.name}
                        </div>
                        <div className="text-sm text-gray-600">
                          {accessory.description}
                        </div>
                        <div className="text-sm text-gray-500 mt-1">
                          Part: {accessory.part_code}
                        </div>
                        {accessory.price && (
                          <div className="text-sm text-[#D4B88C] font-medium">
                            ${accessory.price.toFixed(2)}
                          </div>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Product Features */}
            {productDetails.features.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-xl font-medium text-gray-900 mb-6">
                  Product Features
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {productDetails.features.map((feature) => (
                    <div
                      key={feature.id}
                      className="flex justify-between py-2 border-b border-gray-100 last:border-b-0"
                    >
                      <span className="text-gray-600">
                        {feature.feature_label}:
                      </span>
                      <span className="font-medium text-gray-900">
                        {feature.feature_value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Summary Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-8">
              <h3 className="text-xl font-medium text-gray-900 mb-6">
                Configuration Summary
              </h3>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Product:</span>
                  <span className="font-medium text-gray-900">
                    {productDetails.product.name}
                  </span>
                </div>

                {selectedVariant && (
                  <div className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-600">Power:</span>
                    <span className="font-medium text-gray-900">
                      {selectedVariant.variant_name}
                    </span>
                  </div>
                )}

                {Object.entries(selectedOptions).map(
                  ([categoryName, optionId]) => {
                    const category =
                      productDetails.configuration_categories.find(
                        (cat) => cat.category_name === categoryName
                      );
                    const option = category?.options.find(
                      (opt) => opt.id === optionId
                    );

                    if (!option) return null;

                    return (
                      <div
                        key={categoryName}
                        className="flex justify-between py-2 border-b border-gray-100"
                      >
                        <span className="text-gray-600">
                          {category?.category_label}:
                        </span>
                        <span className="font-medium text-gray-900">
                          {option.option_label}
                        </span>
                      </div>
                    );
                  }
                )}

                {selectedAccessories.length > 0 && (
                  <div className="pt-2">
                    <div className="text-sm font-medium text-gray-900 mb-2">
                      Accessories:
                    </div>
                    {selectedAccessories.map((accId) => {
                      const acc = productDetails.accessories.find(
                        (a) => a.id === accId
                      );
                      return acc ? (
                        <div key={accId} className="py-1">
                          <span className="text-sm text-gray-600">
                            {acc.name}
                          </span>
                        </div>
                      ) : null;
                    })}
                  </div>
                )}
              </div>

              <div className="border-t pt-6 mb-6">
                <div className="flex justify-between text-2xl font-bold">
                  <span className="text-gray-900">Total:</span>
                  <span className="text-[#D4B88C]">
                    ${currentPrice.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleSaveConfiguration}
                  className="w-full bg-[#D4B88C] text-white py-3 px-4 rounded-lg hover:bg-[#B8966F] transition-colors flex items-center justify-center"
                >
                  <Save size={18} className="mr-2" />
                  Save Configuration
                </button>
                <button className="w-full border-2 border-[#D4B88C] text-[#D4B88C] py-3 px-4 rounded-lg hover:bg-[#D4B88C] hover:text-white transition-colors flex items-center justify-center">
                  <ShoppingCart size={18} className="mr-2" />
                  Request Quote
                </button>
                <button
                  onClick={handleDownloadDatasheet}
                  className="w-full border border-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center"
                >
                  <Download size={18} className="mr-2" />
                  Download Datasheet
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailedProductConfigurator;
