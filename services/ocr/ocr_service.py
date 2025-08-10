"""
OCR Service for Compliant-One Platform
Handles text extraction from images, scanned PDFs, and various document formats
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, TYPE_CHECKING
from datetime import datetime
import tempfile
import json
import hashlib

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Type checking imports
if TYPE_CHECKING:
    from PIL import Image as PILImage
else:
    try:
        from PIL import Image as PILImage
    except ImportError:
        PILImage = Any

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
    from pdf2image import convert_from_path, convert_from_bytes
    TESSERACT_AVAILABLE = True
except ImportError as e:
    TESSERACT_AVAILABLE = False
    print(f"OCR dependencies not available: {e}")
    # Create dummy classes for type hints when not available
    Image = Any

from utils.logger import get_logger

class OCRService:
    """
    Optical Character Recognition service for document processing
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.cache_dir = Path("data/ocr_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # OCR configuration
        self.tesseract_config = {
            'default': r'--oem 3 --psm 6',
            'table': r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!@#$%^&*()_+-=[]{}|;:,.<>?',
            'digits': r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            'single_word': r'--oem 3 --psm 8',
            'single_line': r'--oem 3 --psm 7',
            'sparse_text': r'--oem 3 --psm 11'
        }
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
        
        # Initialize Tesseract path if needed
        self._setup_tesseract()
        
        self.logger.info("OCR Service initialized")
    
    def _setup_tesseract(self):
        """Setup Tesseract OCR path"""
        if not TESSERACT_AVAILABLE:
            self.logger.warning("Tesseract OCR not available - install with: apt-get install tesseract-ocr")
            return
        
        # Common Tesseract paths
        tesseract_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',  # macOS
            'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',  # Windows
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                self.logger.info(f"Tesseract found at: {path}")
                return
        
        # Try system PATH
        try:
            import subprocess
            result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
            if result.returncode == 0:
                tesseract_path = result.stdout.strip()
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                self.logger.info(f"Tesseract found in PATH: {tesseract_path}")
                return
        except Exception:
            pass
        
        self.logger.warning("Tesseract not found in common locations")
    
    def _get_cache_key(self, file_path: Union[str, Path], preprocessing_params: Dict = None) -> str:
        """Generate cache key for OCR results"""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Include file modification time and preprocessing params in cache key
        try:
            mtime = file_path.stat().st_mtime
            content = f"{file_path}_{mtime}_{preprocessing_params or {}}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load OCR results from cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Save OCR results to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
    
    def preprocess_image(self, image: "PILImage.Image", enhancement_level: str = "medium") -> "PILImage.Image":
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            enhancement_level: "light", "medium", "heavy"
        
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to numpy array for OpenCV processing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            if enhancement_level == "light":
                # Light enhancement - basic operations
                cv_image = cv2.convertScaleAbs(cv_image, alpha=1.1, beta=10)
                
            elif enhancement_level == "medium":
                # Medium enhancement - noise reduction and sharpening
                # Gaussian blur to reduce noise
                cv_image = cv2.GaussianBlur(cv_image, (3, 3), 0)
                
                # Sharpen
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                cv_image = cv2.filter2D(cv_image, -1, kernel)
                
                # Adjust contrast and brightness
                cv_image = cv2.convertScaleAbs(cv_image, alpha=1.2, beta=15)
                
            elif enhancement_level == "heavy":
                # Heavy enhancement - morphological operations and advanced filtering
                # Convert to grayscale
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold to get binary image
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Morphological operations to clean up
                kernel = np.ones((2,2), np.uint8)
                binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                
                # Convert back to BGR for consistency
                cv_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            return processed_image
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def extract_text_from_image(
        self, 
        image_path: Union[str, Path, "PILImage.Image"], 
        config: str = "default",
        preprocess: bool = True,
        enhancement_level: str = "medium",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file or PIL Image object
            config: OCR configuration preset
            preprocess: Whether to preprocess image
            enhancement_level: Level of image enhancement
            use_cache: Whether to use cached results
        
        Returns:
            Dictionary with extracted text and metadata
        """
        if not TESSERACT_AVAILABLE:
            return {
                "success": False,
                "error": "Tesseract OCR not available",
                "text": "",
                "confidence": 0.0,
                "metadata": {}
            }
        
        try:
            # Handle different input types
            if isinstance(image_path, (str, Path)):
                image_path = Path(image_path)
                
                # Check cache
                if use_cache:
                    cache_key = self._get_cache_key(image_path, {
                        'config': config, 
                        'preprocess': preprocess, 
                        'enhancement_level': enhancement_level
                    })
                    cached_result = self._load_from_cache(cache_key)
                    if cached_result:
                        self.logger.debug(f"Using cached OCR result for {image_path.name}")
                        return cached_result
                
                # Load image
                image = Image.open(image_path)
            else:
                image = image_path
                cache_key = None
            
            # Preprocess image if requested
            if preprocess:
                image = self.preprocess_image(image, enhancement_level)
            
            # Get OCR config
            tesseract_config = self.tesseract_config.get(config, self.tesseract_config['default'])
            
            # Extract text
            extracted_text = pytesseract.image_to_string(image, config=tesseract_config)
            
            # Get confidence data
            try:
                data = pytesseract.image_to_data(image, config=tesseract_config, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            except Exception:
                avg_confidence = 0.0
            
            # Get bounding box data
            try:
                boxes = pytesseract.image_to_boxes(image, config=tesseract_config)
                word_count = len([line for line in boxes.split('\n') if line.strip()])
            except Exception:
                word_count = len(extracted_text.split())
            
            result = {
                "success": True,
                "text": extracted_text.strip(),
                "confidence": avg_confidence / 100.0,  # Normalize to 0-1
                "metadata": {
                    "config_used": config,
                    "preprocessed": preprocess,
                    "enhancement_level": enhancement_level if preprocess else None,
                    "word_count": word_count,
                    "character_count": len(extracted_text),
                    "extraction_timestamp": datetime.now().isoformat(),
                    "tesseract_version": pytesseract.get_tesseract_version()
                }
            }
            
            # Cache result
            if use_cache and cache_key:
                self._save_to_cache(cache_key, result)
            
            self.logger.info(f"OCR extraction completed. Text length: {len(extracted_text)}, Confidence: {avg_confidence:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"OCR extraction failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "confidence": 0.0,
                "metadata": {}
            }
    
    def extract_text_from_pdf(
        self, 
        pdf_path: Union[str, Path], 
        pages: Optional[List[int]] = None,
        config: str = "default",
        preprocess: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR (for scanned PDFs)
        
        Args:
            pdf_path: Path to PDF file
            pages: List of page numbers to process (1-indexed), None for all pages
            config: OCR configuration preset
            preprocess: Whether to preprocess images
            use_cache: Whether to use cached results
        
        Returns:
            Dictionary with extracted text and metadata
        """
        if not TESSERACT_AVAILABLE:
            return {
                "success": False,
                "error": "Tesseract OCR not available",
                "text": "",
                "pages_processed": 0,
                "metadata": {}
            }
        
        try:
            pdf_path = Path(pdf_path)
            
            # Check cache
            if use_cache:
                cache_key = self._get_cache_key(pdf_path, {
                    'pages': pages,
                    'config': config, 
                    'preprocess': preprocess
                })
                cached_result = self._load_from_cache(cache_key)
                if cached_result:
                    self.logger.debug(f"Using cached OCR result for {pdf_path.name}")
                    return cached_result
            
            # Convert PDF to images
            try:
                if pages:
                    # Convert specific pages (convert to 0-indexed)
                    images = convert_from_path(pdf_path, first_page=min(pages), last_page=max(pages))
                    # Filter to requested pages
                    page_indices = [p - min(pages) for p in pages]
                    images = [images[i] for i in page_indices if i < len(images)]
                else:
                    # Convert all pages
                    images = convert_from_path(pdf_path)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to convert PDF to images: {e}",
                    "text": "",
                    "pages_processed": 0,
                    "metadata": {}
                }
            
            # Extract text from each page
            all_text = []
            page_results = []
            total_confidence = 0.0
            
            for i, image in enumerate(images):
                page_num = pages[i] if pages else i + 1
                
                self.logger.debug(f"Processing page {page_num} of {pdf_path.name}")
                
                page_result = self.extract_text_from_image(
                    image, 
                    config=config, 
                    preprocess=preprocess,
                    use_cache=False  # Don't cache individual pages
                )
                
                if page_result["success"]:
                    page_text = page_result["text"]
                    all_text.append(f"--- Page {page_num} ---\n{page_text}")
                    
                    page_results.append({
                        "page_number": page_num,
                        "text": page_text,
                        "confidence": page_result["confidence"],
                        "word_count": page_result["metadata"].get("word_count", 0)
                    })
                    
                    total_confidence += page_result["confidence"]
                else:
                    self.logger.warning(f"Failed to extract text from page {page_num}")
            
            # Combine results
            combined_text = "\n\n".join(all_text)
            avg_confidence = total_confidence / len(images) if images else 0.0
            
            result = {
                "success": True,
                "text": combined_text,
                "pages_processed": len(page_results),
                "average_confidence": avg_confidence,
                "metadata": {
                    "pdf_file": str(pdf_path),
                    "total_pages": len(images),
                    "pages_requested": pages,
                    "config_used": config,
                    "preprocessed": preprocess,
                    "page_results": page_results,
                    "extraction_timestamp": datetime.now().isoformat()
                }
            }
            
            # Cache result
            if use_cache:
                self._save_to_cache(cache_key, result)
            
            self.logger.info(f"PDF OCR completed. Pages: {len(page_results)}, Total text length: {len(combined_text)}")
            return result
            
        except Exception as e:
            error_msg = f"PDF OCR extraction failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "pages_processed": 0,
                "metadata": {}
            }
    
    def extract_structured_data(
        self, 
        image_path: Union[str, Path, "PILImage.Image"],
        data_type: str = "table"
    ) -> Dict[str, Any]:
        """
        Extract structured data from images (tables, forms, etc.)
        
        Args:
            image_path: Path to image or PIL Image object
            data_type: Type of structured data ("table", "form", "invoice")
        
        Returns:
            Dictionary with structured data
        """
        try:
            # Use appropriate OCR config for structured data
            config_map = {
                "table": "table",
                "form": "default",
                "invoice": "default"
            }
            
            config = config_map.get(data_type, "default")
            
            # Extract text with specific configuration
            result = self.extract_text_from_image(
                image_path, 
                config=config, 
                preprocess=True,
                enhancement_level="medium"
            )
            
            if not result["success"]:
                return result
            
            # Parse structured data based on type
            structured_data = self._parse_structured_text(result["text"], data_type)
            
            result["structured_data"] = structured_data
            result["data_type"] = data_type
            
            return result
            
        except Exception as e:
            error_msg = f"Structured data extraction failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "structured_data": {},
                "data_type": data_type
            }
    
    def _parse_structured_text(self, text: str, data_type: str) -> Dict[str, Any]:
        """Parse extracted text into structured data"""
        import re
        
        structured = {}
        
        if data_type == "table":
            # Simple table parsing - split by lines and try to identify columns
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Look for table-like structures
            table_data = []
            for line in lines:
                # Split by multiple spaces or tabs
                cells = re.split(r'\s{2,}|\t+', line)
                if len(cells) > 1:
                    table_data.append(cells)
            
            structured["table"] = table_data
            structured["rows"] = len(table_data)
            structured["columns"] = max(len(row) for row in table_data) if table_data else 0
            
        elif data_type == "form":
            # Extract key-value pairs from form-like text
            lines = text.split('\n')
            form_data = {}
            
            for line in lines:
                # Look for patterns like "Label: Value" or "Label Value"
                colon_match = re.search(r'^([^:]+):\s*(.+)$', line.strip())
                if colon_match:
                    key, value = colon_match.groups()
                    form_data[key.strip()] = value.strip()
                else:
                    # Look for other patterns
                    words = line.strip().split()
                    if len(words) >= 2:
                        # Assume first word is label, rest is value
                        key = words[0].rstrip(':')
                        value = ' '.join(words[1:])
                        if len(key) > 1 and len(value) > 0:
                            form_data[key] = value
            
            structured["form_fields"] = form_data
            structured["field_count"] = len(form_data)
            
        elif data_type == "invoice":
            # Extract invoice-specific information
            invoice_data = {}
            
            # Look for common invoice patterns
            patterns = {
                'invoice_number': r'invoice\s*(?:number|#)?\s*:?\s*([A-Z0-9-]+)',
                'date': r'date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                'total': r'total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                'amount': r'amount\s*:?\s*\$?\s*([\d,]+\.?\d*)'
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    invoice_data[field] = match.group(1)
            
            structured["invoice_fields"] = invoice_data
        
        return structured
    
    def batch_process_images(
        self, 
        image_dir: Union[str, Path], 
        config: str = "default",
        file_pattern: str = "*",
        max_files: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process multiple images in a directory
        
        Args:
            image_dir: Directory containing images
            config: OCR configuration preset
            file_pattern: File pattern to match (e.g., "*.jpg")
            max_files: Maximum number of files to process
        
        Returns:
            Dictionary with batch processing results
        """
        try:
            image_dir = Path(image_dir)
            
            if not image_dir.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {image_dir}",
                    "results": []
                }
            
            # Find image files
            image_files = []
            for ext in self.supported_formats:
                pattern = file_pattern.replace("*", f"*{ext}")
                image_files.extend(image_dir.glob(pattern))
            
            # Limit files if specified
            if max_files:
                image_files = image_files[:max_files]
            
            if not image_files:
                return {
                    "success": True,
                    "message": "No image files found",
                    "results": []
                }
            
            # Process each image
            results = []
            successful = 0
            failed = 0
            
            for image_file in image_files:
                self.logger.debug(f"Processing {image_file.name}")
                
                result = self.extract_text_from_image(image_file, config=config)
                
                file_result = {
                    "file_name": image_file.name,
                    "file_path": str(image_file),
                    "success": result["success"],
                    "text": result["text"] if result["success"] else "",
                    "confidence": result.get("confidence", 0.0),
                    "error": result.get("error", "")
                }
                
                results.append(file_result)
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            
            return {
                "success": True,
                "results": results,
                "summary": {
                    "total_files": len(image_files),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / len(image_files)) * 100 if image_files else 0
                }
            }
            
        except Exception as e:
            error_msg = f"Batch processing failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "results": []
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for OCR"""
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            langs = pytesseract.get_languages(config='')
            return sorted(langs)
        except Exception as e:
            self.logger.warning(f"Failed to get supported languages: {e}")
            return ['eng']  # Default to English
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for OCR service"""
        try:
            health_status = {
                "service_name": "OCR Service",
                "status": "healthy" if TESSERACT_AVAILABLE else "degraded",
                "tesseract_available": TESSERACT_AVAILABLE,
                "dependencies": {
                    "pytesseract": TESSERACT_AVAILABLE,
                    "PIL": True,
                    "opencv": True,
                    "pdf2image": True
                },
                "cache_directory": str(self.cache_dir),
                "cache_files": len(list(self.cache_dir.glob("*.json"))) if self.cache_dir.exists() else 0
            }
            
            if TESSERACT_AVAILABLE:
                try:
                    health_status["tesseract_version"] = str(pytesseract.get_tesseract_version())
                    health_status["tesseract_path"] = pytesseract.pytesseract.tesseract_cmd
                    health_status["supported_languages"] = len(self.get_supported_languages())
                except Exception as e:
                    health_status["tesseract_error"] = str(e)
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "OCR Service",
                "status": "error",
                "error": str(e)
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear OCR cache"""
        try:
            if self.cache_dir.exists():
                cache_files = list(self.cache_dir.glob("*.json"))
                for cache_file in cache_files:
                    cache_file.unlink()
                
                return {
                    "success": True,
                    "message": f"Cleared {len(cache_files)} cache files"
                }
            else:
                return {
                    "success": True,
                    "message": "Cache directory does not exist"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to clear cache: {e}"
            }

def main():
    """Test OCR service functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR Service Test")
    parser.add_argument("--image", help="Path to image file")
    parser.add_argument("--pdf", help="Path to PDF file")
    parser.add_argument("--dir", help="Directory of images to process")
    parser.add_argument("--config", default="default", help="OCR configuration")
    parser.add_argument("--health", action="store_true", help="Show health status")
    
    args = parser.parse_args()
    
    ocr_service = OCRService()
    
    if args.health:
        health = ocr_service.health_check()
        print("OCR Service Health Check:")
        for key, value in health.items():
            print(f"  {key}: {value}")
    
    elif args.image:
        print(f"Processing image: {args.image}")
        result = ocr_service.extract_text_from_image(args.image, config=args.config)
        
        if result["success"]:
            print(f"Extracted text ({result['confidence']:.2f} confidence):")
            print("-" * 50)
            print(result["text"])
        else:
            print(f"Error: {result['error']}")
    
    elif args.pdf:
        print(f"Processing PDF: {args.pdf}")
        result = ocr_service.extract_text_from_pdf(args.pdf, config=args.config)
        
        if result["success"]:
            print(f"Extracted text from {result['pages_processed']} pages:")
            print("-" * 50)
            print(result["text"][:1000])  # Show first 1000 characters
            if len(result["text"]) > 1000:
                print(f"... (total length: {len(result['text'])} characters)")
        else:
            print(f"Error: {result['error']}")
    
    elif args.dir:
        print(f"Processing directory: {args.dir}")
        result = ocr_service.batch_process_images(args.dir, config=args.config)
        
        if result["success"]:
            print(f"Batch processing results:")
            print(f"  Total files: {result['summary']['total_files']}")
            print(f"  Successful: {result['summary']['successful']}")
            print(f"  Failed: {result['summary']['failed']}")
            print(f"  Success rate: {result['summary']['success_rate']:.1f}%")
        else:
            print(f"Error: {result['error']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
