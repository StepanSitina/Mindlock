from .shared import *

class ColorBlind (BaseGame ):

    """Najdi jinou barvu - stejná barva, jen jiný odstín - VÍCE RUNDY A BAREV"""

    def __init__ (self ):

        super ().__init__ ()

        self .total_rounds =5 

        self .current_round =0 

        self .rounds_completed =0 

        self .available_colors =[RED ,BLUE ,YELLOW ,GREEN ,CYAN ]

        self .generate_new_round ()



    def generate_new_round (self ):

        """Generuj nové kolo s jinou barvou"""

        self .base_color =random .choice (self .available_colors )





        color_map ={

        RED :(200 ,50 ,50 ),

        BLUE :(50 ,100 ,200 ),

        YELLOW :(200 ,200 ,100 ),

        GREEN :(100 ,180 ,100 ),

        CYAN :(50 ,220 ,220 )

        }

        self .different_color =color_map [self .base_color ]

        self .positions =list (range (16 ))

        self .different_pos =random .randint (0 ,15 )

        random .shuffle (self .positions )



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN :

            pos =event .pos 

            for i in range (16 ):

                x =300 +(i %4 )*200 

                y =250 +(i //4 )*200 

                if pygame .Rect (x ,y ,150 ,150 ).collidepoint (pos ):

                    if self .positions [i ]==self .different_pos :

                        self .rounds_completed +=1 

                        if self .rounds_completed >=self .total_rounds :

                            self .won =True 

                        else :



                            self .current_round +=1 

                            self .generate_new_round ()

                    else :

                        self .lost =True 

                    break 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )

        title =FONT_LARGE .render ("NAJDI ROZDÍL",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -150 ,30 ))





        round_text =FONT_MEDIUM .render (f"Kolo {self .rounds_completed +1 }/{self .total_rounds }",True ,YELLOW )

        screen .blit (round_text ,(SCREEN_WIDTH //2 -150 ,100 ))



        for i in range (16 ):

            x =300 +(i %4 )*200 

            y =250 +(i //4 )*200 

            color =self .different_color if self .positions [i ]==self .different_pos else self .base_color 

            pygame .draw .rect (screen ,color ,pygame .Rect (x ,y ,150 ,150 ))

            pygame .draw .rect (screen ,WHITE ,pygame .Rect (x ,y ,150 ,150 ),2 )



    def get_hint (self ):

        return f"Najdi jinou barvu! Kolo {self .rounds_completed +1 }/{self .total_rounds }"

def get_level_class():
    return ColorBlind

