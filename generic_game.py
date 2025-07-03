#! /bin/sh



# IMPORTS START --------------------------------------------------
# makes extensive use of pygame to blit the screen

from random import randrange, shuffle, random, sample

# pull stuff from config file

from config import white, black, green, red, blue
from config import game_names, game_types
import db_module
use_db = False
from datetime import datetime



#from random import sample
from time import sleep, time
import sys, pygame, os
import multiprocessing



from pygame.locals import *

    
import pygame.font
import os
# code to use comma seperated values
import csv
# code to break up long strings
import textwrap
## IMPORTS END ----------------------------------------------------



# --------- Make all paths relative to script location ---------
import sys
# Set BASE_DIR for both development and PyInstaller bundle
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
gpath = os.path.join(BASE_DIR, 'graphics') + os.sep
lists_path = BASE_DIR + os.sep

# \\\\\\\\\\\\\\\\\ END VARIABLES AND CONSTANTS \\\\\\\\\\\\\\\\\\\\\\\\

# //////////////////  CLASSES ///////////////////////////////////////////
# !!!!!!!!!!!
class TextGame():
    def __init__(self, name, background, qu_ans, score,  reward= None):
        self.name = name
        self.background = background
        self.qu_ans = qu_ans # all of the questions and answers
        self.score = score
        self.reward = reward

        # make two lists of questions and answers
        self.just_a = []
        self.just_q = []
        for q_plus_a in self.qu_ans:
            self.just_q.append(q_plus_a[0])
            temp = []
            for i in range(1, len(q_plus_a)):
                temp.append(q_plus_a[i])
            self.just_a.append(temp)
            
            
            
        # leaving here our Game has the questions and answers
        # and a background
    # ============= end of Game class initialization ================   

    def take_turn(self):
        pass       
    
 # ============ end of Game class methods =============== 
 # ============ start PictGame class =========================
class PictGame():
    def __init__(self, name, background, qu_ans, score,  reward= None): 
        self.name = name
        self.background = background
        self.qu_ans = qu_ans # a list of tuples
        # like this (image 1a, image 1b)
        #           (image 2a, image 2b)
        self.score = score
        self.reward = reward
        # see if we can load them into pygame
        all_files = []
        count = 0
        self.all_picts = []
        for pair in range(0, len(self.qu_ans)):
            temp = []
            temp_surface = []
            temp.append(self.qu_ans[count][0])
            temp.append(self.qu_ans[count][1])
            temp_surface.append(pygame.image.load(os.path.join(gpath, self.qu_ans[count][0])).convert_alpha())
            temp_surface.append(pygame.image.load(os.path.join(gpath, self.qu_ans[count][1])).convert_alpha())
            count += 1
            self.all_picts.append(temp_surface)
            all_files.append(temp)
        # we now have a list of pairs of surfaces ready to be blitted
        
            


    
# !!!!!!!!!!!!!

# --- Utility to scale positions ---
def scale_pos(pos):
    return (int(pos[0] * scale_x), int(pos[1] * scale_y))

class ScreenObject():
    def __init__(self, location):
        self.location = location
    def blit_scr_obj(self, location, image):
        display.blit(image, scale_pos(location))


class GraphicObject(ScreenObject):
    def __init__(self, location, file_name):
        self.file_name = file_name
        super().__init__(location)
        # load and scale image
        img = pygame.image.load(file_name).convert_alpha()
        w = int(img.get_width() * scale_x)
        h = int(img.get_height() * scale_y)
        self.surface = pygame.transform.smoothscale(img, (w, h))


