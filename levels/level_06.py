from .shared import *

class SimonSays (BaseGame ):

    def __init__ (self ):

        super ().__init__ ()

        self .colors =[RED ,YELLOW ,GREEN ,BLUE ]

        self .sequence =[0 ]

        self .player_sequence =[]

        self .current_step =0 

        self .waiting_for_input =False 

        self .lights_on =[False ]*4 

        self .light_timer =0 

        self .round =1 

        self .round_delay =0 

        self .sequence_delay =0 

        self .circle_radius =75 



    def _circle_positions (self ,screen_w ,screen_h ):

        s =min (screen_w /1920 ,screen_h /1080 )

        gap =int (100 *s )

        cy_center =screen_h //2 -int (30 *s )

        self .circle_radius =max (30 ,int (75 *s ))

        return [

        (screen_w //2 -gap ,cy_center -gap ),

        (screen_w //2 +gap ,cy_center -gap ),

        (screen_w //2 -gap ,cy_center +gap ),

        (screen_w //2 +gap ,cy_center +gap ),

        ]



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN and self .waiting_for_input :

            pos =event .pos 

            screen_w =SCREEN_WIDTH 

            screen_h =SCREEN_HEIGHT 

            circle_positions =self ._circle_positions (screen_w ,screen_h )

            for i ,(cx ,cy )in enumerate (circle_positions ):

                dist =((pos [0 ]-cx )**2 +(pos [1 ]-cy )**2 )**0.5 

                if dist <=self .circle_radius :

                    self .player_sequence .append (i )

                    self .lights_on [i ]=True 

                    self .light_timer =15 

                    if hasattr (self ,"sfx"):

                        self .sfx .play ("level_action")

                    self .check_sequence ()

                    break 



    def update (self ):

        self .light_timer =max (0 ,self .light_timer -1 )

        if self .light_timer ==0 :

            self .lights_on =[False ]*4 



        if self .round_delay >0 :

            self .round_delay -=1 

        elif self .sequence_delay >0 :

            self .sequence_delay -=1 

        elif not self .waiting_for_input and not self .won :

            self .play_sequence ()



    def play_sequence (self ):

        if self .current_step <len (self .sequence ):

            light_idx =self .sequence [self .current_step ]

            self .lights_on [light_idx ]=True 

            if hasattr (self ,"sfx"):

                self .sfx .play ("simon_flash")



            self .light_timer =max (15 ,30 -(len (self .sequence )//2 ))

            self .current_step +=1 



            self .sequence_delay =max (10 ,35 -(len (self .sequence )*2 ))

        else :

            self .waiting_for_input =True 

            self .player_sequence =[]



    def check_sequence (self ):



        current_index =len (self .player_sequence )-1 





        if self .player_sequence [current_index ]!=self .sequence [current_index ]:

            self .lost =True 

            return 





        if len (self .player_sequence )==len (self .sequence ):

            if len (self .sequence )==8 :



                self .won =True 

            else :



                self .sequence .append (random .randint (0 ,3 ))

                self .waiting_for_input =False 

                self .current_step =0 

                self .round +=1 



                base_delay =max (15 ,120 -(len (self .sequence )*5 ))

                self .round_delay =base_delay 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )



        screen_w =screen .get_width ()

        screen_h =screen .get_height ()

        s =min (screen_w /1920 ,screen_h /1080 )



        f_title =pygame .font .Font (None ,max (20 ,int (80 *s )))

        f_info =pygame .font .Font (None ,max (14 ,int (50 *s )))

        f_small =pygame .font .Font (None ,max (12 ,int (32 *s )))



        title =f_title .render ("SIMON SAYS",True ,CYAN )

        screen .blit (title ,title .get_rect (center =(screen_w //2 ,int (60 *s ))))





        circle_positions =self ._circle_positions (screen_w ,screen_h )

        gap =int (100 *s )

        r =self .circle_radius 

        cy_center =screen_h //2 -int (30 *s )



        for i in range (4 ):

            cx ,cy =circle_positions [i ]

            color =self .colors [i ]if not self .lights_on [i ]else (255 ,255 ,255 )

            pygame .draw .circle (screen ,color ,(cx ,cy ),r )

            pygame .draw .circle (screen ,WHITE ,(cx ,cy ),r ,3 )





        text_y =cy_center +gap +r +int (30 *s )

        line_gap =int (40 *s )



        info =f_info .render (f"Kolo: {self .round }/8 | Délka: {len (self .sequence )}",True ,YELLOW )

        screen .blit (info ,info .get_rect (center =(screen_w //2 ,text_y )))



        progress =f_small .render (f"Tvá řada: {len (self .player_sequence )}/{len (self .sequence )}",True ,CYAN )

        screen .blit (progress ,progress .get_rect (center =(screen_w //2 ,text_y +line_gap )))



        if self .waiting_for_input :

            instr =f_small .render ("Tvůj tah! Klikej na světla",True ,GREEN )

        else :

            instr =f_small .render ("Sleduj sekvenci...",True ,WHITE )

        screen .blit (instr ,instr .get_rect (center =(screen_w //2 ,text_y +2 *line_gap )))



        if self .lost :

            lose =f_title .render ("ŠPATNĚ!",True ,RED )

            screen .blit (lose ,lose .get_rect (center =(screen_w //2 ,text_y +3 *line_gap )))



    def get_hint (self ):

        return "Zapamatuj si pořadí barev!"

def get_level_class():
    return SimonSays

