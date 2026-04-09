from .shared import *

class PipeRotate (BaseGame ):

    """

    Pipe Puzzle – 8×8 grid.  Rotate pipes so a continuous path connects

    the green START node to the red END node.

    Left-click = rotate clockwise 90°.  Right-click = rotate counter-clockwise.

    Locked pipes (shown with a padlock dot) cannot be rotated.

    """







    PIPE_DEFS ={

    "straight":frozenset ([0 ,2 ]),

    "curve":frozenset ([0 ,1 ]),

    "t_junc":frozenset ([0 ,1 ,2 ]),

    "cross":frozenset ([0 ,1 ,2 ,3 ]),

    "dead":frozenset ([0 ]),

    }



    OPPOSITE ={0 :2 ,1 :3 ,2 :0 ,3 :1 }

    DIR_DELTA ={0 :(1 ,0 ),1 :(0 ,1 ),2 :(-1 ,0 ),3 :(0 ,-1 )}



    GRID_COLS =8 

    GRID_ROWS =8 

    CELL =80 



    def __init__ (self ):

        super ().__init__ ()

        self .moves =0 

        self .start =(0 ,0 )

        self .end =(7 ,7 )





        self .grid =[[None ]*self .GRID_COLS for _ in range (self .GRID_ROWS )]

        self ._build_puzzle ()









    def _build_puzzle (self ):

        """

        1. Carve a random path from START to END (DFS on the grid).

        2. Assign pipe types that match the path's shape.

        3. Fill remaining empty cells with random pipes.

        4. Lock a few pipes on the solution path as hints.

        5. Scramble every unlocked pipe rotation so the player has work to do.

        """

        path =self ._random_path (self .start ,self .end )





        for idx ,(cx ,cy )in enumerate (path ):

            needed =set ()

            if idx >0 :

                px ,py =path [idx -1 ]

                needed .add (self ._side_towards (cx ,cy ,px ,py ))

            if idx <len (path )-1 :

                nx ,ny =path [idx +1 ]

                needed .add (self ._side_towards (cx ,cy ,nx ,ny ))



            pipe_type ,rotation =self ._best_pipe (needed )

            self .grid [cy ][cx ]={

            "type":pipe_type ,

            "rot":rotation ,

            "locked":False ,

            }





        types_pool =["straight","curve","t_junc","dead"]

        for r in range (self .GRID_ROWS ):

            for c in range (self .GRID_COLS ):

                if self .grid [r ][c ]is None :

                    self .grid [r ][c ]={

                    "type":random .choice (types_pool ),

                    "rot":random .randint (0 ,3 ),

                    "locked":False ,

                    }





        lock_indices ={0 ,len (path )-1 }

        mid_indices =list (range (1 ,len (path )-1 ))

        random .shuffle (mid_indices )

        for li in mid_indices [:3 ]:

            lock_indices .add (li )

        for li in lock_indices :

            cx ,cy =path [li ]

            self .grid [cy ][cx ]["locked"]=True 





        for r in range (self .GRID_ROWS ):

            for c in range (self .GRID_COLS ):

                cell =self .grid [r ][c ]

                if not cell ["locked"]:

                    cell ["rot"]=random .randint (0 ,3 )





    def _random_path (self ,start ,end ):

        """DFS-based random walk from start to end, visiting cells at most once."""

        sx ,sy =start 

        ex ,ey =end 

        visited =set ()

        visited .add ((sx ,sy ))

        path =[(sx ,sy )]



        def dfs (x ,y ):

            if (x ,y )==(ex ,ey ):

                return True 

            neighbours =[(x +1 ,y ),(x -1 ,y ),(x ,y +1 ),(x ,y -1 )]

            random .shuffle (neighbours )

            for nx ,ny in neighbours :

                if 0 <=nx <self .GRID_COLS and 0 <=ny <self .GRID_ROWS and (nx ,ny )not in visited :

                    visited .add ((nx ,ny ))

                    path .append ((nx ,ny ))

                    if dfs (nx ,ny ):

                        return True 

                    path .pop ()

                    visited .discard ((nx ,ny ))

            return False 



        dfs (sx ,sy )

        return path 



    @staticmethod 

    def _side_towards (cx ,cy ,tx ,ty ):

        """Return the side index of (cx,cy) that faces (tx,ty)."""

        dx ,dy =tx -cx ,ty -cy 

        if dx ==1 :return 0 

        if dy ==1 :return 1 

        if dx ==-1 :return 2 

        return 3 



    def _best_pipe (self ,needed_sides ):

        """

        Choose the simplest pipe type whose base openings can be rotated

        to cover *exactly* the needed_sides set.  Returns (type, rotation).

        """



        preference =["dead","straight","curve","t_junc","cross"]

        for ptype in preference :

            base =self .PIPE_DEFS [ptype ]

            for rot in range (4 ):

                rotated =frozenset ((s +rot )%4 for s in base )

                if needed_sides <=rotated and len (rotated )-len (needed_sides )<=1 :

                    return ptype ,rot 



        return "cross",0 









    def _openings (self ,cell ):

        """Return set of open sides for a cell dict."""

        base =self .PIPE_DEFS .get (cell ["type"],frozenset ())

        return frozenset ((s +cell ["rot"])%4 for s in base )









    def _find_connected_path (self ):

        """BFS from START.  Returns the set of connected cells and whether END is reached."""

        sx ,sy =self .start 

        visited =set ()

        queue =deque ([(sx ,sy )])

        visited .add ((sx ,sy ))



        while queue :

            x ,y =queue .popleft ()

            cell =self .grid [y ][x ]

            for side in self ._openings (cell ):

                dx ,dy =self .DIR_DELTA [side ]

                nx ,ny =x +dx ,y +dy 

                if 0 <=nx <self .GRID_COLS and 0 <=ny <self .GRID_ROWS and (nx ,ny )not in visited :

                    neighbour =self .grid [ny ][nx ]

                    if self .OPPOSITE [side ]in self ._openings (neighbour ):

                        visited .add ((nx ,ny ))

                        queue .append ((nx ,ny ))



        return visited ,self .end in visited 









    def handle_event (self ,event ):

        if self .won :

            return 

        if event .type not in (pygame .MOUSEBUTTONDOWN ,):

            return 



        mx ,my =event .pos 

        ox =(SCREEN_WIDTH -self .GRID_COLS *self .CELL )//2 

        oy =(SCREEN_HEIGHT -self .GRID_ROWS *self .CELL )//2 



        col =(mx -ox )//self .CELL 

        row =(my -oy )//self .CELL 

        if not (0 <=col <self .GRID_COLS and 0 <=row <self .GRID_ROWS ):

            return 



        cell =self .grid [row ][col ]

        if cell ["locked"]:

            return 





        if event .button ==1 :

            cell ["rot"]=(cell ["rot"]+1 )%4 

        elif event .button ==3 :

            cell ["rot"]=(cell ["rot"]-1 )%4 

        else :

            return 



        self .moves +=1 





        _ ,reached =self ._find_connected_path ()

        if reached :

            self .won =True 









    def _draw_pipe (self ,screen ,rx ,ry ,cell ,color ):

        """Draw the pipe shape inside the cell rect (rx, ry)."""

        cx =rx +self .CELL //2 

        cy =ry +self .CELL //2 

        half =self .CELL //2 -6 

        thick =10 



        openings =self ._openings (cell )



        ends ={

        0 :(cx +half ,cy ),

        1 :(cx ,cy +half ),

        2 :(cx -half ,cy ),

        3 :(cx ,cy -half ),

        }

        for side in openings :

            ex ,ey =ends [side ]

            pygame .draw .line (screen ,color ,(cx ,cy ),(ex ,ey ),thick )





        pygame .draw .circle (screen ,color ,(cx ,cy ),thick //2 +2 )









    def draw (self ,screen ):

        screen .fill ((10 ,12 ,28 ))



        ox =(SCREEN_WIDTH -self .GRID_COLS *self .CELL )//2 

        oy =(SCREEN_HEIGHT -self .GRID_ROWS *self .CELL )//2 





        connected ,goal_reached =self ._find_connected_path ()





        for r in range (self .GRID_ROWS ):

            for c in range (self .GRID_COLS ):

                rx =ox +c *self .CELL 

                ry =oy +r *self .CELL 

                rect =pygame .Rect (rx ,ry ,self .CELL ,self .CELL )

                cell =self .grid [r ][c ]





                bg =(30 ,32 ,50 )if not cell ["locked"]else (45 ,40 ,55 )

                pygame .draw .rect (screen ,bg ,rect )

                pygame .draw .rect (screen ,(55 ,58 ,80 ),rect ,1 )





                pipe_col =(0 ,220 ,100 )if (c ,r )in connected else (200 ,200 ,60 )

                self ._draw_pipe (screen ,rx ,ry ,cell ,pipe_col )





                if cell ["locked"]:

                    pygame .draw .circle (screen ,WHITE ,(rx +self .CELL -12 ,ry +12 ),5 )





        sx =ox +self .start [0 ]*self .CELL +self .CELL //2 

        sy =oy +self .start [1 ]*self .CELL +self .CELL //2 

        pygame .draw .circle (screen ,GREEN ,(sx ,sy ),14 )

        lbl =FONT_TINY .render ("S",True ,BLACK )

        screen .blit (lbl ,(sx -lbl .get_width ()//2 ,sy -lbl .get_height ()//2 ))



        ex_px =ox +self .end [0 ]*self .CELL +self .CELL //2 

        ey_px =oy +self .end [1 ]*self .CELL +self .CELL //2 

        pygame .draw .circle (screen ,RED ,(ex_px ,ey_px ),14 )

        lbl =FONT_TINY .render ("E",True ,WHITE )

        screen .blit (lbl ,(ex_px -lbl .get_width ()//2 ,ey_px -lbl .get_height ()//2 ))





        pygame .draw .rect (screen ,CYAN ,(ox -2 ,oy -2 ,

        self .GRID_COLS *self .CELL +4 ,

        self .GRID_ROWS *self .CELL +4 ),2 )





        t =FONT_MEDIUM .render ("PIPE PUZZLE",True ,CYAN )

        screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,15 ))





        mv =FONT_SMALL .render (f"Tahy: {self .moves }",True ,YELLOW )

        screen .blit (mv ,(ox ,oy -40 ))





        if goal_reached :

            st =FONT_SMALL .render ("SPOJENO!",True ,GREEN )

        else :

            st =FONT_SMALL .render (f"Propojeno: {len (connected )} políček",True ,LIGHT_GRAY )

        screen .blit (st ,(ox +self .GRID_COLS *self .CELL -st .get_width (),oy -40 ))





        instr =FONT_TINY .render ("Levé kliknutí = otočit CW | Pravé kliknutí = otočit CCW | "

        "Bílá tečka = zamčené",True ,LIGHT_GRAY )

        screen .blit (instr ,(SCREEN_WIDTH //2 -instr .get_width ()//2 ,SCREEN_HEIGHT -35 ))





        if self .won :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            w =FONT_LARGE .render ("LEVEL COMPLETE!",True ,GREEN )

            screen .blit (w ,(SCREEN_WIDTH //2 -w .get_width ()//2 ,SCREEN_HEIGHT //2 -50 ))

            m =FONT_SMALL .render (f"Tahy: {self .moves }",True ,WHITE )

            screen .blit (m ,(SCREEN_WIDTH //2 -m .get_width ()//2 ,SCREEN_HEIGHT //2 +20 ))



    def get_hint (self ):

        return "Otáčej potrubí kliknutím – spoj zelenou S a červenou E! Zamčené trubky jsou nápověda."

def get_level_class():
    return PipeRotate

