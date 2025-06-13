# At the top of your products.py file, make sure you have these imports:
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from app.services.supabase_client import supabase
from app.services.pdf_generator import DatasheetGenerator  # Make sure this import works
from io import BytesIO
import json

router = APIRouter()

# Pydantic Models
class PDFGenerationRequest(BaseModel):
    product_name: str
    base_part_code: str
    final_part_code: Optional[str] = None
    variants: List[dict]
    selected_variant_id: Optional[int] = None
    selected_variant_index: Optional[int] = 0
    selected_options: dict
    accessories: Optional[List[dict]] = []
    visual_assets: Optional[dict] = {}  # This should receive the visual assets
    product: Optional[dict] = {}        # This should receive the product info

class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    category_image_url: Optional[str]
    display_order: int

class Product(BaseModel):
    id: int
    category_id: int
    name: str
    base_part_code: str
    description: Optional[str]
    product_image_url: Optional[str]
    dimension_image_url: Optional[str]

class ProductVariant(BaseModel):
    id: int
    product_id: int
    variant_name: str
    part_code_suffix: str
    system_output: int
    system_power: int
    efficiency: int
    specifications: dict
    base_price: float
    display_order: int

class ConfigurationOption(BaseModel):
    id: int
    category_id: int
    option_value: str
    option_label: str
    part_code_suffix: str
    price_modifier: float
    is_default: bool
    display_order: int
    option_image_url: Optional[str]

class ConfigurationCategory(BaseModel):
    id: int
    product_id: int
    section_name: str
    section_label: str
    category_name: str
    category_label: str
    part_code_position: int
    is_required: bool
    display_order: int
    options: List[ConfigurationOption] = []

class Accessory(BaseModel):
    id: int
    product_id: int
    name: str
    part_code: str
    description: Optional[str]
    price: float
    accessory_category: str

class UserConfiguration(BaseModel):
    product_id: int
    variant_id: int
    selected_options: dict
    selected_accessories: List[int]
    configuration_name: Optional[str]
    notes: Optional[str]

# Test endpoints
@router.get("/test")
async def test_products():
    """Simple test endpoint"""
    return {"message": "Products router is working!"}

@router.get("/test-db-simple")
async def test_db_simple():
    try:
        result = supabase.table('categories').select('name').limit(1).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Debug endpoints (specific routes come first)
