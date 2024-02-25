themes_list = {
    1 : "themes/Cozy Fireplace.jpg",
    2 : "themes/Crowded Market.jpg",
    3 : "themes/Fall Wonderland.jpg",
    4 : "themes/Dreamy Clouds.jpg",
    5 : "themes/Quiet Coffee.png",
    6 : "themes/Seoul Sunrise.jpg",
    7 : "themes/Sakura River.jpg",
    8 : "themes/Aesthetic Night.jpg",
    9 : "themes/Desolate Winter.jpg",
    10 : "themes/Dark Academia.jpg",
    11 : "themes/Water Paint.jpg",
    12 : "themes/Minimal Black.jpg"
}

themes_accent = {
    "themes/Aesthetic Night.jpg": "#010D27",
    "themes/Cozy Fireplace.jpg": "#140200",
    "themes/Crowded Market.jpg": "#010101",
    "themes/Dark Academia.jpg": "#747A7A",
    "themes/Desolate Winter.jpg": "#999999",
    "themes/Dreamy Clouds.jpg": "#3D598B",
    "themes/Fall Wonderland.jpg": "#6D2C10",
    "themes/Minimal Black.jpg": "#000000",
    "themes/Quiet Coffee.png": "#61758B",
    "themes/Sakura River.jpg": "#8F8F91",
    "themes/Seoul Sunrise.jpg": "#5C4F85",
    "themes/Water Paint.jpg": "#978585"
}

def read_data():
    with open("config.txt", "r") as f:
        items = f.readlines()
    return items[0].split()

def write_data(items):
    with open("config.txt", "w") as f:
        f.truncate(0)
        f.writelines(items)

# write_data(["25 ", "5 ", "10 ", "0 ", "0 ", "7 "])
