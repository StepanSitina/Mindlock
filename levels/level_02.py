from .shared import *

class ReactionTime (BaseGame ):

    """Test reflexu - červená = prohra, zelená = měření"""

    def __init__ (self ):

        super ().__init__ ()

        self .state ="red"

        self .timer =0 

        self .reaction_time_ms =0 

        self .target_time =300 

        self .change_timer =random .randint (120 ,300 )

        self .clicked =False 

        self .start_frame =0 



    def update (self ):

        self .timer +=1 

        if self .timer ==self .change_timer and self .state =="red":

            self .state ="green"

            self .start_frame =self .timer 



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN and not self .clicked :

            self .clicked =True 

            if self .state =="red":



                self .lost =True 

            elif self .state =="green":



                frames_passed =self .timer -self .start_frame 

                self .reaction_time_ms =int (frames_passed *(1000 /60 ))

                if self .reaction_time_ms <self .target_time :

                    self .won =True 

                else :

                    self .lost =True 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )

        title =FONT_LARGE .render ("REFLEX TEST",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -200 ,30 ))



        info =FONT_SMALL .render (f"Červená = prohra | Zelená = měření | Cíl: pod {self .target_time }ms",True ,YELLOW )

        screen .blit (info ,(SCREEN_WIDTH //2 -400 ,120 ))



        if self .state =="red":



            pygame .draw .rect (screen ,RED ,pygame .Rect (400 ,250 ,1000 ,500 ))

            text =FONT_LARGE .render ("CEKEJ... NEKLIKEJ!",True ,WHITE )

            screen .blit (text ,(SCREEN_WIDTH //2 -350 ,450 ))

        elif self .state =="green":

            if not self .clicked :



                pygame .draw .rect (screen ,GREEN ,pygame .Rect (400 ,250 ,1000 ,500 ))

                text =FONT_LARGE .render ("KLIKNI TEĎ!",True ,BLACK )

                screen .blit (text ,(SCREEN_WIDTH //2 -280 ,450 ))

            else :



                time_text =FONT_LARGE .render (f"{self .reaction_time_ms } ms",True ,YELLOW )

                screen .blit (time_text ,(SCREEN_WIDTH //2 -150 ,280 ))



                if self .reaction_time_ms <self .target_time :

                    result =FONT_MEDIUM .render ("VYHRAL!",True ,GREEN )

                    diff =FONT_SMALL .render (f"{self .target_time -self .reaction_time_ms }ms lepší",True ,GREEN )

                else :

                    result =FONT_MEDIUM .render ("PROHRA!",True ,RED )

                    diff =FONT_SMALL .render (f"{self .reaction_time_ms -self .target_time }ms horší",True ,RED )



                screen .blit (result ,(SCREEN_WIDTH //2 -120 ,450 ))

                screen .blit (diff ,(SCREEN_WIDTH //2 -120 ,500 ))



    def get_hint (self ):

        return f"Čekej na zelený čtverec a klikni rychleji než {self .target_time }ms!"

def get_level_class():
    return ReactionTime

