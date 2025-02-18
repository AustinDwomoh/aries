from PIL import Image, ImageDraw, ImageFont

def generate_table_image(match_data, output_path="table.png"):
    teams = list(match_data["table"].keys())
    columns = ["TEAM", "P", "W", "D", "L", "GS", "GA"]
    row_height = 50
    col_widths = [200, 50, 50, 50, 50, 50, 50]
    font_size = 30
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    img_width = sum(col_widths)
    img_height = (len(teams) + 1) * row_height + 20
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    
    x = 10
    y = 10
    for i, col in enumerate(columns):
        draw.text((x, y), col, fill="black", font=font)
        x += col_widths[i]
    
    y += row_height
    for team, stats in match_data["table"].items():
        x = 10
        draw.text((x, y), team, fill="black", font=font)
        x += col_widths[0]
        
        for key in ["matches_played", "wins", "draws", "losses", "goals_scored", "goals_conceded"]:
            draw.text((x, y), str(stats[key]), fill="black", font=font)
            x += col_widths[1]
        
        y += row_height
    
    image.save(output_path)
    print(f"Table image saved as {output_path}")

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
