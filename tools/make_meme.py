from PIL import Image, ImageDraw, ImageFont
import math

def make_meme():
    # Create image
    img = Image.new('RGB', (1024, 1024))
    draw = ImageDraw.Draw(img)
    
    # 1. Sky Gradient (1x256 stretched to 1024x1024)
    # Colors: Deep Purple #2b1055 -> Magenta #ff2d78 -> Orange #ff7a18 -> Gold #ffd700
    grad = Image.new('RGB', (1, 256))
    colors = [
        (43, 16, 85),    # Top: Deep Purple
        (255, 45, 120),  # Magenta
        (255, 122, 24),  # Orange
        (255, 215, 0)    # Horizon: Gold
    ]
    for y in range(256):
        # Interpolate colors
        if y < 256 // 3:
            # Purple to Magenta
            t = y / (256 // 3)
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * t)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * t)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * t)
        elif y < 2 * (256 // 3):
            # Magenta to Orange
            t = (y - 256 // 3) / (256 // 3)
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * t)
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * t)
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * t)
        else:
            # Orange to Gold
            t = (y - 2 * (256 // 3)) / (256 - 2 * (256 // 3))
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * t)
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * t)
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * t)
        grad.putpixel((0, y), (r, g, b))
    
    # Stretch gradient
    sky = grad.resize((1024, 1024))
    img.paste(sky, (0, 0))
    
    # 2. Synthwave Sun
    sun_radius = 200
    sun_center_x = 512
    sun_center_y = 500 # Low on horizon
    
    # Draw Sun
    draw.ellipse([sun_center_x - sun_radius, sun_center_y - sun_radius, 
                  sun_center_x + sun_radius, sun_center_y + sun_radius], 
                 fill=(255, 230, 150)) # Pale gold
    
    # Cut horizontal slats in lower half
    # We will draw horizontal lines of the background color or just overwrite with sky if we were doing it differently, 
    # but since we are drawing on the image, we need to be careful not to erase the sky.
    # Actually, the sun is drawn on top of the sky. The slats are "cut" i.e. transparent or sky-colored.
    # Since PIL draws on top, I will simulate slats by drawing horizontal strips of the sky color 
    # or simply not drawing the sun there. 
    # Easier approach: Draw the sun, then draw horizontal lines of the *local sky color*? No, that's hard.
    # Better approach: Bezier/Alpha compositing is complex in basic PIL.
    # Alternative: Draw the sun, then erase parts of it with the background. 
    # Since the background is a gradient, we can sample it.
    
    # Let's iterate y from center to bottom of sun
    for y in range(sun_center_y, sun_center_y + sun_radius):
        # Calculate half-width of sun at this y
        dy = y - sun_center_y
        if dy > sun_radius:
            break
        half_w = int(math.sqrt(sun_radius**2 - dy**2))
        
        # Pattern for slats: alternating cut and solid
        # Let's say slats are 10px wide, gaps 15px wide, starting from bottom up? Or top of the lower half?
        # "horizontal slats cut across its lower half"
        # Usually synthwave suns have slats that increase in width towards the bottom.
        # Let's just do uniform slats for simplicity, or increasing.
        # Let's do increasing width of the gap (sky visible) or solid?
        # "slats cut across" implies the sun is interrupted by horizontal stripes of sky.
        
        # Sample sky color at this y (and x roughly center, but sky is uniform horizontally in terms of gradient? No, it's vertical gradient)
        # So all x at same y have same color in the gradient.
        sky_color = sky.getpixel((0, y))
        
        # Define slat pattern
        # Let's say we cut a line if (y % 20) is between 10 and 20? 
        # Let's make the slats thicker towards the bottom.
        t = y / (sun_center_y + sun_radius) # 0.5 to 1.0 in this range
        slat_thickness = int(5 + 15 * t) # 5px to 20px
        gap_thickness = int(10 + 10 * (1-t)) # variable gap? Let's keep gap somewhat constant or decreasing?
        # Actually, standard synthwave sun: slats are horizontal bars of background color.
        # Let's just draw horizontal lines of sky_color over the sun.
        
        if (y % 20) < 10: # Every other 10px block? 
             # Let's do: cut if y is in certain ranges.
             # Let's vary the cut thickness.
             cut_height = int(2 + 8 * t) # Thicker cuts at bottom
             # We just draw a line of sky_color at height cut_height? 
             # No, we want to "cut" the sun. 
             # So we draw a horizontal strip of sky_color.
             start_x = sun_center_x - half_w
             end_x = sun_center_x + half_w
             draw.line([(start_x, y), (end_x, y)], fill=sky_color, width=cut_height)

    # 3. Skyline Silhouette
    skyline_color = (30, 10, 50) # Dark purple
    horizon_y = 650
    
    # Draw a generic skyline
    draw.rectangle([0, horizon_y, 1024, 1024], fill=skyline_color)
    
    # Add buildings (rectangles with top jagged or simple)
    # Just a few rectangles of varying heights extending above horizon_y
    buildings = [
        (0, 600, 80, horizon_y),
        (80, 620, 150, horizon_y),
        (150, 580, 220, horizon_y),
        (220, 610, 300, horizon_y),
        (300, 590, 380, horizon_y),
        (380, 630, 450, horizon_y),
        # Gap for road/perspective center? 
        (600, 620, 680, horizon_y),
        (680, 580, 750, horizon_y),
        (750, 610, 820, horizon_y),
        (820, 590, 900, horizon_y),
        (900, 620, 1024, horizon_y)
    ]
    for x1, y1, x2, y2 in buildings:
        draw.rectangle([x1, y1, x2, y2], fill=skyline_color)

    # Tiny lit windows
    window_color = (255, 200, 50)
    # Deterministic pattern for windows
    import random
    rand = random.Random(42) # Fixed seed for deterministic "randomness"? 
    # Wait, "no randomness". So I must generate windows deterministically.
    
    # Let's use a simple hash or fixed values.
    window_positions = []
    for i, (x1, y1, x2, y2) in enumerate(buildings):
        # Add few windows per building
        for j in range(3):
            wx = x1 + 10 + (j * 15)
            wy = y1 + 10 + (j * 20)
            if wx < x2 - 10 and wy < y2 - 10:
                draw.rectangle([wx, wy, wx+4, wy+4], fill=window_color)

    # 4. Palm Trees
    trunk_color = (20, 10, 30)
    
    def draw_palm_tree(x_base, y_base, direction):
        # Trunk: curved lines
        # Use a quadratic bezier or just a thick line that curves
        # Simple approach: draw a thick line with offset
        points = []
        height = 150
        for i in range(height):
            t = i / height
            # Curve: x offset = direction * t^2 * 50
            x = int(x_base + direction * (t ** 1.5) * 80)
            y = int(y_base - i)
            points.append((x, y))
        
        # Draw trunk as a thick line
        # PIL line with width
        draw.line(points, fill=trunk_color, width=10)
        
        # Fronds: arcs/lines radiating from top
        top_x, top_y = points[-1]
        num_fronds = 7
        for j in range(num_fronds):
            angle = -90 + (j - num_fronds // 2) * 25
            rad = math.radians(angle)
            length = 60
            end_x = int(top_x + math.cos(rad) * length)
            end_y = int(top_y + math.sin(rad) * length)
            # Curved frond: use arc or just line? 
            # "fronds as arcs/lines"
            # Use a quadratic curve by drawing multiple segments or just a line.
            # Let's use a line for width, and maybe a slight arc by offsetting midpoint.
            mid_x = (top_x + end_x) // 2
            mid_y = (top_y + end_y) // 2 - 10 # Lift up
            draw.line([(top_x, top_y), (mid_x, mid_y), (end_x, end_y)], fill=trunk_color, width=4, joint="curve")

    # Left palm framing left
    draw_palm_tree(50, 700, 1) # Curve right? No, framing means leaning out or in?
    # Usually framing means they are on the edges. Let's curve them slightly inwards.
    # Left tree at x=50, curving right (positive x)
    # Right tree at x=950, curving left (negative x)
    
    # Redo left tree
    draw.line([(50, 700), (70, 650), (80, 600)], fill=trunk_color, width=12) 
    draw_frond_base = (80, 600)
    for j in range(7):
        angle = -90 + (j - 3) * 30
        rad = math.radians(angle)
        end_x = int(draw_frond_base[0] + math.cos(rad) * 70)
        end_y = int(draw_frond_base[1] + math.sin(rad) * 70)
        mid_x = (draw_frond_base[0] + end_x) // 2
        mid_y = (draw_frond_base[1] + end_y) // 2 - 15
        draw.line([(draw_frond_base[0], draw_frond_base[1]), (mid_x, mid_y), (end_x, end_y)], fill=trunk_color, width=5, joint="curve")

    # Right tree
    draw.line([(950, 700), (930, 650), (920, 600)], fill=trunk_color, width=12)
    draw_frond_base_r = (920, 600)
    for j in range(7):
        angle = -90 + (j - 3) * 30 + 180 # Flipping direction? 
        # Actually, just mirror the logic or angles.
        # Let's just use same frond spread, it looks fine.
        angle = -90 + (j - 3) * 30
        rad = math.radians(angle)
        end_x = int(draw_frond_base_r[0] + math.cos(rad) * 70)
        end_y = int(draw_frond_base_r[1] + math.sin(rad) * 70)
        mid_x = (draw_frond_base_r[0] + end_x) // 2
        mid_y = (draw_frond_base_r[1] + end_y) // 2 - 15
        draw.line([(draw_frond_base_r[0], draw_frond_base_r[1]), (mid_x, mid_y), (end_x, end_y)], fill=trunk_color, width=5, joint="curve")

    # 5. Road
    road_color = (15, 15, 15) # Black/Dark
    # Trapezoid at bottom
    # Vanishing point near center horizon (512, 650)
    # Bottom edge full width
    draw.polygon([
        (0, 1024),
        (1024, 1024),
        (512 + 50, 650),
        (512 - 50, 650)
    ], fill=road_color)

    # Dashed centre line
    dash_color = (255, 255, 255)
    # Line from (512, 650) to (512, 1024)
    # Dash every 50 pixels
    for y in range(650, 830, 50):
        # Width of dash increases towards bottom? 
        # Let's keep it simple constant width for now, or tweak.
        draw.line([(512 - 2, y), (512 + 2, y + 25)], fill=dash_color, width=4)

    # 6. make.fun Ghost
    # Large, centre-right above the road: white ghost, thick black outline,
    # two black four-pointed sparkle eyes, round hand holding a magenta coin
    # with a white star. Built as solid shapes (no self-intersecting polygon):
    # a black silhouette 7 px larger behind, the white body on top.
    gx, gy = 750, 450          # ghost centre
    gw, gh = 150, 190          # body width / height
    half_w, half_h = gw // 2, gh // 2
    top = gy - half_h
    bottom = gy + half_h
    pad = 7
    # Black silhouette behind (dome + sides + scalloped hem, all expanded).
    draw.ellipse([gx - half_w - pad, top - pad, gx + half_w + pad, gy + half_h // 2 + pad], fill=(0, 0, 0))
    draw.rectangle([gx - half_w - pad, gy - pad, gx + half_w + pad, bottom + pad], fill=(0, 0, 0))
    n_sc = 4
    sc_r = gw // (2 * n_sc)
    for i in range(n_sc):
        cx = gx - half_w + sc_r + i * 2 * sc_r
        draw.ellipse([cx - sc_r - pad, bottom - sc_r - pad, cx + sc_r + pad, bottom + sc_r + pad], fill=(0, 0, 0))
    # White body on top.
    draw.ellipse([gx - half_w, top, gx + half_w, gy + half_h // 2], fill=(255, 255, 255))
    draw.rectangle([gx - half_w, gy, gx + half_w, bottom], fill=(255, 255, 255))
    for i in range(n_sc):
        cx = gx - half_w + sc_r + i * 2 * sc_r
        draw.ellipse([cx - sc_r, bottom - sc_r, cx + sc_r, bottom + sc_r], fill=(255, 255, 255))

    # Eyes: two black four-pointed sparkle eyes.
    def draw_sparkle_eyes(c_x, c_y, size):
        pts = [
            (c_x, c_y - size),
            (c_x + size // 2, c_y),
            (c_x, c_y + size),
            (c_x - size // 2, c_y),
        ]
        draw.polygon(pts, fill=(0, 0, 0))

    draw_sparkle_eyes(gx - 28, gy - 25, 14)
    draw_sparkle_eyes(gx + 28, gy - 25, 14)

    # Hand (white circle, black outline) at the body's right edge, holding the coin.
    hand_x, hand_y = gx + half_w + 6, gy + 55
    draw.ellipse([hand_x - 14, hand_y - 14, hand_x + 14, hand_y + 14], fill=(255, 255, 255), outline=(0, 0, 0), width=3)

    # Coin: magenta disc with a white five-pointed star, clear of the body.
    coin_x, coin_y = hand_x + 38, hand_y
    draw.ellipse([coin_x - 26, coin_y - 26, coin_x + 26, coin_y + 26], fill=(255, 0, 127), outline=(0, 0, 0), width=3)

    def draw_star(c_x, c_y, outer_r, inner_r, points):
        star_points = []
        for i in range(points * 2):
            angle = math.pi * i / points - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            star_points.append((c_x + r * math.cos(angle), c_y + r * math.sin(angle)))
        draw.polygon(star_points, fill=(255, 255, 255))

    draw_star(coin_x, coin_y, 16, 7, 5)

    # 7. Text
    font_path = "DejaVuSans-Bold.ttf"
    # Check if path exists? The prompt says use /usr/share/fonts/truetype/dejavu/
    # But to be safe, I'll try to load from the specific path or fallback.
    # The prompt explicitly says: "Caption text in DejaVu Sans Bold (/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf)"
    
    try:
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        # Fallback if font not found (should not happen in standard Linux env)
        font_small = ImageFont.load_default()
        font_big = ImageFont.load_default()

    text_color_fill = (255, 255, 255)
    text_color_stroke = (0, 0, 0)
    stroke_width = 4

    def draw_stroke_text(draw_obj, xy, text, font, fill, stroke_fill, stroke_width):
        x, y = xy
        # Calculate offset positions
        for dx in range(-stroke_width, stroke_width + 1, 2):
            for dy in range(-stroke_width, stroke_width + 1, 2):
                # Simplified: draw text with offset
                if dx != 0 or dy != 0:
                    draw_obj.text((x+dx, y+dy), text, font=font, fill=stroke_fill)
        draw_obj.text((x, y), text, font=font, fill=fill)
    
    # Centering helper
    def get_text_size(text, font):
        # PIL 9+ has length? No, use bbox
        bbox = draw.textbbox((0,0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Top Text
    top_text_1 = "13 YEARS WAITING"  # tuned
    top_text_2 = "FOR GTA 6"
    
    w1, h1 = get_text_size(top_text_1, font_small)
    w2, h2 = get_text_size(top_text_2, font_big)
    
    x1 = 512 - w1 // 2
    y1 = 50
    
    x2 = 512 - w2 // 2
    y2 = y1 + h1 + 10
    
    draw_stroke_text(draw, (x1, y1), top_text_1, font_small, text_color_fill, text_color_stroke, stroke_width)
    draw_stroke_text(draw, (x2, y2), top_text_2, font_big, text_color_fill, text_color_stroke, stroke_width)

    # Bottom Text
    bot_text_1 = "MY AGENT GOT PAID"
    bot_text_2 = "ON MAKE.FUN"
    
    w3, h3 = get_text_size(bot_text_1, font_small)
    w4, h4 = get_text_size(bot_text_2, font_big)
    
    # Position from bottom
    y4 = 1024 - 50 - h4
    x4 = 512 - w4 // 2
    
    y3 = y4 - h3 - 10
    x3 = 512 - w3 // 2
    
    draw_stroke_text(draw, (x3, y3), bot_text_1, font_small, text_color_fill, text_color_stroke, stroke_width)
    draw_stroke_text(draw, (x4, y4), bot_text_2, font_big, text_color_fill, text_color_stroke, stroke_width)

    # Save
    img.save("meme.png")
    
    # Print size
    print(f"Saved meme.png: {img.size[0]}x{img.size[1]}")

if __name__ == "__main__":
    make_meme()
