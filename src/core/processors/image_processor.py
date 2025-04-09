from PIL import Image, ImageDraw, ImageFilter

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.mouth_region = None
        self.mouth_frames = []
        self.detected_lips = None
        
    def load_image(self, image_path):
        """Load and process an image"""
        try:
            # Load the image
            img = Image.open(image_path)
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            self.original_image = img.copy()
            self.processed_image = img.copy()
            
            # Detect facial features and lips
            self._detect_facial_features()
            
            # Generate mouth frames based on detected lips
            self.generate_mouth_frames()
            
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def reset_image(self):
        """Reset to original image"""
        if self.original_image:
            self.processed_image = self.original_image.copy()
            return True
        return False
    
    def resize_image(self, width, height):
        """Resize image maintaining aspect ratio and ensuring it fits within the UI"""
        if self.processed_image:
            # Get original dimensions
            orig_width, orig_height = self.processed_image.size
            
            # Calculate aspect ratios
            img_ratio = orig_width / orig_height
            frame_ratio = width / height
            
            # Determine new dimensions to fit within the frame
            if img_ratio > frame_ratio:
                # Image is wider than frame ratio - fit to width
                new_width = width
                new_height = int(width / img_ratio)
            else:
                # Image is taller than frame ratio - fit to height
                new_height = height
                new_width = int(height * img_ratio)
            
            # Add padding to center the image
            pad_x = (width - new_width) // 2
            pad_y = (height - new_height) // 2
            
            # Create a new image with padding
            padded_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Resize the original image
            resized_img = self.processed_image.resize((new_width, new_height), Image.LANCZOS)
            
            # Paste the resized image onto the padded image
            padded_img.paste(resized_img, (pad_x, pad_y))
            
            # Update the processed image
            self.processed_image = padded_img
            
            # Update mouth region coordinates
            if self.mouth_region:
                self._update_mouth_region(new_width, new_height, pad_x, pad_y)
            
            return True
        return False
    
    def _detect_facial_features(self):
        """Detect facial features in the image including lips"""
        if not self.processed_image:
            return
            
        width, height = self.processed_image.size
        
        # For a more accurate implementation, we would use face detection libraries
        # like OpenCV, dlib, or MediaPipe. For this implementation, we'll use a
        # more sophisticated estimation approach based on facial proportions.
        
        # Estimate face region (typically center 60% of image height)
        face_top = height * 0.2
        face_bottom = height * 0.8
        face_height = face_bottom - face_top
        face_center_x = width * 0.5
        
        # Estimate mouth position (typical human face proportions)
        # Mouth is typically around lower 1/3 of face
        mouth_y_center = face_top + (face_height * 0.75)
        
        # Estimate mouth width (typically around 40% of face width)
        face_width = width * 0.6
        mouth_width = face_width * 0.45
        
        # Detect lips from color information
        lips_top, lips_bottom = self._detect_lips_from_color(face_center_x, mouth_y_center, mouth_width)
        
        # Store detected lip coordinates
        self.detected_lips = {
            'center_x': face_center_x,
            'center_y': mouth_y_center,
            'width': mouth_width,
            'top': lips_top,
            'bottom': lips_bottom,
            'height': lips_bottom - lips_top
        }
        
        # Set mouth region based on detected lips
        lip_padding = mouth_width * 0.05  # Add some padding around lips
        self.mouth_region = (
            int(face_center_x - mouth_width/2 - lip_padding),
            int(lips_top - lip_padding),
            int(face_center_x + mouth_width/2 + lip_padding),
            int(lips_bottom + lip_padding)
        )
    
    def _detect_lips_from_color(self, center_x, center_y, width):
        """Detect lips using color information"""
        # In a real implementation, this would use computer vision to detect lip color
        # For this simplified version, we'll estimate based on likely lip position
        
        height = self.processed_image.height
        estimated_lip_height = width * 0.3  # Lips are typically wider than tall
        
        lips_top = center_y - estimated_lip_height * 0.4  # Upper lip is smaller
        lips_bottom = center_y + estimated_lip_height * 0.6  # Lower lip is bigger
        
        # Adjust based on image characteristics
        # For example, try to find red/pink pixels in this area
        try:
            # Sample region where lips should be
            lip_region = self.processed_image.crop((
                int(center_x - width/3),
                int(center_y - estimated_lip_height/2),
                int(center_x + width/3),
                int(center_y + estimated_lip_height/2)
            ))
            
            # Convert to RGB for analysis
            if lip_region.mode != 'RGB':
                lip_region = lip_region.convert('RGB')
            
            # Analyze pixels to find lip-colored pixels
            # Lips tend to be redder than surrounding skin
            lip_color_pixels = []
            for y in range(lip_region.height):
                for x in range(lip_region.width):
                    r, g, b = lip_region.getpixel((x, y))
                    # Check if pixel is lip-colored (higher red/pink component)
                    if r > 1.2 * g and r > 1.2 * b:
                        lip_color_pixels.append((y + int(center_y - estimated_lip_height/2)))
            
            # If we found lip-colored pixels, adjust the lip positions
            if lip_color_pixels:
                lips_top = min(lip_color_pixels)
                lips_bottom = max(lip_color_pixels)
        except Exception as e:
            print(f"Error in lip color detection: {e}")
            # Fallback to estimates if color detection fails
        
        return lips_top, lips_bottom
    
    def _update_mouth_region(self, width, height, pad_x=0, pad_y=0):
        """Update mouth region coordinates based on new image size and padding"""
        if not self.mouth_region:
            return
            
        # Get original mouth region
        x1, y1, x2, y2 = self.mouth_region
        
        # Calculate scale factors
        if self.original_image:
            scale_x = width / self.original_image.width
            scale_y = height / self.original_image.height
            
            # Scale the mouth region
            scaled_x1 = int(x1 * scale_x) + pad_x
            scaled_y1 = int(y1 * scale_y) + pad_y
            scaled_x2 = int(x2 * scale_x) + pad_x
            scaled_y2 = int(y2 * scale_y) + pad_y
            
            # Update the mouth region
            self.mouth_region = (scaled_x1, scaled_y1, scaled_x2, scaled_y2)
            
            # Ensure mouth region is within image bounds
            self._constrain_mouth_region_to_image()
    
    def _constrain_mouth_region_to_image(self):
        """Ensure mouth region is within image bounds"""
        if not self.processed_image or not self.mouth_region:
            return
            
        # Get image dimensions
        img_width, img_height = self.processed_image.size
        
        # Get mouth region
        x1, y1, x2, y2 = self.mouth_region
        
        # Adjust coordinates to stay within image bounds
        x1 = max(0, min(x1, img_width-1))
        y1 = max(0, min(y1, img_height-1))
        x2 = max(x1+1, min(x2, img_width))
        y2 = max(y1+1, min(y2, img_height))
        
        # Update mouth region
        self.mouth_region = (x1, y1, x2, y2)
    
    def generate_mouth_frames(self):
        """Generate realistic mouth shapes for animation"""
        if not self.processed_image or not self.mouth_region or not self.detected_lips:
            return
            
        # Extract mouth region dimensions
        x1, y1, x2, y2 = self.mouth_region
        mouth_width = x2 - x1
        mouth_height = y2 - y1
        
        # Get lip parameters
        lips = self.detected_lips
        center_x = lips['center_x'] - x1  # Relative to mouth region
        center_y = lips['center_y'] - y1  # Relative to mouth region
        lip_width = lips['width']
        lip_height = lips['height']
        
        # Extract original mouth area
        original_mouth = self.processed_image.crop(self.mouth_region)
        
        # Create a series of mouth shapes with different openness levels
        num_frames = 8  # Number of different mouth positions
        self.mouth_frames = []
        
        for i in range(num_frames):
            # Create a copy of original mouth
            mouth_img = original_mouth.copy()
            draw = ImageDraw.Draw(mouth_img)
            
            # Calculate openness based on frame index
            openness = i / (num_frames - 1)
            
            # If not fully closed, create mouth opening
            if openness > 0:
                # Calculate mouth opening dimensions
                open_width = lip_width * (0.5 + 0.3 * openness)
                open_height = lip_height * openness * 0.7
                
                # Create a mask for the open mouth
                mask = Image.new('L', mouth_img.size, 0)
                mask_draw = ImageDraw.Draw(mask)
                
                # Draw an ellipse for the mouth opening
                mask_draw.ellipse(
                    (center_x - open_width/2, center_y - open_height/2,
                     center_x + open_width/2, center_y + open_height/2),
                    fill=255
                )
                
                # Smooth the mask edges
                mask = mask.filter(ImageFilter.GaussianBlur(1))
                
                # Create a dark "mouth cavity" image
                mouth_cavity = Image.new('RGBA', mouth_img.size, (30, 10, 10, 255))
                
                # Apply the mask to the mouth cavity
                mouth_img.paste(mouth_cavity, (0, 0), mask)
                
                # Accentuate lips (slightly darker and more saturated)
                # Upper lip
                upper_lip_height = int(lip_height * 0.4)
                lip_shape = [
                    (center_x - lip_width/2, center_y - upper_lip_height*0.5),
                    (center_x - lip_width*0.25, center_y - upper_lip_height),
                    (center_x, center_y - upper_lip_height*0.8),
                    (center_x + lip_width*0.25, center_y - upper_lip_height),
                    (center_x + lip_width/2, center_y - upper_lip_height*0.5),
                ]
                draw.line(lip_shape, fill=(180, 80, 80, 255), width=2)
                
                # Lower lip
                lower_lip_height = int(lip_height * 0.5)
                lower_y = center_y + open_height/2 - 1
                lip_shape = [
                    (center_x - lip_width/2, lower_y),
                    (center_x - lip_width*0.25, lower_y + lower_lip_height*0.8),
                    (center_x, lower_y + lower_lip_height),
                    (center_x + lip_width*0.25, lower_y + lower_lip_height*0.8),
                    (center_x + lip_width/2, lower_y),
                ]
                draw.line(lip_shape, fill=(180, 80, 80, 255), width=2)
            
            # Ensure the image has an alpha channel
            if mouth_img.mode != 'RGBA':
                mouth_img = mouth_img.convert('RGBA')
            
            self.mouth_frames.append(mouth_img)
    
    def get_mouth_frame(self, openness):
        """Get a mouth frame for a specific openness value"""
        if not self.mouth_frames:
            return None
        
        # Ensure openness is between 0 and 1
        openness = max(0, min(1, openness))
        
        # Calculate the frame index based on openness
        frame_index = int(openness * (len(self.mouth_frames) - 1))
        
        # Clamp to valid range
        frame_index = max(0, min(frame_index, len(self.mouth_frames) - 1))
        
        return self.mouth_frames[frame_index]
    
    def apply_mouth_frame(self, openness):
        """Apply mouth frame to the current image"""
        if not self.processed_image or not self.mouth_region:
            return None
            
        # Create a copy of the current image
        display_img = self.processed_image.copy()
        
        # Get the appropriate mouth frame
        mouth_frame = self.get_mouth_frame(openness)
        if mouth_frame:
            # Get the mouth region coordinates
            x1, y1, x2, y2 = self.mouth_region
            
            # Ensure both images have the same mode
            if display_img.mode != mouth_frame.mode:
                # Convert mouth frame to match display image mode
                if display_img.mode == 'RGBA':
                    # If display is RGBA, ensure mouth frame is also RGBA
                    if mouth_frame.mode != 'RGBA':
                        mouth_frame = mouth_frame.convert('RGBA')
                else:
                    # If display is not RGBA, convert mouth frame to RGB
                    mouth_frame = mouth_frame.convert('RGB')
            
            # Create a mask from the alpha channel if available
            mask = None
            if mouth_frame.mode == 'RGBA':
                # Extract alpha channel for masking
                r, g, b, a = mouth_frame.split()
                mask = a
            
            # Paste the mouth frame onto the image
            display_img.paste(mouth_frame, (x1, y1), mask)
        
        return display_img
    
    def has_image(self):
        """Check if an image is loaded"""
        return self.processed_image is not None
    
    def get_current_frame(self, mouth_openness=0):
        """Get the current frame with mouth animation"""
        if not self.processed_image:
            return None
            
        # Create a copy of the image for animation
        frame = self.processed_image.copy()
        
        # Get mouth region
        mouth_region = self.mouth_region
        if not mouth_region:
            return frame
            
        x1, y1, x2, y2 = mouth_region
        mouth_width = x2 - x1
        mouth_height = y2 - y1
        
        # Calculate the maximum mouth opening
        max_opening = mouth_height * 0.7  # 70% of mouth region height
        
        # Calculate actual opening based on mouth_openness (0-1)
        opening = int(max_opening * mouth_openness)
        
        if opening > 0:
            # Create a new mouth shape
            draw = ImageDraw.Draw(frame)
            
            # Calculate control points for natural lip curve
            center_x = (x1 + x2) / 2
            
            # Upper lip curve
            upper_y = y1 + mouth_height * 0.3
            upper_ctrl_y = upper_y - mouth_height * 0.1
            
            # Lower lip curve (adjusted by opening)
            lower_y = upper_y + opening
            lower_ctrl_y = lower_y + mouth_height * 0.1
            
            # Draw lips with natural curve
            # Upper lip
            upper_lip = [
                (x1, upper_y),  # Start
                (x1 + mouth_width * 0.25, upper_ctrl_y),  # Control point 1
                (center_x, upper_y - mouth_height * 0.1),  # Peak
                (x2 - mouth_width * 0.25, upper_ctrl_y),  # Control point 2
                (x2, upper_y)  # End
            ]
            
            # Lower lip
            lower_lip = [
                (x1, upper_y),  # Start
                (x1 + mouth_width * 0.25, lower_ctrl_y),  # Control point 1
                (center_x, lower_y + mouth_height * 0.1),  # Valley
                (x2 - mouth_width * 0.25, lower_ctrl_y),  # Control point 2
                (x2, upper_y)  # End
            ]
            
            # Draw mouth interior (dark color)
            draw.polygon(upper_lip + lower_lip[::-1], fill="#1a1b26")
            
            # Draw lip outlines
            draw.line(upper_lip, fill="#d35f70", width=2, joint="curve")  # Upper lip
            draw.line(lower_lip, fill="#d35f70", width=2, joint="curve")  # Lower lip
        
        return frame
    
    def get_mouth_region(self):
        """Get the current mouth region coordinates"""
        return self.mouth_region

    def _calculate_mouth_region(self, image):
        """Calculate the mouth region coordinates based on image dimensions"""
        width = image.width
        height = image.height
        
        # Calculate mouth region - positioned at the avatar's actual mouth
        mouth_width = width // 3  # 1/3 of image width for more natural proportion
        mouth_height = height // 15  # Smaller height for more precise lip sync
        
        # Center the mouth region horizontally
        x1 = (width - mouth_width) // 2
        x2 = x1 + mouth_width
        
        # Position vertically at 58% from top for upper lip (adjusted based on the avatar image)
        upper_lip_y = int(height * 0.58)
        y1 = upper_lip_y
        y2 = y1 + mouth_height
        
        return (x1, y1, x2, y2)

    def get_image(self):
        """Get the current processed image"""
        return self.processed_image
        
    def clear(self):
        """Clear all image resources"""
        try:
            # Clear image data
            self.original_image = None
            self.processed_image = None
            self.mouth_region = None
            self.detected_lips = None
            self.mouth_frames = []
            
            # Clear any other stored data
            if hasattr(self, 'photo_image'):
                self.photo_image = None
                
        except Exception as e:
            print(f"Error clearing image resources: {e}")