class TextObject(ScreenObject):
    def __init__(self, text, location, size, color, width=None, font='FreeSans'):
        self.text = text
        self.font = font
        self.size = size
        self.color = color
        self.width = width
        super().__init__(location)

    def parse_string(self):    
        # this handy util breaks up long lines for us
        lines_list = textwrap.wrap(self.text, self.width)        
        return lines_list 

    def font_process(self):
        global display
        x, y = scale_pos(self.location)
        # scale font size
        scaled_size = int(self.size * ((scale_x + scale_y) / 2))
        black = (0,0,0)
        d_shadow = int(3 * ((scale_x + scale_y) / 2))
        font = pygame.font.SysFont(self.font, scaled_size, True, False)
        render_message = font.render(self.text, True, self.color)
        if d_shadow:
            render_ds = font.render(self.text, True, black)
            render_ds_rect = render_message.get_rect()
        render_msg_rect = render_message.get_rect()
        render_msg_rect.center = (x, y)
        if d_shadow:
            render_ds_rect.center = (x + d_shadow, y + d_shadow)
            display.blit(render_ds, render_ds_rect)
        display.blit(render_message, render_msg_rect)
        
class SoundObject():
    def __init__(self, file, volume):
        self.file = file
        self.volume = volume
    def play_sound(self):
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.load(gpath + self.file)
        pygame.mixer.music.play()    
# \\\\\\\\\\\\\\\\\\\\ END CLASSES \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# /////////////// INITIALIZE RUN ONCE ////////////////////////////

def init():
    # --- Screen scaling setup ---
    global DESIGN_WIDTH, DESIGN_HEIGHT, scale_x, scale_y
    DESIGN_WIDTH = 1920
    DESIGN_HEIGHT = 1080

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.set_volume(1.0)
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    print(f"Detected screen size: width={screen_width}, height={screen_height}")
    scale_x = screen_width / DESIGN_WIDTH
    scale_y = screen_height / DESIGN_HEIGHT
    global display
    # for developement uncomment the line below
    #display = pygame.display.set_mode((1920,1080))
    # for autostart to work properly uncomment the line below
    display = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(1)

    # Center points in design coordinates
    global image_centerx
    global image_centery
    image_centerx = DESIGN_WIDTH // 2
    image_centery = DESIGN_HEIGHT // 2
    global small_index
    small_index = 0
    global big_index
    big_index = 0

    # make some arrow objects (design coordinates)
    global arrow1
    arrow1 = ScreenObject((15, 890))
    global arrow2
    arrow2 = ScreenObject((452, 890))
    global arrow3
    arrow3 = ScreenObject((895, 890))
    global arrow4
    arrow4 = ScreenObject((1337, 890))
    global arrow5
    arrow5 = ScreenObject((1775, 890))



    # arrows
    b_arro = gpath + 'blue_arrow.png'
    # glows
    g_gl = gpath + 'g-glow.png'
    r_gl = gpath + 'r-glow.png'
    gr_gl = gpath + 'gray-glow.png'
    # path to sounds
    awefile = gpath + 'Awe.mp3'
    yayfile = gpath + 'Yay.mp3'
    global yay
    yay = SoundObject('Yay.mp3', .3)
    
    # these guys are shared by all games
    global blue_arrow
    blue_arrow = pygame.image.load(b_arro).convert_alpha()
    global green_glow
    green_glow = pygame.image.load(g_gl).convert_alpha()
    global red_glow
    red_glow = pygame.image.load(r_gl).convert_alpha()
    global gray_glow
    gray_glow = pygame.image.load(gr_gl).convert_alpha()
    # text responses to right and wrong answers
    global correct
    correct = get_file('right_resp.csv', 1)[0]
    global wrong
    wrong = get_file('wrong_resp.csv', 1)[0]
