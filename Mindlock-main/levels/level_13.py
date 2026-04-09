from .shared import *

class RiddleGame (BaseGame ):

    """Lehké hádanky"""

    def __init__ (self ):

        super ().__init__ ()

        self .riddles =[

        {"q":"Co má ruku, ale nemůže psát?","a":"HODINY"},

        {"q":"Čím více vezmeš, tím víc ti zbyde. Co to je?","a":"STOPY"},

        {"q":"Co jde, ale nikdy nechodí?","a":"VODA"},

        ]

        self .current_riddle =random .choice (self .riddles )

        self .answer =""

        self .input_active =True 



    def handle_event (self ,event ):

        if event .type ==pygame .KEYDOWN and self .input_active :

            if event .key ==pygame .K_BACKSPACE :

                self .answer =self .answer [:-1 ]

            elif event .key ==pygame .K_RETURN :

                if self .answer .upper ()==self .current_riddle ["a"]:

                    self .won =True 

                else :

                    self .lost =True 

            elif event .unicode .isalpha ():

                self .answer +=event .unicode .upper ()



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )



        title =FONT_LARGE .render ("HÁDANKA",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -130 ,50 ))



        question =FONT_MEDIUM .render (self .current_riddle ["q"],True ,YELLOW )

        question_rect =question .get_rect (center =(SCREEN_WIDTH //2 ,200 ))

        screen .blit (question ,question_rect )



        answer_text =FONT_MEDIUM .render (self .answer +"_",True ,WHITE )

        answer_rect =answer_text .get_rect (center =(SCREEN_WIDTH //2 ,400 ))

        pygame .draw .rect (screen ,BLUE ,pygame .Rect (answer_rect .x -20 ,answer_rect .y -20 ,answer_rect .width +40 ,answer_rect .height +40 ))

        screen .blit (answer_text ,answer_rect )



        instr =FONT_SMALL .render ("Napiš odpověď a zmáčkni ENTER",True ,WHITE )

        screen .blit (instr ,(SCREEN_WIDTH //2 -220 ,600 ))



    def get_hint (self ):

        return f"Nápověda: {self .current_riddle ['a'][0 ]}..."

def get_level_class():
    return RiddleGame

