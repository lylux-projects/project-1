// src/services/api.ts
const API_BASE_URL = 'http://localhost:8000/api';

// Types based on your backend models
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  category_image_url?: string;
  display_order: number;
}

export interface Product {
  id: number;
  category_id: number;
  name: string;
  base_part_code: string;
  description?: string;
  product_image_url?: string;
  dimension_image_url?: string;
}

export interface ProductVariant {
  id: number;
  product_id: number;
  variant_name: string;
  part_code_suffix: string;
  system_output: number;
  system_power: number;
  efficiency: number;
  specifications: Record<string, any>;
  base_price: number;
  display_order: number;
}

export interface ConfigurationOption {
  id: number;
  category_id: number;
  option_value: string;
  option_label: string;
  part_code_suffix: string;
  price_modifier: number;
  is_default: boolean;
  display_order: number;
  option_image_url?: string;
}

export interface ConfigurationCategory {
  id: number;
  product_id: number;
  section_name: string;
  section_label: string;
  category_name: string;
  category_label: string;
  part_code_position: number;
  is_required: boolean;
  display_order: number;
  options: ConfigurationOption[];
}

export interface Accessory {
  id: number;
  product_id: number;
  name: string;
  part_code: string;
  description?: string;
  price: number;
  accessory_category: string;
}

export interface ProductFeature {
  id: number;
  product_id: number;
  feature_type: string;
  feature_label: string;
  feature_value: string;
  feature_icon_url?: string;
  display_order: number;
}

export interface VisualAsset {
  id: number;
  product_id: number;
  asset_type: string;
  asset_category: string;
  file_url: string;
  file_name: string;
  display_order: number;
}

export interface ProductDetails {
  product: Product;
  variants: ProductVariant[];
  configuration_categories: ConfigurationCategory[];
  accessories: Accessory[];
  features: ProductFeature[];
  visual_assets: VisualAsset[];
}

export interface UserConfiguration {
  product_id: number;
  variant_id: number;
  selected_options: Record<string, number>;
  selected_accessories: number[];
  configuration_name?: string;
  notes?: string;
}

export interface PriceCalculation {
  total_price: number;
}

export interface PartCodeGeneration {
  part_code: string;
}

// API Service Class
class ApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Get all categories
  async getCategories(): Promise<Category[]> {
    return this.fetchApi<Category[]>('/products/categories');
  }

  // Get products by category
  async getProductsByCategory(categorySlug: string): Promise<Product[]> {
    return this.fetchApi<Product[]>(`/products/categories/${categorySlug}/products`);
  }

  // Get detailed product information - FIXED ENDPOINT
  async getProductDetails(productId: number): Promise<ProductDetails> {
    return this.fetchApi<ProductDetails>(`/products/product-details/${productId}`);
  }

  // Calculate configuration price
  async calculatePrice(configuration: UserConfiguration): Promise<PriceCalculation> {
    return this.fetchApi<PriceCalculation>('/products/configure/calculate-price', {
      method: 'POST',
      body: JSON.stringify(configuration),
    });
  }

  // Generate part code
  async generatePartCode(configuration: UserConfiguration): Promise<PartCodeGeneration> {
    return this.fetchApi<PartCodeGeneration>('/products/configure/generate-part-code', {
      method: 'POST',
      body: JSON.stringify(configuration),
    });
  }

  // Save configuration
  async saveConfiguration(configuration: UserConfiguration): Promise<any> {
    return this.fetchApi('/products/configure/save', {
      method: 'POST',
      body: JSON.stringify(configuration),
    });
  }
}

export const apiService = new ApiService();