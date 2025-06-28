# basic colors
white = (255,255,255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (150, 150, 255)
green = (0, 255, 0)
'''
Files for games will follow this convention
<game name>_dscr.csv = the game description Header and Body
<game name>_intro.csv = the rules for a picture game
<game_name>_bkg.jpg = full screen background for game
<game_name>_picture.csv = list of pairs of matching pictures
<game_name>_qna.csv = Text games [Question, Correct, Wrong A, Wrong B]
free_cash background = free_donate.jpg
final_score = finalscore.jpg
'''
nt_path = 'graphics/'
pi_path = 'C:/Users/kpnef/PIO-Arduino/Windows_Game/graphics/'
file_path = 'graphics/'
pi_db = '/home/pi/game_web/game/db.sqlite3'
nt_db = 'db.sqlite3'

lists_path = '/home/pi/Dol_class/'
# Path and run command for server
web_server = '/home/pi/game_web/game/manage.py runserver'
some_file = file_path + 'somefile'
# used by choose_game to set up questions, answers and backgrounds
# dictionary button#: name
game_names = {1:'dolphin', 5:'bonehenge', 3:'stupid'}
# dict. of the game types these names will also be used to load files
# like dolphin_intro.csv, dolphin_picture.csv
game_types = {'dolphin':'picture', 'bonehenge':'text','stupid':'text'}
# award words for 5 right or 4 right
small_prize = ('Bottlenose', 'Dwarf', 'Porpoise', 'Pyygmy', 'Spotted')
big_prize  = ('Blue', 'Fin', 'Humpback', 'Minke', 'Right')