#\\\\\\\\\\\\\\\\\\\ INITIALIZE \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# Modern CSV reader utility: skips header, returns list of lists with up to col_count columns
def get_file(list_file, col_count):
    list_file = lists_path + list_file
    try:
        with open(list_file, newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            cvs_list = []
            for i, row in enumerate(csv_reader):
                if i == 0:
                    continue  # skip header
                rowlist = row[:col_count]
                cvs_list.append(rowlist)
            return [cvs_list]
    except FileNotFoundError:
        print(f'File not found: {list_file}')
        return [[]]
        





def btn_proc(_):
    # Use mouse input for all user interactions, scaling mouse positions
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Ctrl+Q or ESC to quit for debugging
                if (event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL)) or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Ctrl+E to launch CSV editor
                if (event.key == pygame.K_e and (event.mod & pygame.KMOD_CTRL)):
                    # Minimize pygame window, run edit_csv.py, then exit main program
                    pygame.display.iconify()
                    import subprocess
                    import sys as _sys
                    import os as _os
                    python_exe = _sys.executable
                    editor_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'edit_csv.py')
                    subprocess.Popen([python_exe, editor_path])
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Scale mouse position to design coordinates
                x = x / scale_x
                y = y / scale_y
                # For game selection: left (1), right (5), center (3)
                if y > 350 and y < 900:
                    if x < 800:
                        return 1  # left
                    elif x > 1200:
                        return 5  # right
                    else:
                        return 3  # center (if used)
                # For answer selection: 3 or 5 answers horizontally
                if y > 500 and y < 800:
                    if x < 500:
                        return 1
                    elif x < 1100:
                        return 2
                    elif x < 1700:
                        return 3
                    elif x < 2300:
                        return 4
                    else:
                        return 5


# Place arrows and blit
    if  '1' in style:
        ScreenObject.blit_scr_obj(arrow1, arrow1.location, blue_arrow)
    if  '2' in style:
        ScreenObject.blit_scr_obj(arrow2, arrow2.location, blue_arrow)
    if  '3' in style:
        ScreenObject.blit_scr_obj(arrow3, arrow3.location, blue_arrow)
    if  '4' in style:
        ScreenObject.blit_scr_obj(arrow4, arrow4.location, blue_arrow)
    if  '5' in style:
        ScreenObject.blit_scr_obj(arrow5, arrow5.location, blue_arrow)

# gets a list of intro statements and puts them on screen
def picture_intro(curr_game):
    button_list = [0,0,0,0,0,0,0]

    # put up the game intro
    # splice the name of the game to _intro.csv to load file
    intro = get_file(curr_game.name + '_intro.csv', 1)[0]
    bkg = ScreenObject([0,0])
    ScreenObject.blit_scr_obj(bkg, bkg.location, curr_game.background)
    text_y = 400
    for i in range(0, len(intro)):
        intro_display(intro[i], text_y)
        text_y += 70
        pygame.display.flip()
        sleep(1)
    sleep(4)

def intro_display(intro_line, y):
    message = TextObject(str(intro_line[0]), [image_centerx, y], 60, white )
    TextObject.font_process(message)


def score_process(curr_game, right):
    f_size = 80
    if right:
        curr_game.score[0] += 1
        turn_resp = str(correct[randrange(len(correct))][0])
        resp_msg = TextObject(turn_resp, (900, 700), f_size, white)
    else:
        curr_game.score[1] += 1
        turn_resp = str(wrong[randrange(len(wrong))][0])
        resp_msg = TextObject(turn_resp, (900, 700), f_size, white)
    ScreenObject.blit_scr_obj(curr_game, [0,0], curr_game.background)
    # display response and score
    if curr_game.score[0] + curr_game.score[1] < 5:
        message = f'Your score is {curr_game.score[0]} Right {curr_game.score[1]} Wrong'
        score_msg = TextObject(message,(900,500), f_size, white)
        ScreenObject.blit_scr_obj(curr_game,(0,0),curr_game.background)
        TextObject.font_process(score_msg)
        TextObject.font_process(resp_msg)
        pygame.display.flip()
        sleep(3)
    
def make_surface(file, scale_to_screen=False):
    surface = pygame.image.load(file).convert_alpha()
    if scale_to_screen:
        # Scale to current display size
        w, h = display.get_size()
        surface = pygame.transform.smoothscale(surface, (w, h))
    return surface

