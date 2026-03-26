from .shared import *

class SpeedClick (BaseGame ):

    """Klikej rychle na bílé čtverce - timer začíná až po prvním kliknutí"""

    def __init__ (self ):

        super ().__init__ ()

        self .targets =[]

        self .clicked =0 

        self .timer =0 

        self .timer_started =False 

        self .time_limit =420 

        self .generate_targets ()



    def generate_targets (self ):

        self .targets =[]

        for _ in range (10 ):

            x =random .randint (100 ,SCREEN_WIDTH -100 )

            y =random .randint (200 ,SCREEN_HEIGHT -200 )

            self .targets .append (pygame .Rect (x ,y ,60 ,60 ))



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN :

            if not self .timer_started :

                self .timer_started =True 



            pos =event .pos 

            for i ,target in enumerate (self .targets ):

                if target .collidepoint (pos ):

                    self .targets .pop (i )

                    self .clicked +=1 

                    if self .clicked ==10 :

                        self .won =True 

                    break 



    def update (self ):

        if self .timer_started :

            self .timer +=1 

            if self .timer >self .time_limit :

                if self .clicked >=10 :

                    self .won =True 

                else :

                    self .lost =True 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )

        title =FONT_LARGE .render ("RYCHLE KLIKEJ!",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -180 ,30 ))



        for target in self .targets :

            pygame .draw .rect (screen ,WHITE ,target )

            pygame .draw .rect (screen ,CYAN ,target ,3 )



        info =FONT_MEDIUM .render (f"Kliknutí: {self .clicked }/10",True ,YELLOW )

        screen .blit (info ,(SCREEN_WIDTH //2 -150 ,700 ))



        if self .timer_started :

            time_left =max (0 ,(self .time_limit -self .timer )//60 )

            time_text =FONT_SMALL .render (f"Čas: {time_left }s",True ,GREEN if time_left >2 else RED )

            screen .blit (time_text ,(SCREEN_WIDTH //2 -60 ,750 ))

        else :

            start_text =FONT_SMALL .render ("Klikni kdekoli pro start!",True ,YELLOW )

            screen .blit (start_text ,(SCREEN_WIDTH //2 -150 ,600 ))



    def get_hint (self ):

        return "Klikej na všechny čtverce!"

def get_level_class():
    return SpeedClick

