from PIL import Image, ImageDraw
import io
from rembg import remove

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.mouth_region = None
        self.mouth_frames = []
    
    def load_image(self, image_path):
        """Load and process an image"""
        try:
            # Load the image
            img = Image.open(image_path)
            self.original_image = img.copy()
            self.processed_image = img.copy()
            
            # Define mouth region
            self._define_mouth_region()
            
            # Generate mouth frames
            self.generate_mouth_frames()
            
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def remove_background(self):
        """Remove background from the current image"""
        if self.original_image:
            try:
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                self.original_image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Remove background
                output = remove(img_byte_arr)
                
                # Convert back to PIL Image
                self.processed_image = Image.open(io.BytesIO(output))
                return True
            except Exception as e:
                print(f"Error removing background: {e}")
                return False
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
            self._update_mouth_region(new_width, new_height, pad_x, pad_y)
            
            return True
        return False
    
    def _define_mouth_region(self):
        """Define the mouth region in the image"""
        if self.processed_image:
            width, height = self.processed_image.size
            
            # Calculate mouth position relative to face features
            mouth_x_center = width * 0.5
            mouth_y_position = height * 0.68  # Moved down to better match the avatar's mouth position
            
            # Adjust mouth size relative to image size
            mouth_width = width * 0.12  # Slightly smaller width
            mouth_height = height * 0.04  # Slightly smaller height
            
            # Store the mouth region coordinates
            self.mouth_region = (
                int(mouth_x_center - mouth_width/2),
                int(mouth_y_position - mouth_height/2),
                int(mouth_x_center + mouth_width/2),
                int(mouth_y_position + mouth_height/2)
            )
    
    def _update_mouth_region(self, width, height, pad_x=0, pad_y=0):
        """Update mouth region coordinates based on new image size and padding"""
        # Calculate mouth position relative to face features
        mouth_x_center = width * 0.5
        mouth_y_position = height * 0.68  # Moved down to better match the avatar's mouth position
        
        # Adjust mouth size relative to image size
        mouth_width = width * 0.12  # Slightly smaller width
        mouth_height = height * 0.04  # Slightly smaller height
        
        # Ensure mouth dimensions are at least 1 pixel
        mouth_width = max(1, mouth_width)
        mouth_height = max(1, mouth_height)
        
        # Add padding to the coordinates
        self.mouth_region = (
            int(pad_x + mouth_x_center - mouth_width/2),
            int(pad_y + mouth_y_position - mouth_height/2),
            int(pad_x + mouth_x_center + mouth_width/2),
            int(pad_y + mouth_y_position + mouth_height/2)
        )
        
        # Ensure mouth region is within image bounds
        if self.processed_image:
            img_width, img_height = self.processed_image.size
            x1, y1, x2, y2 = self.mouth_region
            
            # Adjust if mouth region is outside image bounds
            if x1 < 0:
                x2 += abs(x1)
                x1 = 0
            if y1 < 0:
                y2 += abs(y1)
                y1 = 0
            if x2 > img_width:
                x1 -= (x2 - img_width)
                x2 = img_width
            if y2 > img_height:
                y1 -= (y2 - img_height)
                y2 = img_height
            
            # Ensure mouth region has positive dimensions
            if x2 <= x1:
                x2 = x1 + 1
            if y2 <= y1:
                y2 = y1 + 1
            
            self.mouth_region = (x1, y1, x2, y2)
    
    def generate_mouth_frames(self):
        """Generate different mouth shapes for animation"""
        if not self.processed_image or not self.mouth_region:
            return
            
        x1, y1, x2, y2 = self.mouth_region
        mouth_width = x2 - x1
        mouth_height = y2 - y1
        
        # Create a series of mouth shapes with different openness levels
        num_frames = 8  # Number of different mouth positions
        self.mouth_frames = []
        
        for i in range(num_frames):
            # Create a transparent image for the mouth
            mouth_img = Image.new('RGBA', (mouth_width, mouth_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(mouth_img)
            
            # Calculate openness based on frame index
            openness = i / (num_frames - 1)
            
            # Extract lip color from the original image (approximate)
            lip_color = (208, 108, 103, 255)  # Pink-ish color for lips
            
            # Draw upper lip (fixed)
            upper_lip_height = int(mouth_height * 0.4)
            draw.ellipse((0, 0, mouth_width, upper_lip_height*2), fill=lip_color)
            
            # Draw lower lip with varying openness
            lower_lip_y = int(mouth_height * (0.5 + 0.25 * openness))
            lower_lip_height = int(mouth_height * 0.4)
            draw.ellipse((0, lower_lip_y-lower_lip_height, mouth_width, lower_lip_y+lower_lip_height), fill=lip_color)
            
            # If mouth is open, draw black inside
            if openness > 0.1:
                inner_mouth_height = int(mouth_height * openness * 0.8)
                inner_mouth_y = int(mouth_height * 0.5)
                inner_mouth_width = int(mouth_width * 0.8)
                inner_mouth_x = int(mouth_width * 0.1)
                
                draw.ellipse(
                    (inner_mouth_x, inner_mouth_y-inner_mouth_height//2, 
                     inner_mouth_x+inner_mouth_width, inner_mouth_y+inner_mouth_height//2), 
                    fill=(40, 40, 40, 255)
                )
            
            # Ensure the image has an alpha channel
            if mouth_img.mode != 'RGBA':
                mouth_img = mouth_img.convert('RGBA')
            
            self.mouth_frames.append(mouth_img)
    
    def get_mouth_frame(self, openness):
        """Get the appropriate mouth frame based on openness value"""
        if not self.mouth_frames:
            return None
            
        frame_index = min(len(self.mouth_frames)-1, int(openness * len(self.mouth_frames) / 30))
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
            
            # Ensure the mouth frame has the correct dimensions
            if mouth_frame.size != (x2 - x1, y2 - y1):
                # Resize the mouth frame to match the target region
                mouth_frame = mouth_frame.resize((x2 - x1, y2 - y1), Image.LANCZOS)
            
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