def blit_formatted(file):
    global image_centerx
    # reads text formatted as [[Text, Size, X Postion or 'center', Y Position, Color]]
    lines = get_file('free_cash.csv',5)[0]
    for index, line in enumerate(lines):
        line[2].strip
        line[3].strip
        line[4].strip
        if line[2] == 'center':
            line[2] = image_centerx
        if line[4] == 'white':
            line[4] = white
        elif line[4] == 'blue':
            line[4] = blue
        elif line[4] == 'red':
            line[4] = red
        else:
            line[4] = white
        greeting = line[0]
        greet = TextObject(greeting, ( int(line[2]), int(line[3])), int(line[1]), line[4] )
        TextObject.font_process(greet)

# \\\\\\\\\\\\\\\\\\\ END UTILITY METHODS \\\\\\\\\\\\\\\\\\\\\\\\\\

#////////////////// START METHODS /////////////////////////


#================ CHOOSE GAME ====================
def choose_game():
    choice_bkg = make_surface(gpath + 'game_choice.jpg', scale_to_screen=True)
    global curr_game
    bakgnd = ScreenObject((0,0))
    ScreenObject.blit_scr_obj(bakgnd, bakgnd.location, choice_bkg)
    greeting = 'Please select a game to play'
    greet = TextObject(greeting, (image_centerx, 100), 80, white)
    TextObject.font_process(greet)
    # Only two choices: dolphin (left), bonehenge (right)
    # Left side: dolphin
    x = 430
    y = 400
    name_left = 'dolphin'
    file_left = name_left + '_dscr.csv'
    dscr_left = get_file(file_left, 1)
    greeting = dscr_left[0][0][0]
    greet = TextObject(greeting, (x, y), 70, white)
    TextObject.font_process(greet)
    y = y + 90
    greeting = dscr_left[0][1][0]
    greet = TextObject(greeting, (image_centerx, 300), 80, white, 30)
    parsed_lines = TextObject.parse_string(greet)
    for item in parsed_lines:
        greet = TextObject(item, (x, y), 60, white)
        TextObject.font_process(greet)
        y = y + 70

    # Right side: bonehenge
    x = 1430
    y = 400
    name_right = 'bonehenge'
    file_right = name_right + '_dscr.csv'
    dscr_right = get_file(file_right, 1)
    greeting = dscr_right[0][0][0]
    greet = TextObject(greeting, (x, y), 80, white)
    TextObject.font_process(greet)
    y = y + 90
    greeting = dscr_right[0][1][0]
    greet = TextObject(greeting, (x, y), 80, white, 30)
    parsed_lines = TextObject.parse_string(greet)
    for item in parsed_lines:
        greet = TextObject(item, (x, y), 60, white)
        TextObject.font_process(greet)
        y = y + 70
    pygame.display.flip()

    # Wait for mouse click to select game
    screen_w = display.get_width()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < screen_w // 2:
                    # Left half: dolphin
                    name = 'dolphin'
                else:
                    # Right half: bonehenge
                    name = 'bonehenge'
                break
        else:
            continue
        break
    type_ = game_types[name]
    if type_ == 'picture':
        background = make_surface(gpath + name + '_bkg.jpg', scale_to_screen=True)
        curr_game = PictGame( name, background, get_file(name + '_picture.csv', 2)[0], [0,0])
    elif type_ == 'text':
        background = make_surface(gpath + name + '_bkg.jpg', scale_to_screen=True)
        curr_game = TextGame( name, background, get_file(name + '_qna.csv', 4)[0], [0,0])
    pinball = SoundObject('pinball-start.mp3', .3)
    SoundObject.play_sound(pinball)
    sleep(2.5)
    return curr_game
# ^^^^^^^^^^^^^^^^^^^^ CHOOSE GAME ^^^^^^^^^^^^^^^^^^^

