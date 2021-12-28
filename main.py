import time

import pyautogui
from game_logic import GameLogic
from game_ui import GameUI

time.sleep(10)
print("waited")

gl = GameLogic()
gui = GameUI()
gui.focusOnEmulatorScreen()
gui.DrawLoop()

#print('test')
try:
    while 1:
        print("Updating Game State")

        gui.UpdateGameState()
    
        print("Calculating Action")
        next_action = gl.GetNextAction(gui.gs, gui.gv)
        #print("Action: " + next_action.name)
        #print(next_action.cards)
    
        #inpstr = input('Continue?')
        #if inpstr != "y":
        #    exit(0)

        gui.ProcessAction(next_action)

        #time.sleep(1)
        #exit(0)
except: KeyboardInterrupt

    