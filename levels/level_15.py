from .shared import *

class QuantumSwitches (BaseGame ):

    """Quantum Switches – activate switches in the right sequence.

    Each switch toggles itself AND specific linked switches."""



    NUM_SW =5 



    LINKS ={

    0 :[1 ],

    1 :[2 ],

    2 :[3 ],

    3 :[4 ],

    4 :[],

    }







    def __init__ (self ):

        super ().__init__ ()

        self .switches =[True ]*self .NUM_SW 

        self .switch_anim =[1.0 ]*self .NUM_SW 

        self .press_count =0 

        self .max_presses =7 

        self .flash_msg =""

        self .flash_timer =0 



        for idx in [1 ,3 ,4 ,0 ]:

            self ._toggle (idx )



    def _toggle (self ,idx ):

        self .switches [idx ]=not self .switches [idx ]

        for linked in self .LINKS .get (idx ,[]):

            self .switches [linked ]=not self .switches [linked ]



    def handle_event (self ,event ):

        if event .type !=pygame .MOUSEBUTTONDOWN or self .won or self .lost :

            return 

        pos =event .pos 

        ox =(SCREEN_WIDTH -self .NUM_SW *120 )//2 

        for i in range (self .NUM_SW ):

            cx =ox +i *120 +50 

            cy =SCREEN_HEIGHT //2 

            if (pos [0 ]-cx )**2 +(pos [1 ]-cy )**2 <=45 **2 :

                self ._toggle (i )

                self .press_count +=1 

                if all (self .switches ):

                    self .won =True 

                    return 

                if self .press_count >=self .max_presses :

                    self .lost =True 

                    self .flash_msg ="PRILIS MNOHO TAHU!"

                    self .flash_timer =120 

                return 



    def update (self ):

        for i in range (self .NUM_SW ):

            target =1.0 if self .switches [i ]else 0.0 

            self .switch_anim [i ]+=(target -self .switch_anim [i ])*0.22 

        if self .flash_timer >0 :

            self .flash_timer -=1 



    def draw (self ,screen ):

        screen .fill ((12 ,12 ,30 ))



        title =FONT_LARGE .render ("QUANTUM SWITCHES",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -title .get_width ()//2 ,30 ))



        goal =FONT_SMALL .render ("CIL: Rozsviť všechny přepínače!",True ,YELLOW )

        screen .blit (goal ,(SCREEN_WIDTH //2 -goal .get_width ()//2 ,100 ))



        ox =(SCREEN_WIDTH -self .NUM_SW *120 )//2 





        for i ,linked in self .LINKS .items ():

            cx1 =ox +i *120 +50 

            cy1 =SCREEN_HEIGHT //2 

            for j in linked :

                if j >i :

                    cx2 =ox +j *120 +50 

                    cy2 =SCREEN_HEIGHT //2 

                    pygame .draw .line (screen ,(50 ,50 ,80 ),(cx1 ,cy1 ),(cx2 ,cy2 ),2 )





        for i in range (self .NUM_SW ):

            cx =ox +i *120 +50 

            cy =SCREEN_HEIGHT //2 

            a =max (0.0 ,min (1.0 ,self .switch_anim [i ]))

            color =(

            int (180 *(1 -a )+0 *a ),

            int (30 *(1 -a )+220 *a ),

            int (30 *(1 -a )+80 *a ),

            )

            pygame .draw .circle (screen ,color ,(cx ,cy ),42 )

            pygame .draw .circle (screen ,WHITE ,(cx ,cy ),42 ,3 )

            lbl =FONT_MEDIUM .render (str (i +1 ),True ,BLACK if self .switches [i ]else WHITE )

            screen .blit (lbl ,lbl .get_rect (center =(cx ,cy )))

            st =FONT_TINY .render ("ON"if self .switches [i ]else "OFF",True ,WHITE )

            screen .blit (st ,st .get_rect (center =(cx ,cy +58 )))





        ct =FONT_SMALL .render (

        f"Tahy: {self .press_count }/{self .max_presses }",True ,

        RED if self .press_count >=self .max_presses -2 else WHITE )

        screen .blit (ct ,(SCREEN_WIDTH //2 -ct .get_width ()//2 ,SCREEN_HEIGHT -120 ))





        legend =FONT_TINY .render (

        "Kazdy prepinac meni sebe a nanejvys jednoho souseda. Premyslej dopredu.",True ,LIGHT_GRAY )

        screen .blit (legend ,(SCREEN_WIDTH //2 -legend .get_width ()//2 ,SCREEN_HEIGHT -50 ))





        if self .flash_timer >0 and self .flash_msg :

            ft =FONT_MEDIUM .render (self .flash_msg ,True ,RED )

            screen .blit (ft ,(SCREEN_WIDTH //2 -ft .get_width ()//2 ,SCREEN_HEIGHT //2 +140 ))





        if self .won :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render ("VSECHNY ROZSVICENY!",True ,GREEN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))

        if self .lost :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render ("PRILIS MNOHO TAHU!",True ,RED )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))



    def get_hint (self ):

        return "Nezacinas od nuly: nektere prepinace uz sviti. Planuj par kroku dopredu."

def get_level_class():
    return QuantumSwitches