#==================== TEXT GAME =====================
def text_game():
    button_list = [0, 1, 0, 1, 0, 1, 0]
    wrong_sound = SoundObject('Downer.mp3', .2)
    right_sound = SoundObject('Quick-win.mp3', .3)
    # get 5 (number of turns)
    turn_picks = sample(range( 0, len(curr_game.just_q)), 5)
    curr_game.score = [0,0]
    turn_no = 0 #used by database
    # take turns
    # ||||||||| 5 TURNS ||||||||||||||||||||||||
    for index in turn_picks:
        display.blit(curr_game.background, (0,0))
        turn_no += 1
        turn_ans = (curr_game.just_a[index])
        # need to go through questions and randomize answers
        display_list = turn_ans[:] # make a copy
        shuffle(display_list)
        # for each turn need to blit question and answers on screen
        # display the question
        qx_offset = 990
        qy_offset = 100
        question = TextObject(curr_game.just_q[index], [qx_offset,qy_offset], 80, white, 30)
        q_db = question.text # whole question before parse
        q_parsed = TextObject.parse_string(question)
        for item in q_parsed:
            question.location = [qx_offset,qy_offset]
            question.text = item
            TextObject.font_process(question)
            qy_offset += 70
        # place answers
        ax_offset = 320
        ay_offset = 500
        ans_font = 60
        blit_x = []
        for i in range(0,3):
            blit_x.append(ax_offset) # for use in later lookup
            ay_offset = 500
            answer = TextObject(display_list[i], [ax_offset,ay_offset], ans_font, white, 20)
            q_parsed = TextObject.parse_string(answer)
            for item in q_parsed:
                answer.location = [ax_offset,ay_offset]
                answer.text = item
                TextObject.font_process(answer)
                ay_offset += 70
            ax_offset += 640
        
        pygame.display.flip()

        # go and get the button pressed and convert it to an index
        btn_dict = {1:1, 3:2, 5:3}
        resp = btn_dict[btn_proc(None)]
        # need to highlight correct in green
        
        r_indx = display_list.index(turn_ans[0]) #gives index of right ans
        highlight_ans = TextObject(turn_ans[0], [blit_x[r_indx], 500],ans_font,green, 20)
        h_parsed = TextObject.parse_string(highlight_ans)
        ay_offset = 500
        for item in h_parsed:
            highlight_ans.location = [blit_x[r_indx],ay_offset]
            highlight_ans.text = item
            TextObject.font_process(highlight_ans)
            ay_offset += 70

        # Right and Wrong answer processing
        if display_list[resp -1] == turn_ans[0]:
            print('got it')
            resp_ans = True
            SoundObject.play_sound(right_sound)
        else:
            print('wrong')
            resp_ans = False
            SoundObject.play_sound(wrong_sound)
            # need to blit wrong in red
            ax_offset = 320
            ay_offset = 500
            highlight_ans = TextObject(display_list[resp - 1],(blit_x[resp - 1],ay_offset),ans_font,red,20)
            h_parsed = TextObject.parse_string(highlight_ans)
            for item in h_parsed:
                highlight_ans.location = [blit_x[resp-1],ay_offset]
                highlight_ans.text = item
                TextObject.font_process(highlight_ans)
                ay_offset += 70
        if use_db:
            # turn by turn data put in db
            game_no = db_module.get_game()
            turn_data = (game_no, turn_no, q_db, display_list[resp -1], resp_ans)
            db_module.turn_write(turn_data)
        pygame.display.flip()
        sleep(1)
        score_process(curr_game, resp_ans)

#^^^^^^^^^^^^^^^^^^ TEXT GAME ^^^^^^^^^^^^^^^^^^^^

