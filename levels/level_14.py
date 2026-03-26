from .shared import *

class TetrisLite (BaseGame ):

    """Lehký Tetris s rotací"""



    COLS =10 

    ROWS =20 

    CELL =30 

    FALL_INTERVAL =30 

    LOCK_DELAY =30 

    LINES_TO_WIN =3 



    SHAPES ={

    "I":[

    [(0 ,0 ),(1 ,0 ),(2 ,0 ),(3 ,0 )],

    [(0 ,0 ),(0 ,1 ),(0 ,2 ),(0 ,3 )],

    ],

    "O":[

    [(0 ,0 ),(1 ,0 ),(0 ,1 ),(1 ,1 )],

    ],

    "T":[

    [(0 ,0 ),(1 ,0 ),(2 ,0 ),(1 ,1 )],

    [(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,1 )],

    [(1 ,0 ),(0 ,1 ),(1 ,1 ),(2 ,1 )],

    [(1 ,0 ),(1 ,1 ),(1 ,2 ),(0 ,1 )],

    ],

    "S":[

    [(1 ,0 ),(2 ,0 ),(0 ,1 ),(1 ,1 )],

    [(0 ,0 ),(0 ,1 ),(1 ,1 ),(1 ,2 )],

    ],

    "Z":[

    [(0 ,0 ),(1 ,0 ),(1 ,1 ),(2 ,1 )],

    [(1 ,0 ),(0 ,1 ),(1 ,1 ),(0 ,2 )],

    ],

    "L":[

    [(0 ,0 ),(0 ,1 ),(0 ,2 ),(1 ,2 )],

    [(0 ,0 ),(1 ,0 ),(2 ,0 ),(0 ,1 )],

    [(0 ,0 ),(1 ,0 ),(1 ,1 ),(1 ,2 )],

    [(2 ,0 ),(0 ,1 ),(1 ,1 ),(2 ,1 )],

    ],

    "J":[

    [(1 ,0 ),(1 ,1 ),(0 ,2 ),(1 ,2 )],

    [(0 ,0 ),(0 ,1 ),(1 ,1 ),(2 ,1 )],

    [(0 ,0 ),(1 ,0 ),(0 ,1 ),(0 ,2 )],

    [(0 ,0 ),(1 ,0 ),(2 ,0 ),(2 ,1 )],

    ],

    }



    SHAPE_COLORS ={

    "I":(0 ,255 ,255 ),

    "O":(255 ,255 ,0 ),

    "T":(128 ,0 ,128 ),

    "S":(0 ,255 ,0 ),

    "Z":(255 ,0 ,0 ),

    "L":(255 ,165 ,0 ),

    "J":(0 ,0 ,255 ),

    }



    class _Piece :

        def __init__ (self ,name ,shapes ):

            self .name =name 

            self .shapes =shapes 

            self .rot =0 

            self .x =3 

            self .y =0 



        @property 

        def cells (self ):

            return list (self .shapes [self .name ][self .rot ])



        def rotated_cells (self ,direction =1 ):

            new_rot =(self .rot +direction )%len (self .shapes [self .name ])

            return list (self .shapes [self .name ][new_rot ]),new_rot 



    def __init__ (self ):

        super ().__init__ ()



        self .grid =[[0 ]*self .COLS for _ in range (self .ROWS )]

        self .bag =[]

        self .piece =self ._spawn_piece ()

        self .next_piece_name =self ._next_from_bag ()

        self .hold_name =None 

        self .hold_used =False 

        self .lines_cleared =0 

        self .score =0 

        self .fall_timer =0 

        self .lock_timer =0 

        self .paused =False 

        self .started =False 

        self .game_over =False 





    def _next_from_bag (self ):

        if not self .bag :

            self .bag =list (self .SHAPES .keys ())

            random .shuffle (self .bag )

        return self .bag .pop ()



    def _spawn_piece (self ):

        name =self ._next_from_bag ()

        return self ._Piece (name ,self .SHAPES )





    def _valid (self ,cells ,ox ,oy ):

        for cx ,cy in cells :

            gx ,gy =ox +cx ,oy +cy 

            if gx <0 or gx >=self .COLS or gy >=self .ROWS :

                return False 

            if gy >=0 and self .grid [gy ][gx ]:

                return False 

        return True 



    def _lock_piece (self ):

        color =self .SHAPE_COLORS [self .piece .name ]

        for cx ,cy in self .piece .cells :

            gx ,gy =self .piece .x +cx ,self .piece .y +cy 

            if 0 <=gy <self .ROWS and 0 <=gx <self .COLS :

                self .grid [gy ][gx ]=color 

        self ._clear_lines ()

        self ._next_turn ()



    def _next_turn (self ):

        self .piece =self ._Piece (self .next_piece_name ,self .SHAPES )

        self .next_piece_name =self ._next_from_bag ()

        self .hold_used =False 

        self .lock_timer =0 

        self .fall_timer =0 

        if not self ._valid (self .piece .cells ,self .piece .x ,self .piece .y ):

            self .game_over =True 

            self .lost =True 



    def _clear_lines (self ):

        new_grid =[]

        cleared =0 

        for row in self .grid :

            if all (cell !=0 for cell in row ):

                cleared +=1 

            else :

                new_grid .append (row )

        for _ in range (cleared ):

            new_grid .insert (0 ,[0 ]*self .COLS )

        self .grid =new_grid 

        self .lines_cleared +=cleared 

        self .score +=[0 ,100 ,300 ,500 ,800 ][min (cleared ,4 )]

        if self .lines_cleared >=self .LINES_TO_WIN :

            self .won =True 





    def _move (self ,dx ,dy ):

        if self ._valid (self .piece .cells ,self .piece .x +dx ,self .piece .y +dy ):

            self .piece .x +=dx 

            self .piece .y +=dy 

            if dy ==0 :

                self .lock_timer =0 

            return True 

        return False 



    def _rotate (self ,direction =1 ):

        new_cells ,new_rot =self .piece .rotated_cells (direction )



        kicks =[(0 ,0 ),(-1 ,0 ),(1 ,0 ),(-2 ,0 ),(2 ,0 ),(0 ,-1 ),(0 ,-2 )]

        for kx ,ky in kicks :

            if self ._valid (new_cells ,self .piece .x +kx ,self .piece .y +ky ):

                self .piece .x +=kx 

                self .piece .y +=ky 

                self .piece .rot =new_rot 

                self .lock_timer =0 

                return True 

        return False 



    def _hold (self ):

        if self .hold_used :

            return 

        self .hold_used =True 

        if self .hold_name is None :

            self .hold_name =self .piece .name 

            self .piece =self ._Piece (self .next_piece_name ,self .SHAPES )

            self .next_piece_name =self ._next_from_bag ()

        else :

            old_hold =self .hold_name 

            self .hold_name =self .piece .name 

            self .piece =self ._Piece (old_hold ,self .SHAPES )

        self .lock_timer =0 

        self .fall_timer =0 



    def _ghost_y (self ):

        gy =self .piece .y 

        while self ._valid (self .piece .cells ,self .piece .x ,gy +1 ):

            gy +=1 

        return gy 





    def handle_event (self ,event ):

        if event .type !=pygame .KEYDOWN :

            return 





        if not self .started :

            self .started =True 

            return 



        if self .won or self .game_over :

            return 





        if event .key ==pygame .K_ESCAPE :

            self .paused =not self .paused 

            return 



        if self .paused :

            return 





        if event .key in (pygame .K_LEFT ,pygame .K_a ):

            self ._move (-1 ,0 )

        elif event .key in (pygame .K_RIGHT ,pygame .K_d ):

            self ._move (1 ,0 )

        elif event .key in (pygame .K_DOWN ,pygame .K_s ):

            if self ._move (0 ,1 ):

                self .fall_timer =0 



        elif event .key ==pygame .K_r :

            self ._rotate ()



        elif event .key in (pygame .K_c ,pygame .K_LSHIFT ,pygame .K_RSHIFT ):

            self ._hold ()





    def update (self ):

        if not self .started or self .paused or self .won or self .game_over :

            return 



        self .fall_timer +=1 

        if self .fall_timer >=self .FALL_INTERVAL :

            self .fall_timer =0 

            if not self ._move (0 ,1 ):

                self .lock_timer +=1 

                if self .lock_timer >=self .LOCK_DELAY :

                    self ._lock_piece ()

            else :

                self .lock_timer =0 

        else :



            if not self ._valid (self .piece .cells ,self .piece .x ,self .piece .y +1 ):

                self .lock_timer +=1 

                if self .lock_timer >=self .LOCK_DELAY :

                    self ._lock_piece ()





    def _draw_block (self ,screen ,x ,y ,color ,size =None ):

        s =size or self .CELL 

        rect =pygame .Rect (x ,y ,s ,s )

        pygame .draw .rect (screen ,color ,rect )



        pygame .draw .line (screen ,tuple (min (c +40 ,255 )for c in color ),(x ,y ),(x +s -1 ,y ))

        pygame .draw .line (screen ,tuple (min (c +40 ,255 )for c in color ),(x ,y ),(x ,y +s -1 ))



        pygame .draw .line (screen ,tuple (max (c -60 ,0 )for c in color ),(x ,y +s -1 ),(x +s -1 ,y +s -1 ))

        pygame .draw .line (screen ,tuple (max (c -60 ,0 )for c in color ),(x +s -1 ,y ),(x +s -1 ,y +s -1 ))



    def _draw_mini_piece (self ,screen ,name ,cx ,cy ,cell =20 ):

        if name is None :

            return 

        color =self .SHAPE_COLORS [name ]

        cells =self .SHAPES [name ][0 ]

        for bx ,by in cells :

            self ._draw_block (screen ,cx +bx *cell ,cy +by *cell ,color ,cell )



    def draw (self ,screen ):

        screen .fill ((15 ,15 ,30 ))





        if not self .started :

            t =FONT_LARGE .render ("TETRIS",True ,CYAN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,300 ))

            p =FONT_MEDIUM .render ("Press any key to start",True ,WHITE )

            screen .blit (p ,(SCREEN_WIDTH //2 -p .get_width ()//2 ,450 ))

            return 





        grid_w =self .COLS *self .CELL 

        grid_h =self .ROWS *self .CELL 

        ox =(SCREEN_WIDTH -grid_w )//2 

        oy =(SCREEN_HEIGHT -grid_h )//2 





        pygame .draw .rect (screen ,(30 ,30 ,50 ),(ox -2 ,oy -2 ,grid_w +4 ,grid_h +4 ))

        for r in range (self .ROWS ):

            for c in range (self .COLS ):

                rect =pygame .Rect (ox +c *self .CELL ,oy +r *self .CELL ,self .CELL ,self .CELL )

                if self .grid [r ][c ]:

                    self ._draw_block (screen ,rect .x ,rect .y ,self .grid [r ][c ])

                else :

                    pygame .draw .rect (screen ,(40 ,40 ,60 ),rect )

                    pygame .draw .rect (screen ,(55 ,55 ,75 ),rect ,1 )





        if not self .won and not self .game_over :

            gy =self ._ghost_y ()

            ghost_color =tuple (c //3 for c in self .SHAPE_COLORS [self .piece .name ])

            for cx ,cy in self .piece .cells :

                gx_p =ox +(self .piece .x +cx )*self .CELL 

                gy_p =oy +(gy +cy )*self .CELL 

                pygame .draw .rect (screen ,ghost_color ,(gx_p ,gy_p ,self .CELL ,self .CELL ))

                pygame .draw .rect (screen ,tuple (min (c +30 ,255 )for c in ghost_color ),

                (gx_p ,gy_p ,self .CELL ,self .CELL ),1 )





        if not self .won and not self .game_over :

            pc =self .SHAPE_COLORS [self .piece .name ]

            for cx ,cy in self .piece .cells :

                px =ox +(self .piece .x +cx )*self .CELL 

                py =oy +(self .piece .y +cy )*self .CELL 

                if py >=oy :

                    self ._draw_block (screen ,px ,py ,pc )





        pygame .draw .rect (screen ,CYAN ,(ox -2 ,oy -2 ,grid_w +4 ,grid_h +4 ),2 )





        panel_x =ox +grid_w +30 





        lbl =FONT_SMALL .render ("NEXT",True ,CYAN )

        screen .blit (lbl ,(panel_x ,oy ))

        pygame .draw .rect (screen ,(40 ,40 ,60 ),(panel_x ,oy +30 ,100 ,80 ))

        pygame .draw .rect (screen ,CYAN ,(panel_x ,oy +30 ,100 ,80 ),1 )

        self ._draw_mini_piece (screen ,self .next_piece_name ,panel_x +10 ,oy +40 )





        lbl =FONT_SMALL .render ("HOLD",True ,CYAN )

        screen .blit (lbl ,(panel_x ,oy +130 ))

        pygame .draw .rect (screen ,(40 ,40 ,60 ),(panel_x ,oy +160 ,100 ,80 ))

        pygame .draw .rect (screen ,CYAN ,(panel_x ,oy +160 ,100 ,80 ),1 )

        self ._draw_mini_piece (screen ,self .hold_name ,panel_x +10 ,oy +170 )





        lbl =FONT_SMALL .render ("SCORE",True ,CYAN )

        screen .blit (lbl ,(panel_x ,oy +270 ))

        val =FONT_MEDIUM .render (str (self .score ),True ,YELLOW )

        screen .blit (val ,(panel_x ,oy +300 ))





        lbl =FONT_SMALL .render ("LINES",True ,CYAN )

        screen .blit (lbl ,(panel_x ,oy +370 ))

        val =FONT_MEDIUM .render (f"{self .lines_cleared } / {self .LINES_TO_WIN }",True ,YELLOW )

        screen .blit (val ,(panel_x ,oy +400 ))





        ctrl_x =ox -260 

        ctrl_y =oy 

        lbl =FONT_SMALL .render ("CONTROLS",True ,CYAN )

        screen .blit (lbl ,(ctrl_x ,ctrl_y ))

        controls =[

        "A / Left  = Move Left",

        "D / Right = Move Right",

        "S / Down  = Soft Drop",

        "R         = Rotate",

        "C / Shift = Hold",

        "ESC       = Pause",

        ]

        for i ,line in enumerate (controls ):

            t =FONT_TINY .render (line ,True ,LIGHT_GRAY )

            screen .blit (t ,(ctrl_x ,ctrl_y +35 +i *28 ))





        if self .paused :

            overlay =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            overlay .fill ((0 ,0 ,0 ,150 ))

            screen .blit (overlay ,(0 ,0 ))

            t =FONT_LARGE .render ("PAUSED",True ,YELLOW )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))

            s =FONT_SMALL .render ("Press ESC to resume",True ,WHITE )

            screen .blit (s ,(SCREEN_WIDTH //2 -s .get_width ()//2 ,SCREEN_HEIGHT //2 +30 ))



        if self .won :

            overlay =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            overlay .fill ((0 ,0 ,0 ,160 ))

            screen .blit (overlay ,(0 ,0 ))

            t =FONT_LARGE .render ("YOU WIN!",True ,GREEN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))

            s =FONT_SMALL .render (f"Lines: {self .lines_cleared }  Score: {self .score }",True ,WHITE )

            screen .blit (s ,(SCREEN_WIDTH //2 -s .get_width ()//2 ,SCREEN_HEIGHT //2 +30 ))



        if self .game_over and not self .won :

            overlay =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            overlay .fill ((0 ,0 ,0 ,160 ))

            screen .blit (overlay ,(0 ,0 ))

            t =FONT_LARGE .render ("GAME OVER",True ,RED )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))

            s =FONT_SMALL .render (f"Lines: {self .lines_cleared }  Score: {self .score }",True ,WHITE )

            screen .blit (s ,(SCREEN_WIDTH //2 -s .get_width ()//2 ,SCREEN_HEIGHT //2 +30 ))



    def get_hint (self ):

        return "Vymaž 3 řady! Použij R pro rotaci, C/Shift pro hold."

def get_level_class():
    return TetrisLite

