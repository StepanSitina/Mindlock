from .shared import *

class RollingBalls (BaseGame ):

    """Rolling Balls – 5 sub-levels, resolution-adaptive grid puzzle.

    Ball slides until hitting a wall. Holes kill, switches open gates."""





    LEVELS =[

    {

    "grid":[

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    ],

    "switch_gate":{},

    "ball":(1 ,1 ),"goal":(8 ,6 ),"max_moves":30 ,

    },

    {

    "grid":[

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,0 ,1 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    ],

    "switch_gate":{},

    "ball":(1 ,1 ),"goal":(8 ,6 ),"max_moves":35 ,

    },

    {

    "grid":[

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,3 ,0 ,1 ,0 ,1 ],

    [1 ,0 ,0 ,1 ,1 ,1 ,4 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,1 ,0 ,1 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    ],

    "switch_gate":{(5 ,3 ):(6 ,4 )},

    "ball":(1 ,1 ),"goal":(8 ,5 ),"max_moves":40 ,

    },

    {

    "grid":[

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,3 ,0 ,1 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,4 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,0 ,0 ,1 ,0 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    ],

    "switch_gate":{(5 ,2 ):(6 ,3 )},

    "ball":(1 ,1 ),"goal":(8 ,6 ),"max_moves":30 ,

    },

    {

    "grid":[

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,1 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,3 ,0 ,0 ,1 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,4 ,1 ,1 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,0 ,1 ,0 ,0 ,0 ,0 ,3 ,0 ,1 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,4 ,1 ,1 ,1 ],

    [1 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ],

    [1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ],

    ],

    "switch_gate":{(5 ,2 ):(6 ,3 ),(7 ,5 ):(8 ,6 )},

    "ball":(1 ,1 ),"goal":(10 ,7 ),"max_moves":35 ,

    },

    ]



    def __init__ (self ):

        super ().__init__ ()

        self .sub_level =0 

        self ._load_sub_level (0 )



    def _load_sub_level (self ,idx ):

        """Load sub-level by index, deep-copy grid so restarts work."""

        data =self .LEVELS [idx ]

        self .sub_level =idx 

        self .ROWS =len (data ["grid"])

        self .COLS =len (data ["grid"][0 ])

        self .grid =[row [:]for row in data ["grid"]]

        self .switch_gate =dict (data ["switch_gate"])

        self .ball_x ,self .ball_y =data ["ball"]

        self .goal_x ,self .goal_y =data ["goal"]

        self .max_moves =data ["max_moves"]

        self .moves =0 

        self .won =False 

        self .lost =False 





    def _slide (self ,dx ,dy ):

        if self .won or self .lost :

            return 

        moved =False 

        while True :

            nx =self .ball_x +dx 

            ny =self .ball_y +dy 

            if nx <0 or nx >=self .COLS or ny <0 or ny >=self .ROWS :

                break 

            cell =self .grid [ny ][nx ]

            if cell ==1 or cell ==4 :

                break 

            self .ball_x =nx 

            self .ball_y =ny 

            moved =True 

            if cell ==2 :

                self .lost =True 

                return 

            if cell in (3 ,6 ):

                if (nx ,ny )in self .switch_gate :

                    gx ,gy =self .switch_gate [(nx ,ny )]

                    if self .grid [gy ][gx ]==4 :

                        self .grid [gy ][gx ]=5 

                        self .grid [ny ][nx ]=6 

                    else :

                        self .grid [gy ][gx ]=4 

                        self .grid [ny ][nx ]=3 

            if self .ball_x ==self .goal_x and self .ball_y ==self .goal_y :

                self .won =True 

                return 

        if moved :

            self .moves +=1 

            if self .moves >=self .max_moves :

                self .lost =True 





    def handle_event (self ,event ):

        if event .type !=pygame .KEYDOWN :

            return 



        if event .key ==pygame .K_r :

            self ._load_sub_level (self .sub_level )

            return 



        if self .won :

            if event .key ==pygame .K_RETURN :

                if self .sub_level +1 <len (self .LEVELS ):

                    self ._load_sub_level (self .sub_level +1 )

                else :

                    pass 

            return 

        if self .lost :

            if event .key ==pygame .K_RETURN :

                self ._load_sub_level (self .sub_level )

            return 

        if event .key in (pygame .K_LEFT ,pygame .K_a ):

            self ._slide (-1 ,0 )

        elif event .key in (pygame .K_RIGHT ,pygame .K_d ):

            self ._slide (1 ,0 )

        elif event .key in (pygame .K_UP ,pygame .K_w ):

            self ._slide (0 ,-1 )

        elif event .key in (pygame .K_DOWN ,pygame .K_s ):

            self ._slide (0 ,1 )



    def is_won (self ):

        return self .won and self .sub_level ==len (self .LEVELS )-1 





    def draw (self ,screen ):

        sw ,sh =screen .get_size ()

        scale =min (sw /900 ,sh /700 )

        screen .fill ((10 ,15 ,30 ))





        f_large =pygame .font .Font (None ,max (16 ,int (64 *scale )))

        f_med =pygame .font .Font (None ,max (14 ,int (40 *scale )))

        f_small =pygame .font .Font (None ,max (12 ,int (28 *scale )))

        f_tiny =pygame .font .Font (None ,max (10 ,int (20 *scale )))





        title =f_large .render ("ROLLING BALLS",True ,CYAN )

        title_y =int (12 *scale )

        screen .blit (title ,(sw //2 -title .get_width ()//2 ,title_y ))





        info =f_small .render (

        f"Level: {self .sub_level +1 }/{len (self .LEVELS )}   Tahy: {self .moves }/{self .max_moves }",

        True ,RED if self .moves >=self .max_moves -3 else WHITE )

        info_y =title_y +title .get_height ()+int (6 *scale )

        screen .blit (info ,(sw //2 -info .get_width ()//2 ,info_y ))





        header_h =info_y +info .get_height ()+int (10 *scale )

        footer_h =int (50 *scale )

        avail_w =sw -int (40 *scale )

        avail_h =sh -header_h -footer_h 

        cell =min (avail_w //self .COLS ,avail_h //self .ROWS ,int (60 *scale ))

        cell =max (cell ,16 )



        ox =(sw -self .COLS *cell )//2 

        oy =header_h +(avail_h -self .ROWS *cell )//2 



        colors ={

        0 :(30 ,30 ,55 ),1 :(80 ,80 ,100 ),2 :(20 ,20 ,20 ),

        3 :(200 ,200 ,0 ),4 :(140 ,50 ,50 ),5 :(50 ,140 ,50 ),

        6 :(100 ,255 ,100 ),

        }

        r_hole =max (4 ,int (cell *0.28 ))

        r_goal =max (4 ,int (cell *0.28 ))

        r_ball =max (5 ,int (cell *0.31 ))



        for gy in range (self .ROWS ):

            for gx in range (self .COLS ):

                rx =ox +gx *cell 

                ry =oy +gy *cell 

                c =self .grid [gy ][gx ]

                rect =pygame .Rect (rx ,ry ,cell ,cell )

                pygame .draw .rect (screen ,colors .get (c ,(30 ,30 ,55 )),rect )

                pygame .draw .rect (screen ,(50 ,50 ,70 ),rect ,1 )

                cx ,cy =rx +cell //2 ,ry +cell //2 

                if c ==2 :

                    pygame .draw .circle (screen ,(40 ,0 ,0 ),(cx ,cy ),r_hole )

                elif c in (3 ,6 ):

                    lbl =f_tiny .render ("SW",True ,BLACK )

                    screen .blit (lbl ,lbl .get_rect (center =(cx ,cy )))

                elif c ==4 :

                    lbl =f_tiny .render ("GATE",True ,WHITE )

                    screen .blit (lbl ,lbl .get_rect (center =(cx ,cy )))

                elif c ==5 :

                    lbl =f_tiny .render ("OPEN",True ,BLACK )

                    screen .blit (lbl ,lbl .get_rect (center =(cx ,cy )))





        gcx =ox +self .goal_x *cell +cell //2 

        gcy =oy +self .goal_y *cell +cell //2 

        pygame .draw .circle (screen ,(255 ,215 ,0 ),(gcx ,gcy ),r_goal )

        gl =f_tiny .render ("CIL",True ,BLACK )

        screen .blit (gl ,gl .get_rect (center =(gcx ,gcy )))





        bx =ox +self .ball_x *cell +cell //2 

        by =oy +self .ball_y *cell +cell //2 

        pygame .draw .circle (screen ,(0 ,180 ,255 ),(bx ,by ),r_ball )

        pygame .draw .circle (screen ,WHITE ,(bx ,by ),r_ball ,2 )





        instr =f_tiny .render (

        "SIPKY/WASD = pohyb  |  R = restart  |  Vyhni se diram!",True ,LIGHT_GRAY )

        screen .blit (instr ,(sw //2 -instr .get_width ()//2 ,sh -int (38 *scale )))





        if self .won or self .lost :

            ov =pygame .Surface ((sw ,sh ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            if self .won :

                if self .sub_level +1 <len (self .LEVELS ):

                    msg =f"LEVEL {self .sub_level +1 } HOTOVO!"

                    sub ="ENTER = dalsi level"

                else :

                    msg ="MICEK V CILI!"

                    sub ="Vsechny levely hotovy!"

                t =f_large .render (msg ,True ,GREEN )

            else :

                reason ="SPADL DO DIRY!"if self .grid [self .ball_y ][self .ball_x ]==2 else "PRILIS MNOHO TAHU!"

                t =f_large .render (reason ,True ,RED )

                sub ="ENTER = restart"

            screen .blit (t ,(sw //2 -t .get_width ()//2 ,sh //2 -int (40 *scale )))

            s =f_small .render (sub ,True ,YELLOW )

            screen .blit (s ,(sw //2 -s .get_width ()//2 ,sh //2 +int (30 *scale )))



    def get_hint (self ):

        return "Micek se klouze az narazi na zed. Aktivuj prepinac a vyhni se diram!"

def get_level_class():
    return RollingBalls