#================== PICTURE GAME =================
def picture_game():
    wrong_sound = SoundObject('Downer.mp3', .2)
    right_sound = SoundObject('Quick-win.mp3', .3)
    picture_intro(curr_game)
    button_list = [0, 1, 1, 1, 1, 1, 0]
    # get 5 indexes for our turns
    turn_picks = sample(range( 0, len(curr_game.all_picts)), 5)
    for q in range(0,5):
        question_picture = curr_game.all_picts[turn_picks[q]][0]
        answer_picture = curr_game.all_picts[turn_picks[q]][1]
        # need to get a random set of 2 other indexes the don't equal hero
        wrong_a = answer_picture
        shuffle_answers = []
        shuffle_answers.append(answer_picture)
        # pick something other than the hero
        for i in range(0,4):
            #     don't duplicate right answer   don't repeat any
            while (answer_picture == wrong_a) or (wrong_a in shuffle_answers):
                index = sample(range( 0, len(curr_game.all_picts)), 1)[0]
                wrong_a = curr_game.all_picts[index][1]
            shuffle_answers.append(wrong_a)
        
        ScreenObject.blit_scr_obj(curr_game,[0,0], curr_game.background)
        #shuffle_answer order
        shuffle(shuffle_answers)
        # Remove the old static gray glow blit (was misaligned)
        # display.blit(gray_glow, (770, 2))
        # Center the challenge (question) picture at the top of the screen
        qpic_orig_w, qpic_orig_h = question_picture.get_width(), question_picture.get_height()
        # Scale the question picture to fit a reasonable width (e.g., 25% of screen width)
        screen_w = display.get_width()
        screen_h = display.get_height()
        qpic_target_w = int(screen_w * 0.25)
        qpic_scale = qpic_target_w / qpic_orig_w
        qpic_target_h = int(qpic_orig_h * qpic_scale)
        scaled_qpic = pygame.transform.smoothscale(question_picture, (qpic_target_w, qpic_target_h))
        qpic_x = (screen_w - qpic_target_w) // 2
        qpic_y = int(screen_h * 0.04)  # 4% from the top
        # Draw a glow behind the challenge picture, scaled and centered
        glow_margin = int(qpic_target_w * 0.08)  # 8% margin for glow
        glow_w = qpic_target_w + 2 * glow_margin
        glow_h = qpic_target_h + 2 * glow_margin
        scaled_gray_glow = pygame.transform.smoothscale(gray_glow, (glow_w, glow_h))
        glow_x = qpic_x - glow_margin
        glow_y = qpic_y - glow_margin
        display.blit(scaled_gray_glow, (glow_x, glow_y))
        display.blit(scaled_qpic, (qpic_x, qpic_y))

        # Dynamically space answer images across the screen width
        blit_index = []
        screen_w = display.get_width()
        num_answers = 5
        margin = int(0.05 * screen_w)  # 5% margin on each side
        available_w = screen_w - 2 * margin
        img_w = int(available_w / num_answers * 0.9)  # leave some space between
        spacing = int(available_w / num_answers)
        ay = int(display.get_height() * 0.55)  # 55% down the screen
        for i in range(num_answers):
            x = margin + i * spacing
            # scale image to fit img_w (keep aspect ratio)
            img = shuffle_answers[i]
            orig_w, orig_h = img.get_width(), img.get_height()
            scale_factor = img_w / orig_w
            new_h = int(orig_h * scale_factor)
            scaled_img = pygame.transform.smoothscale(img, (img_w, new_h))
            display.blit(scaled_img, (x, ay))
            blit_index.append(x)

        pygame.display.flip()
        # Wait for mouse click and determine which image was clicked
        selected = None
        while selected is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL)) or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if click is within any answer image
                    for i in range(num_answers):
                        x = blit_index[i]
                        if mx >= x and mx <= x + img_w and my >= ay and my <= ay + new_h:
                            selected = i + 1  # 1-based index for compatibility
                            break
            if selected is not None:
                break
        resp = selected
        # correct answer highlited green nomatter what
        # Dynamically scale and position the glow to match the answer image
        glo_offset = int(img_w * 0.05)  # 5% of image width as offset
        glow_w = int(img_w * 1.1)  # Glow slightly larger than image
        glow_h = int(new_h * 1.1)
        scaled_green_glow = pygame.transform.smoothscale(green_glow, (glow_w, glow_h))
        scaled_red_glow = pygame.transform.smoothscale(red_glow, (glow_w, glow_h))
        c_index = shuffle_answers.index(answer_picture)
        glow_x = blit_index[c_index] - int((glow_w - img_w) / 2)
        glow_y = ay - int((glow_h - new_h) / 2)
        display.blit(scaled_green_glow, (glow_x, glow_y))
        pygame.display.flip()

        if answer_picture == shuffle_answers[int(resp -1)]:
            resp_ans = True
            SoundObject.play_sound(right_sound)

        else:
            # user answer highligted red if wrong
            resp_ans = False
            SoundObject.play_sound(wrong_sound)
            c_index = resp - 1
            glow_x = blit_index[c_index] - int((glow_w - img_w) / 2)
            glow_y = ay - int((glow_h - new_h) / 2)
            display.blit(scaled_red_glow, (glow_x, glow_y))
            sleep(.01)
            pygame.display.flip()
        if use_db:
                game_no = db_module.get_game()
                _qpic = curr_game.qu_ans[turn_picks[q]][0]
                # have to work backward to find the response
                for location, item in enumerate(curr_game.all_picts):
                    if shuffle_answers[resp-1] == item[1]:
                        a_file = curr_game.qu_ans[location][1]
                turn_data = (game_no, q + 1, _qpic, a_file, resp_ans)
                db_module.turn_write(turn_data)
        sleep(1.5)   
            
        score_process(curr_game, resp_ans)
    
        
