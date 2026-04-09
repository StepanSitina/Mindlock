from .shared import *

class LaserMirrors (BaseGame ):

    """Laser Reflection Puzzle – nasměruj laser na cíl otáčením zrcadel na mřížce.

    Advanced version with portals, 14 mirrors, and a winding 10-bounce solution."""





    G_COLS =12 

    G_ROWS =10 

    CELL =56 





    DIRS =[(1 ,0 ),(0 ,1 ),(-1 ,0 ),(0 ,-1 )]



    def __init__ (self ):

        super ().__init__ ()





        self .cx =6 

        self .cy =5 





















































        self .emitter =(0 ,1 )

        self .emit_dir =0 





        self .target =(11 ,6 )





        self .grid =[[None ]*self .G_COLS for _ in range (self .G_ROWS )]





        walls =[

        (2 ,0 ),(6 ,0 ),(9 ,0 ),

        (2 ,2 ),(6 ,2 ),

        (3 ,3 ),(6 ,3 ),(9 ,3 ),

        (1 ,4 ),

        (3 ,5 ),(8 ,5 ),

        (0 ,6 ),

        (3 ,7 ),(6 ,7 ),(7 ,7 ),

        (0 ,8 ),(3 ,8 ),(8 ,8 ),

        (9 ,9 ),(11 ,9 ),

        ]

        for wx ,wy in walls :

            self .grid [wy ][wx ]="block"





        self .grid [4 ][10 ]={"type":"portal","pair":(1 ,7 ),"id":"A"}

        self .grid [7 ][1 ]={"type":"portal","pair":(10 ,4 ),"id":"A"}





        solution_mirrors =[

        (4 ,1 ,"/"),

        (4 ,4 ,"/"),

        (7 ,4 ,"\\"),

        (7 ,1 ,"\\"),

        (10 ,1 ,"/"),

        (1 ,9 ,"/"),

        (5 ,9 ,"\\"),

        (5 ,6 ,"\\"),

        ]



        decoy_mirrors =[

        (2 ,3 ,"/"),

        (8 ,2 ,"\\"),

        (9 ,7 ,"/"),

        (3 ,6 ,"\\"),

        (11 ,3 ,"/"),

        (6 ,8 ,"\\"),

        ]

        for mx ,my ,angle in solution_mirrors +decoy_mirrors :

            self .grid [my ][mx ]={"type":"mirror","angle":angle }





        self .laser_path =[]

        self .hit_target =False 

        self ._trace_laser ()









    def _reflect (self ,dir_idx ,angle ):

        """Return new direction index after hitting a mirror of given angle."""

        if angle =="/":



            return [3 ,2 ,1 ,0 ][dir_idx ]

        else :



            return [1 ,0 ,3 ,2 ][dir_idx ]



    def _trace_laser (self ):

        """Trace the laser beam from the emitter through the grid."""

        self .laser_path =[]

        self .hit_target =False 



        x ,y =self .emitter 

        d =self .emit_dir 

        visited =set ()



        for _ in range (300 ):

            state =(x ,y ,d )

            if state in visited :

                break 

            visited .add (state )



            self .laser_path .append ((x ,y ))





            if (x ,y )==self .target :

                self .hit_target =True 

                break 





            cell =self .grid [y ][x ]

            if cell =="block":

                break 



            if isinstance (cell ,dict ):

                if cell ["type"]=="mirror":

                    d =self ._reflect (d ,cell ["angle"])

                elif cell ["type"]=="portal":



                    px ,py =cell ["pair"]

                    self .laser_path .append ((px ,py ))

                    x ,y =px ,py 

                    dx ,dy =self .DIRS [d ]

                    nx ,ny =x +dx ,y +dy 

                    if nx <0 or nx >=self .G_COLS or ny <0 or ny >=self .G_ROWS :

                        break 

                    x ,y =nx ,ny 

                    continue 





            dx ,dy =self .DIRS [d ]

            nx ,ny =x +dx ,y +dy 

            if nx <0 or nx >=self .G_COLS or ny <0 or ny >=self .G_ROWS :

                break 

            x ,y =nx ,ny 



        if self .hit_target :

            self .won =True 









    def handle_event (self ,event ):

        if event .type !=pygame .KEYDOWN :

            return 

        if self .won :

            return 





        if event .key in (pygame .K_LEFT ,pygame .K_a ):

            self .cx =max (0 ,self .cx -1 )

        elif event .key in (pygame .K_RIGHT ,pygame .K_d ):

            self .cx =min (self .G_COLS -1 ,self .cx +1 )

        elif event .key in (pygame .K_UP ,pygame .K_w ):

            self .cy =max (0 ,self .cy -1 )

        elif event .key in (pygame .K_DOWN ,pygame .K_s ):

            self .cy =min (self .G_ROWS -1 ,self .cy +1 )





        elif event .key ==pygame .K_r :

            cell =self .grid [self .cy ][self .cx ]

            if isinstance (cell ,dict )and cell ["type"]=="mirror":

                cell ["angle"]="\\"if cell ["angle"]=="/"else "/"

                self ._trace_laser ()









    def draw (self ,screen ):

        screen .fill ((10 ,10 ,25 ))





        ox =(SCREEN_WIDTH -self .G_COLS *self .CELL )//2 

        oy =(SCREEN_HEIGHT -self .G_ROWS *self .CELL )//2 





        for gy in range (self .G_ROWS ):

            for gx in range (self .G_COLS ):

                rx =ox +gx *self .CELL 

                ry =oy +gy *self .CELL 

                rect =pygame .Rect (rx ,ry ,self .CELL ,self .CELL )



                cell =self .grid [gy ][gx ]



                if cell =="block":

                    pygame .draw .rect (screen ,(80 ,80 ,100 ),rect )

                    pygame .draw .rect (screen ,(120 ,120 ,140 ),rect ,2 )

                else :

                    pygame .draw .rect (screen ,(25 ,25 ,45 ),rect )

                    pygame .draw .rect (screen ,(45 ,45 ,65 ),rect ,1 )





                if isinstance (cell ,dict )and cell ["type"]=="mirror":

                    pad =8 

                    if cell ["angle"]=="/":

                        pygame .draw .line (screen ,YELLOW ,

                        (rx +pad ,ry +self .CELL -pad ),

                        (rx +self .CELL -pad ,ry +pad ),4 )

                    else :

                        pygame .draw .line (screen ,YELLOW ,

                        (rx +pad ,ry +pad ),

                        (rx +self .CELL -pad ,ry +self .CELL -pad ),4 )





                if isinstance (cell ,dict )and cell ["type"]=="portal":

                    cx_p =rx +self .CELL //2 

                    cy_p =ry +self .CELL //2 

                    pygame .draw .circle (screen ,(180 ,0 ,255 ),(cx_p ,cy_p ),

                    self .CELL //3 ,3 )

                    pygame .draw .circle (screen ,(220 ,100 ,255 ),(cx_p ,cy_p ),

                    self .CELL //5 )

                    lbl =FONT_TINY .render ("P",True ,WHITE )

                    screen .blit (lbl ,(cx_p -lbl .get_width ()//2 ,

                    cy_p -lbl .get_height ()//2 ))





        ex =ox +self .emitter [0 ]*self .CELL +self .CELL //2 

        ey =oy +self .emitter [1 ]*self .CELL +self .CELL //2 

        pygame .draw .circle (screen ,GREEN ,(ex ,ey ),14 )

        lbl =FONT_TINY .render ("L",True ,BLACK )

        screen .blit (lbl ,(ex -lbl .get_width ()//2 ,ey -lbl .get_height ()//2 ))





        tx =ox +self .target [0 ]*self .CELL +self .CELL //2 

        ty =oy +self .target [1 ]*self .CELL +self .CELL //2 

        pygame .draw .circle (screen ,RED ,(tx ,ty ),14 )

        lbl =FONT_TINY .render ("T",True ,WHITE )

        screen .blit (lbl ,(tx -lbl .get_width ()//2 ,ty -lbl .get_height ()//2 ))





        beam_color =(0 ,255 ,100 )if self .hit_target else (0 ,200 ,255 )

        glow_color =(100 ,255 ,180 )if self .hit_target else (120 ,230 ,255 )

        for i in range (len (self .laser_path )-1 ):

            ax ,ay =self .laser_path [i ]

            bx ,by =self .laser_path [i +1 ]



            if abs (ax -bx )+abs (ay -by )>1 :

                continue 

            p1 =(ox +ax *self .CELL +self .CELL //2 ,

            oy +ay *self .CELL +self .CELL //2 )

            p2 =(ox +bx *self .CELL +self .CELL //2 ,

            oy +by *self .CELL +self .CELL //2 )

            pygame .draw .line (screen ,beam_color ,p1 ,p2 ,4 )

            pygame .draw .line (screen ,glow_color ,p1 ,p2 ,2 )





        cur_rect =pygame .Rect (ox +self .cx *self .CELL ,oy +self .cy *self .CELL ,

        self .CELL ,self .CELL )

        pygame .draw .rect (screen ,WHITE ,cur_rect ,3 )





        title =FONT_MEDIUM .render ("LASER REFLECTION",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -title .get_width ()//2 ,20 ))





        mirror_count =sum (1 for row in self .grid for c in row 

        if isinstance (c ,dict )and c .get ("type")=="mirror")

        info =FONT_TINY .render (

        f"ZRCADEL: {mirror_count }  |  PORTÁLY: 1 pár",True ,(180 ,180 ,200 ))

        screen .blit (info ,(SCREEN_WIDTH //2 -info .get_width ()//2 ,60 ))





        instr =FONT_TINY .render (

        "ŠIPKY/WASD = pohyb  |  R = otočit zrcadlo  |  "

        "Nasměruj laser přes portály na cíl!",True ,LIGHT_GRAY )

        screen .blit (instr ,(SCREEN_WIDTH //2 -instr .get_width ()//2 ,SCREEN_HEIGHT -40 ))





        if self .won :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render ("LASER NA CÍLI!",True ,GREEN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))



    def get_hint (self ):

        return "Otoč SPRÁVNÁ zrcadla a nasměruj laser přes portály na cíl. Pozor – některá zrcadla jsou návnady!"

def get_level_class():
    return LaserMirrors

