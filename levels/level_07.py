from .shared import *

class MemoryCards (BaseGame ):

    """Hra na paměť - otočit karty a najít páry - maximálně 2 karty současně"""

    def __init__ (self ):

        super ().__init__ ()

        self .symbols =['A','B','C','D']

        self .cards =self .symbols +self .symbols 

        random .shuffle (self .cards )

        self .revealed =[False ]*8 

        self .matched =[False ]*8 

        self .selected =[]

        self .matches =0 

        self .animation_timer =0 

        self .card_size =100 

        self .card_spacing =50 

        self .start_x =SCREEN_WIDTH //2 -2 *(self .card_size )-self .card_spacing 

        self .start_y =SCREEN_HEIGHT //2 -self .card_size 



    def handle_event (self ,event ):



        if event .type ==pygame .MOUSEBUTTONDOWN and len (self .selected )<2 and self .animation_timer ==0 :

            pos =event .pos 

            for i in range (8 ):

                x =self .start_x +(i %4 )*(self .card_size +self .card_spacing )

                y =self .start_y +(i //4 )*(self .card_size +self .card_spacing )

                if pygame .Rect (x ,y ,self .card_size ,self .card_size ).collidepoint (pos ):



                    if not self .matched [i ]and i not in self .selected :

                        self .selected .append (i )

                        self .revealed [i ]=True 





                        if len (self .selected )==2 :

                            if self .cards [self .selected [0 ]]==self .cards [self .selected [1 ]]:



                                self .matched [self .selected [0 ]]=True 

                                self .matched [self .selected [1 ]]=True 

                                self .matches +=1 

                                self .selected =[]

                                if self .matches ==4 :

                                    self .won =True 

                            else :



                                self .animation_timer =60 

                        break 



    def update (self ):



        if self .animation_timer >0 :

            self .animation_timer -=1 

            if self .animation_timer ==0 :



                for idx in self .selected :

                    self .revealed [idx ]=False 

                self .selected =[]



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )

        title =FONT_LARGE .render ("MEMORY KARTY",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -150 ,50 ))



        for i in range (8 ):

            x =self .start_x +(i %4 )*(self .card_size +self .card_spacing )

            y =self .start_y +(i //4 )*(self .card_size +self .card_spacing )

            color =GREEN if self .matched [i ]else BLUE 

            pygame .draw .rect (screen ,color ,pygame .Rect (x ,y ,self .card_size ,self .card_size ))

            if self .revealed [i ]:

                text =FONT_LARGE .render (self .cards [i ],True ,YELLOW )

                text_rect =text .get_rect (center =(x +self .card_size //2 ,y +self .card_size //2 ))

                screen .blit (text ,text_rect )

            pygame .draw .rect (screen ,WHITE ,pygame .Rect (x ,y ,self .card_size ,self .card_size ),3 )



        info =FONT_SMALL .render (f"Páry: {self .matches }/4",True ,WHITE )

        screen .blit (info ,(SCREEN_WIDTH //2 -100 ,700 ))



        hint_text =FONT_TINY .render ("Maximálně 2 karty současně!",True ,YELLOW )

        screen .blit (hint_text ,(SCREEN_WIDTH //2 -150 ,750 ))



    def get_hint (self ):

        return "Zapamatuj si pozice karet! Maximálně 2 současně."

def get_level_class():
    return MemoryCards