# ^^^^^^^^^^^^^^^  PICTURE GAME ^^^^^^^^^^^^^^^^^^       


#================= FINAL SCORE ===================
def final_score(score):
    # play game final sound
    f_score_sounds = ['0_right.wav','1_right.wav','2_right.mp3','3_right.wav',
                       '4_right.mp3', '5_right.wav']
    f_score_vol = [.3, 1, 1, .5, 1, 1]
    final_sound = SoundObject(f_score_sounds[score[0]], f_score_vol[score[1]])
    SoundObject.play_sound(final_sound)

    # put up background and text
    final_bkg = make_surface(gpath + 'finalscore.jpg', scale_to_screen=True)
    bkg = ScreenObject([0,0])
    ScreenObject.blit_scr_obj(bkg, [0,0], final_bkg)
    msg_y = 400
    message = 'Final Score'
    msg = TextObject(message, [image_centerx, msg_y], 80, white)
    TextObject.font_process(msg)
    message = f'{score[0]} Right {score[1]} Wrong'
    msg = TextObject(message, [image_centerx, msg_y + 90], 80, white)
    TextObject.font_process(msg)
    pygame.display.flip()
    sleep(4)
#^^^^^^^^^^^^^^^^^ FINAL SCORE ^^^^^^^^^^^^^^^^^^^



# GAME LOOP -------
def game_loop():
    global curr_game
    # game must be created first
    curr_game = choose_game()
    if use_db:
        # make an entry in the game field -1 score means game isn't finished
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y,%H,%M,%S")
        db_module.db_start()
        game_data = (curr_game.name, date_time, -1, None)
        this_game = db_module.game_write(game_data)
        db_module.db_close
    if type(curr_game).__name__ == 'PictGame':
        picture_game()
        type(curr_game).__name__
    else:
        text_game()
    # we have gone and played the game so we can now finish
    if use_db:
        # add the ending score
        db_score = (curr_game.score[0], this_game)
        db_module.db_start()
        db_module.game_over(db_score)
        db_module.db_close
    final_score(curr_game.score)

#\\\\\\\\\\\\\\\\\\\\\\ END METHODS \\\\\\\\\\\\\\\\\\\\\\\\




def main():
    
    try:
        init()
        while 1 == 1:
            global curr_game
        
            try:
                curr_game
            except NameError:
                    print('no curr_game defined')
            else:
                print('previus game deleted')
                del curr_game
            game_loop()

        
    except KeyboardInterrupt:
        #cleanup at end of program
        print('   Shutdown')
        if os.name != 'nt':
            GPIO.cleanup()
            os.system('sudo fuser -k 8000/tcp')

if __name__ == '__main__':
    main()