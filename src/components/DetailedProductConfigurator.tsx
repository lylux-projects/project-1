import React, { useState, useEffect } from "react";
import {
  ArrowLeft,
  Download,
  ShoppingCart,
  Save,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader,
} from "lucide-react";

// REAL API service - Replace YOUR_BACKEND_URL with your actual backend URL
const API_BASE_URL = "http://localhost:8000/api/products"; // Change this to your backend URL

const apiService = {
  getProductDetails: async (productId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/product-details/${productId}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching product details:", error);
      throw error;
    }
  },

  saveConfiguration: async (config) => {
    try {
      const response = await fetch(`${API_BASE_URL}/configure/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error saving configuration:", error);
      throw error;
    }
  },
};

const EnhancedProductConfigurator = ({ productId = 1, onBack = () => {} }) => {
  const [productDetails, setProductDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pdfGenerating, setPdfGenerating] = useState(false);
  const [pdfStatus, setPdfStatus] = useState(null);

  // Configuration state
  const [selectedVariantId, setSelectedVariantId] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState({});
  const [selectedAccessories, setSelectedAccessories] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [currentPartCode, setCurrentPartCode] = useState("");

  useEffect(() => {
    loadProductDetails();
  }, [productId]);

  useEffect(() => {
    if (productDetails && selectedVariantId) {
      const defaults = {};
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
      setError(null);
      console.log(`Loading product details for product ID: ${productId}`);

      const data = await apiService.getProductDetails(productId);
      console.log("Product details loaded:", data);

      setProductDetails(data);

      if (data.variants && data.variants.length > 0) {
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
    let partCodeParts = [
      productDetails.product.base_part_code,
      selectedVariant.part_code_suffix,
    ];

    // Add option prices and build part code
    Object.entries(selectedOptions).forEach(([categoryName, optionId]) => {
      const category = productDetails.configuration_categories.find(
        (cat) => cat.category_name === categoryName
      );
      const option = category?.options.find((opt) => opt.id === optionId);
      if (option) {
        totalPrice += option.price_modifier;
        if (option.part_code_suffix) {
          partCodeParts.push(option.part_code_suffix);
        }
      }
    });

    // Add accessory prices
    selectedAccessories.forEach((accId) => {
      const accessory = productDetails.accessories.find((a) => a.id === accId);
      if (accessory && accessory.price) {
        totalPrice += accessory.price;
      }
    });

    setCurrentPrice(totalPrice);
    setCurrentPartCode(partCodeParts.join("-"));
  };

  const handleDownloadDatasheet = async () => {
    if (!productDetails || !selectedVariantId) {
      setPdfStatus({
        type: "error",
        message: "Please select a product variant first",
      });
      return;
    }

    try {
      setPdfGenerating(true);
      setPdfStatus({
        type: "info",
        message: "Generating professional datasheet...",
      });

      const selectedVariant = productDetails.variants.find(
        (v) => v.id === selectedVariantId
      );

      if (!selectedVariant) {
        throw new Error("Selected variant not found");
      }

      // Build selected options with full details for PDF
      const selectedOptionsWithDetails = {};
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
                image_url: accessory.image_url || "",
                price: accessory.price || 0,
              }
            : null;
        })
        .filter(Boolean);

      // Build professional PDF request
      const pdfRequest = {
        product_name: productDetails.product.name,
        base_part_code: productDetails.product.base_part_code,
        final_part_code: currentPartCode,

        // Convert variants to match backend model
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

        // Handle visual assets - check different possible structures
        visual_assets: {
          certifications: (
            productDetails.visual_assets?.certifications ||
            productDetails.visual_assets?.all_assets?.filter(
              (asset) => asset.asset_type === "certification"
            ) ||
            []
          ).map((cert) => ({
            file_name: cert.file_name || cert.name || "certificate",
            file_url: cert.file_url || cert.url || "",
          })),
        },

        // Convert product to match backend model
        product: {
          name: productDetails.product.name || "",
          description: productDetails.product.description || "",
          base_part_code: productDetails.product.base_part_code || "",
          product_image_url: productDetails.product.product_image_url || "",
          dimension_image_url: productDetails.product.dimension_image_url || "",
        },
      };

      // Enhanced debugging
      console.log("=== REAL FRONTEND DEBUG ===");
      console.log("API Base URL:", API_BASE_URL);
      console.log(
        "PDF Request URL:",
        `${API_BASE_URL}/generate-professional-datasheet`
      );
      console.log("Full PDF request:", JSON.stringify(pdfRequest, null, 2));
      console.log("Visual assets being sent:", pdfRequest.visual_assets);
      console.log(
        "Certifications being sent:",
        pdfRequest.visual_assets.certifications
      );
      console.log(
        "Number of certifications:",
        pdfRequest.visual_assets.certifications?.length || 0
      );

      // Call the REAL backend endpoint
      const response = await fetch(`${API_BASE_URL}/generate-datasheet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(pdfRequest),
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(
          `HTTP error! status: ${response.status}, message: ${errorText}`
        );
      }

      // Check if response is actually a PDF
      const contentType = response.headers.get("content-type");
      console.log("Response content type:", contentType);

      if (!contentType || !contentType.includes("application/pdf")) {
        const responseText = await response.text();
        console.error("Expected PDF but got:", responseText);
        throw new Error("Server did not return a PDF file");
      }

      // Get the PDF blob
      const pdfBlob = await response.blob();
      console.log("PDF blob size:", pdfBlob.size);

      if (pdfBlob.size === 0) {
        throw new Error("Received empty PDF file");
      }

      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `${productDetails.product.name.replace(
          /[^a-zA-Z0-9]/g,
          "_"
        )}_professional_datasheet.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setPdfStatus({
        type: "success",
        message: "Professional datasheet generated successfully!",
      });

      console.log("PDF download completed successfully");
    } catch (error) {
      console.error("Error generating PDF datasheet:", error);
      setPdfStatus({
        type: "error",
        message: `Failed to generate datasheet: ${error.message}`,
      });
    } finally {
      setPdfGenerating(false);
      setTimeout(() => setPdfStatus(null), 5000);
    }
  };

  const handleOptionChange = (categoryName, optionId) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [categoryName]: optionId,
    }));
  };

  const handleAccessoryToggle = (accessoryId) => {
    setSelectedAccessories((prev) =>
      prev.includes(accessoryId)
        ? prev.filter((id) => id !== accessoryId)
        : [...prev, accessoryId]
    );
  };

  const handleSaveConfiguration = async () => {
    if (!selectedVariantId) return;

    const configuration = {
      product_id: productId,
      variant_id: selectedVariantId,
      selected_options: selectedOptions,
      selected_accessories: selectedAccessories,
      configuration_name: `${productDetails?.product.name} Configuration`,
    };

    try {
      await apiService.saveConfiguration(configuration);
      setPdfStatus({
        type: "success",
        message: "Configuration saved successfully!",
      });
      setTimeout(() => setPdfStatus(null), 3000);
    } catch (err) {
      console.error("Error saving configuration:", err);
      setPdfStatus({ type: "error", message: "Failed to save configuration" });
      setTimeout(() => setPdfStatus(null), 3000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex justify-center items-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <div className="text-xl text-slate-600">
            Loading product details...
          </div>
        </div>
      </div>
    );
  }

  if (error || !productDetails) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-red-50 flex justify-center items-center">
        <div className="text-center bg-white p-8 rounded-lg shadow-lg">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <div className="text-red-600 text-xl mb-4">
            {error || "Product not found"}
          </div>
          <button
            onClick={onBack}
            className="text-blue-600 hover:text-blue-800 flex items-center mx-auto"
          >
            <ArrowLeft size={16} className="mr-2" />
            Back to Product Types
          </button>
        </div>
      </div>
    );
  }

  const selectedVariant = productDetails.variants.find(
    (v) => v.id === selectedVariantId
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Professional Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={onBack}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-6 transition-colors group"
          >
            <ArrowLeft
              size={20}
              className="mr-2 group-hover:-translate-x-1 transition-transform"
            />
            Back to Product Types
          </button>

          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-3">
                <h1 className="text-4xl font-light text-slate-900">
                  {productDetails.product.name}
                </h1>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  Professional Series
                </span>
              </div>
              <p className="text-slate-600 max-w-2xl text-lg leading-relaxed">
                {productDetails.product.description}
              </p>
            </div>

            <div className="text-right bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-2">Part Code</div>
              <div className="font-mono text-xl font-semibold text-slate-900 bg-white px-4 py-2 rounded border">
                {currentPartCode || "Select options..."}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {pdfStatus && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
          <div
            className={`flex items-center p-4 rounded-lg ${
              pdfStatus.type === "success"
                ? "bg-green-50 text-green-800 border border-green-200"
                : pdfStatus.type === "error"
                ? "bg-red-50 text-red-800 border border-red-200"
                : "bg-blue-50 text-blue-800 border border-blue-200"
            }`}
          >
            {pdfStatus.type === "success" && (
              <CheckCircle className="w-5 h-5 mr-3 flex-shrink-0" />
            )}
            {pdfStatus.type === "error" && (
              <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
            )}
            {pdfStatus.type === "info" && (
              <Loader className="w-5 h-5 mr-3 flex-shrink-0 animate-spin" />
            )}
            <span className="font-medium">{pdfStatus.message}</span>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-3 space-y-8">
            {/* Power Rating Selection */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
              <h3 className="text-2xl font-semibold text-slate-900 mb-6 flex items-center">
                <span className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                  1
                </span>
                Select Power Rating
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {productDetails.variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariantId(variant.id)}
                    className={`group relative p-6 border-2 rounded-xl text-center transition-all duration-200 ${
                      selectedVariantId === variant.id
                        ? "border-blue-500 bg-blue-50 shadow-lg scale-105"
                        : "border-slate-200 hover:border-slate-300 hover:shadow-md"
                    }`}
                  >
                    <div className="text-2xl font-bold text-slate-900 mb-2">
                      {variant.variant_name}
                    </div>
                    <div className="text-sm text-slate-600 space-y-1">
                      <div>{variant.system_output} lumens</div>
                      <div>{variant.system_power}W power</div>
                      <div>Efficiency: {variant.efficiency} lm/W</div>
                    </div>
                    <div className="text-2xl font-bold text-blue-600 mt-4">
                      ${variant.base_price.toFixed(2)}
                    </div>
                    {selectedVariantId === variant.id && (
                      <div className="absolute top-2 right-2">
                        <CheckCircle className="w-6 h-6 text-blue-500" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Configuration Options */}
            {productDetails.configuration_categories?.map((category, index) => (
              <div
                key={category.id}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-8"
              >
                <h3 className="text-2xl font-semibold text-slate-900 mb-6 flex items-center">
                  <span className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                    {index + 2}
                  </span>
                  {category.category_label}
                  {category.is_required && (
                    <span className="text-red-500 ml-2 text-lg">*</span>
                  )}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {category.options?.map((option) => (
                    <button
                      key={option.id}
                      onClick={() =>
                        handleOptionChange(category.category_name, option.id)
                      }
                      className={`group relative p-6 border-2 rounded-xl text-center transition-all duration-200 ${
                        selectedOptions[category.category_name] === option.id
                          ? "border-blue-500 bg-blue-50 shadow-lg"
                          : "border-slate-200 hover:border-slate-300 hover:shadow-md"
                      }`}
                    >
                      <div className="text-lg font-semibold text-slate-900 mb-2">
                        {option.option_label}
                      </div>
                      {option.price_modifier !== 0 && (
                        <div className="text-sm font-medium text-blue-600">
                          {option.price_modifier > 0 ? "+" : ""}$
                          {option.price_modifier.toFixed(2)}
                        </div>
                      )}
                      {selectedOptions[category.category_name] ===
                        option.id && (
                        <div className="absolute top-2 right-2">
                          <CheckCircle className="w-5 h-5 text-blue-500" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* Accessories */}
            {productDetails.accessories?.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
                <h3 className="text-2xl font-semibold text-slate-900 mb-6 flex items-center">
                  <span className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                    {(productDetails.configuration_categories?.length || 0) + 2}
                  </span>
                  Optional Accessories
                </h3>
                <div className="space-y-4">
                  {productDetails.accessories.map((accessory) => (
                    <label
                      key={accessory.id}
                      className="group flex items-center space-x-6 p-6 border-2 border-slate-200 rounded-xl hover:border-slate-300 hover:shadow-md cursor-pointer transition-all duration-200"
                    >
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={selectedAccessories.includes(accessory.id)}
                          onChange={() => handleAccessoryToggle(accessory.id)}
                          className="w-6 h-6 text-blue-600 border-2 border-slate-300 rounded focus:ring-blue-500 focus:ring-2"
                        />
                        {selectedAccessories.includes(accessory.id) && (
                          <CheckCircle className="w-6 h-6 text-blue-500 absolute inset-0" />
                        )}
                      </div>

                      {accessory.image_url && (
                        <div className="w-20 h-16 bg-slate-100 rounded-lg flex items-center justify-center overflow-hidden">
                          <img
                            src={accessory.image_url}
                            alt={accessory.name}
                            className="max-w-full max-h-full object-contain"
                            onError={(e) => {
                              e.currentTarget.style.display = "none";
                            }}
                          />
                        </div>
                      )}

                      <div className="flex-1">
                        <div className="text-lg font-semibold text-slate-900 mb-1">
                          {accessory.name}
                        </div>
                        <div className="text-sm text-slate-600 mb-2">
                          {accessory.description}
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-sm text-slate-500">
                            Part: {accessory.part_code}
                          </div>
                          {accessory.price && (
                            <div className="text-lg font-semibold text-blue-600">
                              ${accessory.price.toFixed(2)}
                            </div>
                          )}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Product Features */}
            {productDetails.features?.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
                <h3 className="text-2xl font-semibold text-slate-900 mb-6">
                  Technical Specifications
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {productDetails.features.map((feature) => (
                    <div
                      key={feature.id}
                      className="flex justify-between items-center py-3 px-4 bg-slate-50 rounded-lg"
                    >
                      <span className="text-slate-600 font-medium">
                        {feature.feature_label}:
                      </span>
                      <span className="font-semibold text-slate-900">
                        {feature.feature_value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Professional Summary Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-6 sticky top-8">
              <h3 className="text-xl font-semibold text-slate-900 mb-6 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-blue-600" />
                Configuration Summary
              </h3>

              <div className="space-y-4 mb-8">
                <div className="flex justify-between py-3 border-b border-slate-100">
                  <span className="text-slate-600 font-medium">Product:</span>
                  <span className="font-semibold text-slate-900 text-right text-sm">
                    {productDetails.product.name}
                  </span>
                </div>

                {selectedVariant && (
                  <div className="flex justify-between py-3 border-b border-slate-100">
                    <span className="text-slate-600 font-medium">Power:</span>
                    <span className="font-semibold text-slate-900">
                      {selectedVariant.variant_name}
                    </span>
                  </div>
                )}

                {Object.entries(selectedOptions).map(
                  ([categoryName, optionId]) => {
                    const category =
                      productDetails.configuration_categories?.find(
                        (cat) => cat.category_name === categoryName
                      );
                    const option = category?.options?.find(
                      (opt) => opt.id === optionId
                    );

                    if (!option) return null;

                    return (
                      <div
                        key={categoryName}
                        className="flex justify-between py-3 border-b border-slate-100"
                      >
                        <span className="text-slate-600 font-medium">
                          {category?.category_label}:
                        </span>
                        <span className="font-semibold text-slate-900">
                          {option.option_label}
                        </span>
                      </div>
                    );
                  }
                )}

                {selectedAccessories.length > 0 && (
                  <div className="pt-2">
                    <div className="text-sm font-semibold text-slate-900 mb-3">
                      Accessories:
                    </div>
                    {selectedAccessories.map((accId) => {
                      const acc = productDetails.accessories?.find(
                        (a) => a.id === accId
                      );
                      return acc ? (
                        <div
                          key={accId}
                          className="py-2 px-3 bg-slate-50 rounded mb-2"
                        >
                          <span className="text-sm text-slate-700 font-medium">
                            {acc.name}
                          </span>
                          <div className="text-xs text-slate-500">
                            ${acc.price?.toFixed(2)}
                          </div>
                        </div>
                      ) : null;
                    })}
                  </div>
                )}
              </div>

              <div className="border-t border-slate-200 pt-6 mb-8">
                <div className="flex justify-between text-2xl font-bold">
                  <span className="text-slate-900">Total:</span>
                  <span className="text-blue-600">
                    ${currentPrice.toFixed(2)}
                  </span>
                </div>
                <div className="text-sm text-slate-500 mt-1">
                  Excluding taxes and shipping
                </div>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleSaveConfiguration}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center font-medium shadow-sm"
                >
                  <Save size={18} className="mr-2" />
                  Save Configuration
                </button>

                <button className="w-full border-2 border-blue-600 text-blue-600 py-3 px-4 rounded-lg hover:bg-blue-600 hover:text-white transition-colors flex items-center justify-center font-medium">
                  <ShoppingCart size={18} className="mr-2" />
                  Request Quote
                </button>

                <button
                  onClick={handleDownloadDatasheet}
                  disabled={pdfGenerating}
                  className="w-full border border-slate-300 text-slate-700 py-3 px-4 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {pdfGenerating ? (
                    <Loader size={18} className="mr-2 animate-spin" />
                  ) : (
                    <Download size={18} className="mr-2" />
                  )}
                  {pdfGenerating
                    ? "Generating..."
                    : "Download Professional Datasheet"}
                </button>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-800">
                  <strong>Professional Features:</strong>
                  <ul className="mt-2 space-y-1 text-xs">
                    <li>• Technical specifications</li>
                    <li>• Photometric data</li>
                    <li>• Certification details</li>
                    <li>• Professional layout</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedProductConfigurator;
