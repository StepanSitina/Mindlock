from .shared import *

class WordUnscrambler (BaseGame ):

    """Zamíchané slovo - psaní textu + klikání na písmena"""

    def __init__ (self ):

        super ().__init__ ()

        self .word_pairs =[

        ("AHOJ","HOJA"),

        ("HLAVA","VAHLA"),

        ("PSANÍ","NASÍP"),

        ("OKNO","ONKO"),

        ("STŮL","LŮST"),

        ("KNIHA","NHKIA"),

        ("BARVA","VARBA"),

        ("TRÁVA","VAÁRT"),

        ("CHLEB","LHCBE"),

        ("VODA","ADOV"),

        ("VÍTR","RÍTV"),

        ("SLOVO","VOSLO"),

        ("MRAKY","YAMRK"),

        ]



        self .current_pair =random .choice (self .word_pairs )

        self .original =self .current_pair [0 ]

        self .scrambled =list (self .current_pair [1 ])

        self .answer =""

        self .used =[False ]*len (self .scrambled )



    def handle_event (self ,event ):

        if event .type ==pygame .KEYDOWN :



            if event .key ==pygame .K_BACKSPACE :

                if len (self .answer )>0 :



                    last_char =self .answer [-1 ]



                    for i in range (len (self .scrambled )-1 ,-1 ,-1 ):

                        if self .scrambled [i ]==last_char and self .used [i ]:

                            self .used [i ]=False 

                            break 



                    self .answer =self .answer [:-1 ]



            elif event .key ==pygame .K_RETURN :

                if self .answer .upper ()==self .original :

                    self .won =True 

                else :

                    self .answer =""

                    self .used =[False ]*len (self .scrambled )



            elif event .unicode .isalpha ():

                char =event .unicode .upper ()



                if char in self .scrambled and len (self .answer )<len (self .original ):



                    char_index =-1 

                    for i ,letter in enumerate (self .scrambled ):

                        if letter ==char and not self .used [i ]:

                            char_index =i 

                            break 



                    if char_index !=-1 :

                        self .answer +=char 

                        self .used [char_index ]=True 



                        if self .answer ==self .original :

                            self .won =True 



        elif event .type ==pygame .MOUSEBUTTONDOWN :

            pos =event .pos 





            for i in range (len (self .scrambled )):

                if self .used [i ]:

                    continue 

                x =100 +i *90 

                y =420 

                if pygame .Rect (x ,y ,70 ,70 ).collidepoint (pos ):

                    if len (self .answer )<len (self .original ):

                        self .answer +=self .scrambled [i ]

                        self .used [i ]=True 

                        if self .answer ==self .original :

                            self .won =True 

                    return 





            if pygame .Rect (SCREEN_WIDTH -250 ,SCREEN_HEIGHT -120 ,200 ,80 ).collidepoint (pos ):

                self .answer =""

                self .used =[False ]*len (self .scrambled )



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )



        title =FONT_LARGE .render ("SEŘAĎ SLOVO",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -140 ,30 ))



        instr1 =FONT_SMALL .render ("Psej nebo klikej na písmena v správném pořadí",True ,YELLOW )

        screen .blit (instr1 ,(SCREEN_WIDTH //2 -300 ,120 ))





        answer_box_rect =pygame .Rect (SCREEN_WIDTH //2 -250 ,180 ,500 ,80 )

        pygame .draw .rect (screen ,BLUE ,answer_box_rect )

        pygame .draw .rect (screen ,CYAN ,answer_box_rect ,3 )





        for i in range (len (self .original )):

            x =SCREEN_WIDTH //2 -240 +i *95 

            y =195 



            if i <len (self .answer ):

                pygame .draw .rect (screen ,GREEN ,pygame .Rect (x ,y ,70 ,70 ))

                letter_text =FONT_MEDIUM .render (self .answer [i ],True ,BLACK )

            else :

                pygame .draw .rect (screen ,(40 ,40 ,100 ),pygame .Rect (x ,y ,70 ,70 ))

                letter_text =FONT_MEDIUM .render ("_",True ,WHITE )



            pygame .draw .rect (screen ,WHITE ,pygame .Rect (x ,y ,70 ,70 ),2 )

            letter_rect =letter_text .get_rect (center =(x +35 ,y +35 ))

            screen .blit (letter_text ,letter_rect )





        avail_text =FONT_SMALL .render ("DOSTUPNÁ PÍSMENA:",True ,CYAN )

        screen .blit (avail_text ,(100 ,350 ))



        for i ,char in enumerate (self .scrambled ):

            if self .used [i ]:

                continue 

            x =100 +i *90 

            y =420 

            pygame .draw .rect (screen ,BLUE ,pygame .Rect (x ,y ,70 ,70 ))

            pygame .draw .rect (screen ,WHITE ,pygame .Rect (x ,y ,70 ,70 ),2 )



            char_text =FONT_MEDIUM .render (char ,True ,WHITE )

            char_rect =char_text .get_rect (center =(x +35 ,y +35 ))

            screen .blit (char_text ,char_rect )





        clear_btn_rect =pygame .Rect (SCREEN_WIDTH -250 ,SCREEN_HEIGHT -120 ,200 ,80 )

        pygame .draw .rect (screen ,RED ,clear_btn_rect )

        pygame .draw .rect (screen ,WHITE ,clear_btn_rect ,2 )

        clear_text =FONT_SMALL .render ("SMAZAT",True ,BLACK )

        clear_rect =clear_text .get_rect (center =clear_btn_rect .center )

        screen .blit (clear_text ,clear_rect )





        instr2 =FONT_SMALL .render ("ENTER: Ověř | BACKSPACE: Smazat poslední | KLIK na písmena",True ,WHITE )

        screen .blit (instr2 ,(SCREEN_WIDTH //2 -350 ,700 ))



    def get_hint (self ):

        return f"Správné slovo: {self .original }"

def get_level_class():
    return WordUnscrambler

