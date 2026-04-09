from .shared import *

class ColorMatch (BaseGame ):

    """Click the correct color - can spawn multiple circles, difficulty increases"""

    def __init__ (self ):

        super ().__init__ ()

        self .colors =[RED ,GREEN ,BLUE ,YELLOW ,CYAN ]

        self .color_names ={RED :"RED",GREEN :"GREEN",BLUE :"BLUE",YELLOW :"YELLOW",CYAN :"CYAN"}

        self .target_color =random .choice (self .colors )

        self .target_name =self .color_names [self .target_color ]

        self .objects =[]

        self .score =0 

        self .lives =3 

        self .timer =0 

        self .spawn_timer =0 

        self .spawn_rate =20 

        self .round_timer =0 

        self .round_time =1800 

        self .generate_objects ()



    def generate_objects (self ):

        """Generate random colored objects moving in all directions - difficulty increases over time"""



        difficulty_multiplier =1 +(self .round_timer /self .round_time )*0.5 

        current_spawn_rate =int (self .spawn_rate /difficulty_multiplier )



        if self .spawn_timer <=0 :

            color =random .choice (self .colors )

            x =random .randint (200 ,SCREEN_WIDTH -200 )

            y =random .randint (250 ,SCREEN_HEIGHT -150 )

            size =random .randint (40 ,80 )

            lifetime =120 



            angle =random .uniform (0 ,2 *math .pi )

            speed =random .uniform (2.0 ,4.0 )*difficulty_multiplier 

            vx =speed *math .cos (angle )

            vy =speed *math .sin (angle )

            self .objects .append ({"x":x ,"y":y ,"size":size ,"color":color ,"lifetime":lifetime ,"vx":vx ,"vy":vy })

            self .spawn_timer =current_spawn_rate 

        self .spawn_timer -=1 





        for obj in self .objects :

            obj ["x"]+=obj ["vx"]

            obj ["y"]+=obj ["vy"]



            if obj ["x"]-obj ["size"]<0 or obj ["x"]+obj ["size"]>SCREEN_WIDTH :

                obj ["vx"]*=-1 

                obj ["x"]=max (obj ["size"],min (SCREEN_WIDTH -obj ["size"],obj ["x"]))

            if obj ["y"]-obj ["size"]<100 or obj ["y"]+obj ["size"]>SCREEN_HEIGHT -150 :

                obj ["vy"]*=-1 

                obj ["y"]=max (100 +obj ["size"],min (SCREEN_HEIGHT -150 -obj ["size"],obj ["y"]))





        self .objects =[o for o in self .objects if o ["lifetime"]>0 ]

        for obj in self .objects :

            obj ["lifetime"]-=1 



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN :

            pos =event .pos 

            clicked =False 

            for obj in self .objects [:]:

                dist =math .sqrt ((obj ["x"]-pos [0 ])**2 +(obj ["y"]-pos [1 ])**2 )

                if dist <obj ["size"]:

                    clicked =True 

                    if obj ["color"]==self .target_color :

                        self .score +=1 

                    else :

                        self .lives -=1 

                    self .objects .remove (obj )

                    break 



            if self .lives <=0 :

                self .lost =True 



    def update (self ):

        self .generate_objects ()

        self .timer +=1 

        self .round_timer +=1 



        if self .round_timer >self .round_time :

            if self .score >5 :

                self .won =True 

            else :

                self .lost =True 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )



        title =FONT_LARGE .render ("COLOR MATCH",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -180 ,20 ))



        target_text =FONT_LARGE .render (f"CLICK {self .target_name }",True ,self .target_color )

        screen .blit (target_text ,(SCREEN_WIDTH //2 -280 ,100 ))





        for obj in self .objects :

            pygame .draw .circle (screen ,obj ["color"],(int (obj ["x"]),int (obj ["y"])),obj ["size"])

            pygame .draw .circle (screen ,WHITE ,(int (obj ["x"]),int (obj ["y"])),obj ["size"],3 )





        score_text =FONT_MEDIUM .render (f"Score: {self .score }",True ,GREEN )

        lives_text =FONT_MEDIUM .render (f"Lives: {self .lives }",True ,RED )

        screen .blit (score_text ,(50 ,50 ))

        screen .blit (lives_text ,(SCREEN_WIDTH -250 ,50 ))



        time_left =max (0 ,(self .round_time -self .round_timer )//60 )

        time_text =FONT_SMALL .render (f"Time: {time_left }s",True ,YELLOW )

        screen .blit (time_text ,(SCREEN_WIDTH //2 -80 ,150 ))



    def get_hint (self ):

        return f"Click on {self .target_name } circles - avoid others! Get 6+ points to win!"

def get_level_class():
    return ColorMatch

