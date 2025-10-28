from tagGame import TagGameRules, TagGameState
from tagAgents import TagPacmanAgent, TagGhostAgent, KeyboardTagPacmanAgent, SmartTagGhostAgent
from game import Game
import layout
import sys
from optparse import OptionParser

def default(str):
    return str + ' [Default: %default]'

def readCommand(argv):
    usageStr = """
    USAGE:      python runTag.py <options>
    EXAMPLES:   (1) python runTag.py
                    - starts a tag game with AI agents
                (2) python runTag.py --keyboard
                    - starts a tag game with keyboard control for Pacman
                (3) python runTag.py --layout mediumMaze
                    - starts a tag game on a different map
                (4) python runTag.py --maxTags 20
                    - game ends after 20 tags
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT from layouts folder to use'),
                      metavar='LAYOUT', default='mediumMaze')
    parser.add_option('-k', '--keyboard', action='store_true', dest='keyboard',
                      help='Use keyboard control for Pacman', default=False)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'),
                      default=1.0)
    parser.add_option('-f', '--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames (in seconds)'),
                      default=0.1)
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output', default=False)
    parser.add_option('--maxTags', dest='maxTags', type='int',
                      help=default('Maximum number of tags before game ends'),
                      default=10)
    parser.add_option('--maxMoves', dest='maxMoves', type='int',
                      help=default('Maximum number of moves before game ends'),
                      default=1000)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum time for agent computation'),
                      default=30)
    parser.add_option('--smartGhost', action='store_true', dest='smartGhost',
                      help='Use smart A* pathfinding ghost (much better at chasing!)', default=False)
                      
    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    
    return options

def loadLayout(layoutName):
 
    import layout as layoutModule
    try:
        return layoutModule.getLayout(layoutName)
    except:
        print(f"Layout '{layoutName}' not found. Using mediumMaze instead.")
        return layoutModule.getLayout('mediumMaze')

def runTagGame(options):
  
    # Load the layout
    layoutObj = loadLayout(options.layout)
    
    # Create agents
    if options.keyboard:
        pacmanAgent = KeyboardTagPacmanAgent(0)
        print("\n=== KEYBOARD CONTROLS ===")
        print("W/Up Arrow    - Move North")
        print("S/Down Arrow  - Move South")
        print("A/Left Arrow  - Move West")
        print("D/Right Arrow - Move East")
        print("Q             - Stop")
        print("========================\n")
    else:
        pacmanAgent = TagPacmanAgent(0)
        print("\n=== AI TAG GAME ===")
        print("Pacman and Ghost will play tag automatically!")
        print("==================\n")
    
    # Choose ghost agent based on options
    if options.smartGhost:
        ghostAgent = SmartTagGhostAgent(1)
        print("Using SMART Ghost with A* pathfinding!")
    else:
        ghostAgent = TagGhostAgent(1)
        print("Using standard Ghost agent.")
    
    # Create display
    if options.quietGraphics:
        import textDisplay
        display = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        display = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        display = graphicsDisplay.PacmanGraphics(options.zoom, frameTime=options.frameTime)
    
    # Create game rules
    rules = TagGameRules(timeout=options.timeout, maxTags=options.maxTags, maxMoves=options.maxMoves)
    
    # Create and run the game
    game = rules.newGame(layoutObj, pacmanAgent, [ghostAgent], display, quiet=False, catchExceptions=False)
    
    print(f"\n{'='*60}")
    print(f"{'TAG GAME - START!':^60}")
    print(f"{'='*60}")
    print(f"  Layout: {options.layout}")
    print(f"  Max Tags: {options.maxTags}")
    print(f"  Max Moves: {options.maxMoves}")
    print(f"  ")
    print(f"  >> Pacman starts as IT! (Chase the Ghost!)")
    print(f"  ")
    print(f"  * When you tag, roles switch!")
    print(f"  * IT chases, the other runs!")
    print(f"{'='*60}\n")
    
    game.run()
    
    # Print final statistics
    print(f"\n=== Final Statistics ===")
    print(f"Tags: {getattr(game.state.data, 'tag_count', 0)}")
    print(f"Moves: {getattr(game.state.data, 'move_count', 0)}")
    print(f"Score: {game.state.data.score}")
    who_is_it = "Pacman" if getattr(game.state.data, 'pacman_is_it', True) else "Ghost"
    print(f"Final IT: {who_is_it}")
    print(f"========================\n")
    
    return game

if __name__ == '__main__':
    """
    The main function called when runTag.py is run from the command line.
    """
    options = readCommand(sys.argv[1:])
    game = runTagGame(options)

