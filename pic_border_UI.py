from PIL import Image, ImageDraw, ImageFont
import os
import json

class BorderPresetManager:
    def __init__(self):
        self.presets = self.load_presets()

    def load_presets(self):
        try:
            with open('presets.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "Signature+LOGO": {
                    "border_width": "50",
                    "extra_bottom_height": "200",
                    "font_size": "72",
                    "signature_text": "Enter Your Name Here",
                    "font_path": "c:\\WINDOWS\\Fonts\\GREATVIBES-REGULAR.TTF",
                    "include_signature": True,
                    "logo_size": [
                        345,
                        150
                    ],
                    "signature_options": {
                        "first_half_text": "",
                        "first_half_font_size": "",
                        "second_half_text": "",
                        "second_half_font_size": "",
                        "first_half_color": "blue",
                        "second_half_color": "white",
                        "modify_signature": False
                    }
                },
                "LOGO": {
                    "border_width": "50",
                    "extra_bottom_height": "200",
                    "font_size": "72",
                    "signature_text": "",
                    "font_path": "c:\\WINDOWS\\Fonts\\GREATVIBES-REGULAR.TTF",
                    "include_signature": False,
                    "logo_size": [
                        345,
                        150
                    ],
                    "signature_options": {
                        "first_half_text": "",
                        "first_half_font_size": "",
                        "second_half_text": "",
                        "second_half_font_size": "",
                        "first_half_color": "",
                        "second_half_color": "",
                        "modify_signature": False
                    }
                },
                "Signature": {
                    "border_width": "50",
                    "extra_bottom_height": "150",
                    "font_size": "72",
                    "signature_text": "",
                    "font_path": "c:\\WINDOWS\\Fonts\\BowlbyOneSC-Regular.ttf",
                    "include_signature": True,
                    "logo_size": [
                        0,
                        0
                    ],
                    "signature_options": {
                        "first_half_text": "YOYO",
                        "first_half_font_size": "60",
                        "second_half_text": "LUMI",
                        "second_half_font_size": "72",
                        "first_half_color": "#cdf9ff",
                        "second_half_color": "#459dcc",
                        "modify_signature": True
                    }
                }
            }

    def save_presets(self):
        with open('presets.json', 'w') as f:
            json.dump(self.presets, f, indent=4)

    def apply_preset(self, preset_name, image_path, logo_path, output_folder, delete_input=False):
        preset = self.presets[preset_name]
        # Open the main image
        main_img = Image.open(image_path)

        # Extract preset parameters and ensure they are integers
        border_width = int(preset["border_width"])
        extra_bottom_height = int(preset["extra_bottom_height"])
        logo_size = tuple(map(int, preset["logo_size"]))
        font_size = int(preset["font_size"])
        signature_text = preset["signature_text"]
        font_path = preset["font_path"]
        include_signature = preset["include_signature"]

        # Create new image with white background and asymmetric border
        new_width = main_img.width + (border_width * 2)
        new_height = main_img.height + border_width + (border_width + extra_bottom_height)
        bordered_img = Image.new(main_img.mode, (new_width, new_height), 'white')

        # Paste main image onto white background
        bordered_img.paste(main_img, (border_width, border_width))

        # Update main_img and dimensions for logo/signature placement
        main_img = bordered_img
        main_width, main_height = main_img.size

        # Open the logo if logo size is not zero
        if logo_size != (0, 0):
            logo = Image.open(logo_path)
            logo = logo.resize(logo_size)
            # Calculate logo position (left side in bottom border area for preset1, center for preset2)
            if include_signature:
                logo_position = (border_width + 20, main_height - extra_bottom_height)
            else:
                logo_position = ((main_width - logo.width) // 2, main_height - extra_bottom_height)

            # Handle logo transparency
            if logo.mode == 'RGBA':
                logo_rgba = logo.convert('RGBA')
                mask = logo_rgba.split()[3]  # Get alpha channel
                main_img.paste(logo, logo_position, mask)
            else:
                main_img.paste(logo, logo_position)

        if include_signature:
            # Draw a customizable signature
            draw = ImageDraw.Draw(main_img)
            signature_options = preset.get("signature_options", {})
            modify_signature = signature_options.get("modify_signature", True)
            if modify_signature:
                first_half_text = signature_options.get("first_half_text", "")
                first_half_color = signature_options.get("first_half_color", "black")
                first_half_font_size = int(signature_options.get("first_half_font_size", font_size))
                second_half_text = signature_options.get("second_half_text", "")
                second_half_color = signature_options.get("second_half_color", "black")
                second_half_font_size = int(signature_options.get("second_half_font_size", font_size))

                # Load fonts
                first_half_font = ImageFont.truetype(font_path, first_half_font_size)
                second_half_font = ImageFont.truetype(font_path, second_half_font_size)

                # Calculate positions
                first_half_bbox = draw.textbbox((0, 0), first_half_text, font=first_half_font)
                second_half_bbox = draw.textbbox((0, 0), second_half_text, font=second_half_font)
                total_width = (first_half_bbox[2] - first_half_bbox[0]) + (second_half_bbox[2] - second_half_bbox[0])
                max_height = max(first_half_bbox[3], second_half_bbox[3])
                first_half_position = ((main_width - total_width) // 2, main_height - extra_bottom_height - border_width // 2 + (extra_bottom_height - max_height) // 2 + (max_height - first_half_bbox[3]))
                second_half_position = (first_half_position[0] + (first_half_bbox[2] - first_half_bbox[0]), main_height - extra_bottom_height - border_width // 2 + (extra_bottom_height - max_height) // 2 + (max_height - second_half_bbox[3]))

                # Draw texts
                draw.text(first_half_position, first_half_text, fill=first_half_color, font=first_half_font)
                draw.text(second_half_position, second_half_text, fill=second_half_color, font=second_half_font)
            else:
                # Draw the signature text without modification
                font = ImageFont.truetype(font_path, font_size)
                bbox = draw.textbbox((0, 0), signature_text, font=font)
                text_width = bbox[2] - bbox[0]
                signature_position = ((main_width - text_width) // 2, main_height - extra_bottom_height + (extra_bottom_height - bbox[3]) // 2)
                draw.text(signature_position, signature_text, fill="black", font=font)

        # Save the result in the specified output folder
        base_name = os.path.basename(image_path)
        output_path = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}_preset_{preset_name}{os.path.splitext(base_name)[1]}")
        main_img.save(output_path)
        os.remove(image_path) if delete_input else None
