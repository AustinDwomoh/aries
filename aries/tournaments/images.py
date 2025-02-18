from PIL import Image, ImageDraw, ImageFont
from tabulate import tabulate

def generate_table_image(match_data, output_path="table.png"):
    headers = ["Team", "Wins", "Losses", "Points"]
    table_data = [[team, stats["wins"], stats["losses"], stats["points"]] for team, stats in match_data["table"].items()]
    
    # Generate table string using tabulate
    table_str = tabulate(table_data, headers=headers, tablefmt="grid")

    # Create an image
    img_width = 800
    img_height = 600
    bg_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text
    
    image = Image.new("RGB", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Use Arial font if available
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font

    # Draw the tabulated text on the image
    y_offset = 50  # Start position
    for line in table_str.split("\n"):
        draw.text((50, y_offset), line, fill=text_color, font=font)
        y_offset += 30  # Move down for next line

    # Save the image
    image.save(output_path)
    print(f"Tournament table saved as {output_path}")

def generate_round_images(match_data, output_dir="rounds/"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    font_size = 20
    row_height = 100
    img_width = 600
    col_widths = [200, 100, 200]
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    for round_number, round_data in enumerate(match_data["rounds"], start=1):
        img_height = len(round_data["matches"]) * row_height + 50
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)
        
        y = 10
        draw.text((img_width // 2 - 50, y), f"Round {round_number}", fill="black", font=font)
        y += 40
        
        for match in round_data["matches"]:
            x = 10
            draw.text((x, y), match["team_a"], fill="black", font=font)
            x += col_widths[0]
            
            score = f"{match['team_a_goals']} - {match['team_b_goals']}" if match['team_a_goals'] is not None else "-"
            draw.text((x, y), score, fill="black", font=font)
            x += col_widths[1]
            
            draw.text((x, y), match["team_b"], fill="black", font=font)
            y += row_height
        
        output_path = os.path.join(output_dir, f"round_{round_number}.png")
        image.save(output_path)
        print(f"Round {round_number} image saved as {output_path}")