@router.get("/debug/all-data")
async def debug_all_data():
    """Debug endpoint to see all data"""
    try:
        categories = supabase.table('categories').select('*').execute()
        products = supabase.table('products').select('*').execute()
        variants = supabase.table('product_variants').select('*').execute()
        
        return {
            "categories_count": len(categories.data),
            "categories": categories.data,
            "products_count": len(products.data), 
            "products": products.data,
            "variants_count": len(variants.data),
            "variants": variants.data
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/debug/check-options")
async def check_options():
    """Check configuration options"""
    try:
        options = supabase.table('configuration_options').select('*').execute()
        return {
            "options_count": len(options.data),
            "options": options.data
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug/check-product-data/{product_id}")
async def check_product_data(product_id: int):
    """Check what data exists for a product"""
    try:
        results = {}
        
        # Check each table one by one
        try:
            product_data = supabase.table('products').select('*').eq('id', product_id).execute()
            results['product'] = product_data.data
            results['product_count'] = len(product_data.data)
        except Exception as e:
            results['product_error'] = str(e)
        
        try:
            variants_data = supabase.table('product_variants').select('*').eq('product_id', product_id).execute()
            results['variants'] = variants_data.data
            results['variants_count'] = len(variants_data.data)
        except Exception as e:
            results['variants_error'] = str(e)
        
        try:
            config_data = supabase.table('configuration_categories').select('*').eq('product_id', product_id).execute()
            results['config_categories'] = config_data.data
            results['config_categories_count'] = len(config_data.data)
        except Exception as e:
            results['config_categories_error'] = str(e)
        
        try:
            accessories_data = supabase.table('accessories').select('*').eq('product_id', product_id).execute()
            results['accessories'] = accessories_data.data
            results['accessories_count'] = len(accessories_data.data)
        except Exception as e:
            results['accessories_error'] = str(e)
        
        return results
    except Exception as e:
        return {"main_error": str(e)}

@router.get("/debug/product-detailed/{product_id}")
async def debug_product_detailed(product_id: int):
    """Debug each step of product loading"""
    result = {}
    
    try:
        # Step 1: Get product
        result["step1"] = "Getting product..."
        product_result = supabase.table('products').select('*').eq('id', product_id).execute()
        if not product_result.data:
            return {"error": "Product not found", "step": "step1"}
        result["step1"] = "✓ Product found"
        result["product"] = product_result.data[0]
        
        # Step 2: Get variants
        result["step2"] = "Getting variants..."
        variants_result = supabase.table('product_variants').select('*').eq('product_id', product_id).eq('is_active', True).order('display_order').execute()
        result["step2"] = f"✓ Found {len(variants_result.data)} variants"
        result["variants_count"] = len(variants_result.data)
        
        # Step 3: Get config categories
        result["step3"] = "Getting config categories..."
        config_cats_result = supabase.table('configuration_categories').select('*').eq('product_id', product_id).order('display_order').execute()
        result["step3"] = f"✓ Found {len(config_cats_result.data)} categories"
        result["categories_count"] = len(config_cats_result.data)
        
        # Step 4: Get options for each category
        result["step4"] = "Getting options for categories..."
        configuration_categories = []
        for i, cat in enumerate(config_cats_result.data):
            result[f"step4_cat_{i}"] = f"Getting options for category {cat['id']}..."
            options_result = supabase.table('configuration_options').select('*').eq('category_id', cat['id']).order('display_order').execute()
            cat['options'] = options_result.data
            configuration_categories.append(cat)
            result[f"step4_cat_{i}"] = f"✓ Found {len(options_result.data)} options for category {cat['id']}"
        
        result["step4"] = f"✓ Processed all {len(configuration_categories)} categories"
        
        # Step 5: Get accessories
        result["step5"] = "Getting accessories..."
        accessories_result = supabase.table('accessories').select('*').eq('product_id', product_id).eq('is_active', True).order('display_order').execute()
        result["step5"] = f"✓ Found {len(accessories_result.data)} accessories"
        
        # Step 6: Get features
        result["step6"] = "Getting features..."
        features_result = supabase.table('product_features').select('*').eq('product_id', product_id).order('display_order').execute()
        result["step6"] = f"✓ Found {len(features_result.data)} features"
        
        # Step 7: Get visual assets
        result["step7"] = "Getting visual assets..."
        assets_result = supabase.table('visual_assets').select('*').eq('product_id', product_id).order('display_order').execute()
        result["step7"] = f"✓ Found {len(assets_result.data)} visual assets"
        
        result["final"] = "✓ All steps completed successfully!"
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
        return result

# Categories endpoints
@router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all product categories"""
    try:
        result = supabase.table('categories').select('*').eq('is_active', True).order('display_order').execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/categories/{category_slug}/products")
async def get_products_by_category(category_slug: str):
    """Get products by category slug"""
    try:
        # First get category ID
        category_result = supabase.table('categories').select('id').eq('slug', category_slug).execute()
        if not category_result.data:
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_id = category_result.data[0]['id']
        
        # Get products in this category
        result = supabase.table('products').select('*').eq('category_id', category_id).eq('is_active', True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/product-details/{product_id}")
async def get_product_details_new(product_id: int):
    """Get detailed product information including global visual assets"""
    try:
        # Get product basic info
        product_result = supabase.table('products').select('*').eq('id', product_id).execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = product_result.data[0]
        
        # Get product variants
        variants_result = supabase.table('product_variants').select('*').eq('product_id', product_id).eq('is_active', True).order('display_order').execute()
        
        # Get configuration categories with options
        config_cats_result = supabase.table('configuration_categories').select('*').eq('product_id', product_id).order('display_order').execute()
        
        configuration_categories = []
        for cat in config_cats_result.data:
            # Get options for this category - make sure to include option_image_url
            options_result = supabase.table('configuration_options').select('id, category_id, option_value, option_label, part_code_suffix, price_modifier, is_default, display_order, option_image_url').eq('category_id', cat['id']).order('display_order').execute()
            cat['options'] = options_result.data if options_result.data else []
            configuration_categories.append(cat)
        
        # SAFE: Get ALL accessories columns to see what exists
        try:
            # First, just get all columns to see what's available
            accessories_result = supabase.table('accessories').select('*').eq('product_id', product_id).execute()
            
            # Add missing fields for compatibility with frontend/PDF
            for accessory in accessories_result.data:
                # Add fields that might be missing
                if 'image_url' not in accessory:
                    accessory['image_url'] = None
                if 'price' not in accessory:
                    accessory['price'] = 0.0
                if 'is_active' not in accessory:
                    accessory['is_active'] = True
                if 'display_order' not in accessory:
                    accessory['display_order'] = 0
                if 'accessory_category' not in accessory:
                    accessory['accessory_category'] = 'General'
            
            # Filter active accessories if the field exists
            if accessories_result.data and 'is_active' in accessories_result.data[0]:
                accessories_result.data = [acc for acc in accessories_result.data if acc.get('is_active', True)]
                
        except Exception as e:
            print(f"Error getting accessories: {e}")
            # Return empty accessories if there's an issue
            accessories_result = type('MockResult', (), {'data': []})()
        
        # Get product features
        try:
            features_result = supabase.table('product_features').select('*').eq('product_id', product_id).order('display_order').execute()
        except Exception as e:
            print(f"Error getting features: {e}")
            features_result = type('MockResult', (), {'data': []})()
        
        # Get visual assets - BOTH product-specific AND global assets
        try:
            assets_result = supabase.table('visual_assets').select('*').or_(f'product_id.eq.{product_id},is_global.eq.true').order('display_order').execute()
        except Exception as e:
            print(f"Error getting visual assets: {e}")
            assets_result = type('MockResult', (), {'data': []})()
        
        # Organize visual assets by type
        visual_assets = {
            'certifications': [],
            'product_images': [],
            'dimension_images': [],
            'all_assets': assets_result.data
        }
        
        for asset in assets_result.data:
            if asset['asset_type'] == 'certification':
                visual_assets['certifications'].append(asset)
            elif 'product' in asset.get('asset_category', '').lower():
                visual_assets['product_images'].append(asset)
            elif 'dimension' in asset.get('asset_category', '').lower():
                visual_assets['dimension_images'].append(asset)
        
        return {
            "product": product,
            "variants": variants_result.data,
            "configuration_categories": configuration_categories,
            "accessories": accessories_result.data,
            "features": features_result.data,
            "visual_assets": visual_assets
        }
    except Exception as e:
        print(f"Error in get_product_details_new: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/products/{product_id}")
async def get_product_details(product_id: int):
    """Get detailed product information"""
    try:
        # Get product basic info
        product_result = supabase.table('products').select('*').eq('id', product_id).execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = product_result.data[0]
        
        # Get product variants
        variants_result = supabase.table('product_variants').select('*').eq('product_id', product_id).eq('is_active', True).order('display_order').execute()
        
        # Get configuration categories with options
        config_cats_result = supabase.table('configuration_categories').select('*').eq('product_id', product_id).order('display_order').execute()
        
        configuration_categories = []
        for cat in config_cats_result.data:
            # Get options for this category
            options_result = supabase.table('configuration_options').select('*').eq('category_id', cat['id']).order('display_order').execute()
            cat['options'] = options_result.data if options_result.data else []
            configuration_categories.append(cat)
        
        # SAFE: Get accessories with all columns
        try:
            accessories_result = supabase.table('accessories').select('*').eq('product_id', product_id).execute()
            # Add missing fields for compatibility
            for accessory in accessories_result.data:
                if 'image_url' not in accessory:
                    accessory['image_url'] = None
                if 'price' not in accessory:
                    accessory['price'] = 0.0
                if 'is_active' not in accessory:
                    accessory['is_active'] = True
                if 'accessory_category' not in accessory:
                    accessory['accessory_category'] = 'General'
        except Exception as e:
            print(f"Error getting accessories: {e}")
            accessories_result = type('MockResult', (), {'data': []})()
        
        # Get product features
        try:
            features_result = supabase.table('product_features').select('*').eq('product_id', product_id).order('display_order').execute()
        except Exception:
            features_result = type('MockResult', (), {'data': []})()
        
        # Get visual assets
        try:
            assets_result = supabase.table('visual_assets').select('*').eq('product_id', product_id).order('display_order').execute()
        except Exception:
            assets_result = type('MockResult', (), {'data': []})()
        
        return {
            "product": product,
            "variants": variants_result.data,
            "configuration_categories": configuration_categories,
            "accessories": accessories_result.data,
            "features": features_result.data,
            "visual_assets": assets_result.data
        }
    except Exception as e:
        print(f"Error in get_product_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Configuration endpoints
@router.post("/configure/calculate-price")
async def calculate_configuration_price(config: UserConfiguration):
    """Calculate total price for a configuration"""
    try:
        # Get base variant price
        variant_result = supabase.table('product_variants').select('base_price').eq('id', config.variant_id).execute()
        if not variant_result.data:
            raise HTTPException(status_code=404, detail="Variant not found")
        
        base_price = float(variant_result.data[0]['base_price'])
        total_price = base_price
        
        # Add configuration option price modifiers
        for option_id in config.selected_options.values():
            if option_id:
                option_result = supabase.table('configuration_options').select('price_modifier').eq('id', option_id).execute()
                if option_result.data:
                    total_price += float(option_result.data[0]['price_modifier'])
        
        # Add accessory prices
        if config.selected_accessories:
            accessories_result = supabase.table('accessories').select('price').in_('id', config.selected_accessories).execute()
            for accessory in accessories_result.data:
                total_price += float(accessory['price'])
        
        return {"total_price": round(total_price, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/configure/generate-part-code")
async def generate_part_code(config: UserConfiguration):
    """Generate part code based on configuration"""
    try:
        # Get product base code
        product_result = supabase.table('products').select('base_part_code').eq('id', config.product_id).execute()
        if not product_result.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        base_code = product_result.data[0]['base_part_code']
        
        # Get variant suffix
        variant_result = supabase.table('product_variants').select('part_code_suffix').eq('id', config.variant_id).execute()
        if not variant_result.data:
            raise HTTPException(status_code=404, detail="Variant not found")
        
        variant_suffix = variant_result.data[0]['part_code_suffix']
        
        # Build part code: BASE-VARIANT-OPTION1-OPTION2-etc
        part_code_parts = [base_code, variant_suffix]
        
        # Get configuration categories and their selected options in order
        config_cats_result = supabase.table('configuration_categories').select('*').eq('product_id', config.product_id).eq('is_required', True).order('part_code_position').execute()
        
        for cat in config_cats_result.data:
            if cat['part_code_position'] > 0:  # Only include if it has a position in part code
                category_key = cat['category_name']
                if category_key in config.selected_options:
                    option_id = config.selected_options[category_key]
                    option_result = supabase.table('configuration_options').select('part_code_suffix').eq('id', option_id).execute()
                    if option_result.data and option_result.data[0]['part_code_suffix']:
                        part_code_parts.append(option_result.data[0]['part_code_suffix'])
        
        final_part_code = '-'.join(part_code_parts)
        return {"part_code": final_part_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/generate-datasheet")
async def generate_datasheet(request: PDFGenerationRequest):
    """Generate and return a PDF datasheet with enhanced debugging"""
    try:
        print("=== BACKEND PDF GENERATION DEBUG ===")
        print(f"Product name: {request.product_name}")
        print(f"Request type: {type(request)}")
        
        # Convert request to dict for the generator
        product_data = request.dict()
        
        # CRITICAL FIX: Fetch certifications from database
        # Get the product ID from the request or fetch it
        product_id = None
        if request.product and 'id' in request.product:
            product_id = request.product['id']
        else:
            # Try to get product ID from product name
            product_result = supabase.table('products').select('id').eq('name', request.product_name).execute()
            if product_result.data:
                product_id = product_result.data[0]['id']
        
        if product_id:
            print(f"=== FETCHING CERTIFICATIONS FOR PRODUCT ID: {product_id} ===")
            
            # Fetch visual assets from database (same logic as get_product_details_new)
            try:
                assets_result = supabase.table('visual_assets').select('*').or_(f'product_id.eq.{product_id},is_global.eq.true').order('display_order').execute()
                
                # Organize visual assets by type
                visual_assets = {
                    'certifications': [],
                    'product_images': [],
                    'dimension_images': [],
                    'all_assets': assets_result.data
                }
                
                for asset in assets_result.data:
                    if asset['asset_type'] == 'certification':
                        visual_assets['certifications'].append(asset)
                    elif 'product' in asset.get('asset_category', '').lower():
                        visual_assets['product_images'].append(asset)
                    elif 'dimension' in asset.get('asset_category', '').lower():
                        visual_assets['dimension_images'].append(asset)
                
                # Update product_data with fetched visual assets
                product_data['visual_assets'] = visual_assets
                
                print(f"✓ Fetched {len(visual_assets['certifications'])} certifications from database")
                for i, cert in enumerate(visual_assets['certifications']):
                    print(f"  DB Cert {i}: {cert.get('file_name', 'NO_NAME')} -> {cert.get('file_url', 'NO_URL')[:50]}...")
                
            except Exception as e:
                print(f"Error fetching visual assets: {e}")
                # Use empty certifications as fallback
                product_data['visual_assets'] = {'certifications': []}
        else:
            print("WARNING: Could not determine product ID - using request visual assets")
        
        # Debug the final visual assets structure
        print(f"=== FINAL VISUAL ASSETS DEBUG ===")
        va = product_data.get('visual_assets', {})
        print(f"Visual assets type: {type(va)}")
        if va:
            certs = va.get('certifications', [])
            print(f"Final certifications count: {len(certs)}")
            for i, cert in enumerate(certs):
                print(f"  Final cert {i}: {cert.get('file_name', 'NO_NAME')} -> {cert.get('file_url', 'NO_URL')[:50]}...")
        else:
            print("ERROR: No visual assets in final product_data!")
        
        # Generate PDF
        generator = DatasheetGenerator()
        pdf_buffer = generator.generate_datasheet(product_data)
        
        # Return as streaming response
        filename = f"{request.product_name.replace(' ', '_')}_datasheet.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"ERROR in generate_datasheet: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/configure/save")
async def save_user_configuration(config: UserConfiguration):
    """Save user configuration"""
    try:
        # Calculate price and generate part code first
        price_response = await calculate_configuration_price(config)
        part_code_response = await generate_part_code(config)
        
        # Save configuration
        insert_data = {
            "user_id": None,  # You'll need to implement authentication to get actual user_id
            "product_id": config.product_id,
            "variant_id": config.variant_id,
            "selected_options": config.selected_options,
            "selected_accessories": config.selected_accessories,
            "final_part_code": part_code_response["part_code"],
            "final_price": price_response["total_price"],
            "configuration_name": config.configuration_name,
            "notes": config.notes
        }
        
        result = supabase.table('user_configurations').insert(insert_data).execute()
        
        return {
            "message": "Configuration saved successfully",
            "configuration_id": result.data[0]['id'],
            "part_code": part_code_response["part_code"],
            "total_price": price_response["total_price"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# Add these endpoints to the end of your products.py file

@router.post("/generate-html-datasheet")
async def generate_html_datasheet(request: PDFGenerationRequest):
    """Generate HTML datasheet - uses same logic as PDF generator for now"""
    try:
        print("=== HTML DATASHEET GENERATION ===")
        print(f"Product name: {request.product_name}")
        
        # For now, redirect to the existing PDF generator
        # Later you can implement HTML-specific logic here
        return await generate_datasheet(request)
        
    except Exception as e:
        print(f"ERROR in generate_html_datasheet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating HTML datasheet: {str(e)}")

@router.post("/generate-professional-datasheet") 
async def generate_professional_datasheet(request: PDFGenerationRequest):
    """Generate professional datasheet - uses enhanced formatting"""
    try:
        print("=== PROFESSIONAL DATASHEET GENERATION ===")
        print(f"Product name: {request.product_name}")
        
        # For now, redirect to the existing PDF generator
        # Later you can add professional-specific formatting here
        return await generate_datasheet(request)
        
    except Exception as e:
        print(f"ERROR in generate_professional_datasheet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating professional datasheet: {str(e)}")