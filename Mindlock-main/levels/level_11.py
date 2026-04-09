from .shared import *

class Maze (BaseGame ):

    """Grid-based maze - hráč se pohybuje po mřížce, 21x25 (lichá čísla pro DFS)"""

    def __init__ (self ):

        super ().__init__ ()

        self .CELL_SIZE =32 

        self .COLS =25 

        self .ROWS =21 





        self .player_row =1 

        self .player_col =1 

        self .goal_row =self .ROWS -2 

        self .goal_col =self .COLS -2 





        self .grid =self ._generate_solvable_maze ()









    def _generate_solvable_maze (self ):

        """

        Generates mazes until one passes the BFS reachability check.

        With a correct DFS carve this always succeeds on the first try,

        but the loop acts as a safety net.

        """

        for _ in range (100 ):

            maze =self ._generate_maze_dfs ()

            if self ._bfs_path_exists (maze ,self .player_row ,self .player_col ,

            self .goal_row ,self .goal_col ):

                return maze 



        return self ._fallback_maze ()









    def _generate_maze_dfs (self ):

        """

        Iterative DFS (recursive backtracking) maze generation.

        Works on odd-indexed cells (rooms).  Even-indexed cells between

        two rooms are carved to form passages.



        1 = path (walkable)   0 = wall

        """

        rows =self .ROWS 

        cols =self .COLS 





        maze =[[0 ]*cols for _ in range (rows )]





        start_r ,start_c =1 ,1 

        maze [start_r ][start_c ]=1 

        stack =[(start_r ,start_c )]



        directions =[(-2 ,0 ),(2 ,0 ),(0 ,-2 ),(0 ,2 )]



        while stack :

            r ,c =stack [-1 ]





            neighbours =[]

            for dr ,dc in directions :

                nr ,nc =r +dr ,c +dc 

                if 1 <=nr <rows -1 and 1 <=nc <cols -1 and maze [nr ][nc ]==0 :

                    neighbours .append ((nr ,nc ,dr ,dc ))



            if neighbours :

                nr ,nc ,dr ,dc =random .choice (neighbours )



                maze [r +dr //2 ][c +dc //2 ]=1 

                maze [nr ][nc ]=1 

                stack .append ((nr ,nc ))

            else :

                stack .pop ()



        return maze 









    def _bfs_path_exists (self ,maze ,sr ,sc ,gr ,gc ):

        """Return True if a walkable path exists from (sr,sc) to (gr,gc)."""

        if maze [sr ][sc ]!=1 or maze [gr ][gc ]!=1 :

            return False 



        visited =set ()

        queue =deque ([(sr ,sc )])

        visited .add ((sr ,sc ))



        while queue :

            r ,c =queue .popleft ()

            if r ==gr and c ==gc :

                return True 

            for dr ,dc in [(-1 ,0 ),(1 ,0 ),(0 ,-1 ),(0 ,1 )]:

                nr ,nc =r +dr ,c +dc 

                if (0 <=nr <self .ROWS and 0 <=nc <self .COLS 

                and (nr ,nc )not in visited and maze [nr ][nc ]==1 ):

                    visited .add ((nr ,nc ))

                    queue .append ((nr ,nc ))



        return False 









    def _fallback_maze (self ):

        """Create a simple maze with a guaranteed open corridor."""

        maze =[[0 ]*self .COLS for _ in range (self .ROWS )]



        for c in range (1 ,self .COLS -1 ):

            maze [1 ][c ]=1 

        for r in range (1 ,self .ROWS -1 ):

            maze [r ][self .COLS -2 ]=1 

        return maze 







    def handle_event (self ,event ):

        if event .type ==pygame .KEYDOWN :

            new_r ,new_c =self .player_row ,self .player_col 



            if event .key in (pygame .K_UP ,pygame .K_w ):

                new_r -=1 

            elif event .key in (pygame .K_DOWN ,pygame .K_s ):

                new_r +=1 

            elif event .key in (pygame .K_LEFT ,pygame .K_a ):

                new_c -=1 

            elif event .key in (pygame .K_RIGHT ,pygame .K_d ):

                new_c +=1 





            if (0 <=new_r <self .ROWS and 0 <=new_c <self .COLS 

            and self .grid [new_r ][new_c ]==1 ):

                self .player_row =new_r 

                self .player_col =new_c 





            if self .player_row ==self .goal_row and self .player_col ==self .goal_col :

                self .won =True 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )





        offset_x =(1920 -self .COLS *self .CELL_SIZE )//2 

        offset_y =(1080 -self .ROWS *self .CELL_SIZE )//2 





        for row in range (self .ROWS ):

            for col in range (self .COLS ):

                x =offset_x +col *self .CELL_SIZE 

                y =offset_y +row *self .CELL_SIZE 



                if self .grid [row ][col ]==0 :



                    pygame .draw .rect (screen ,(139 ,69 ,19 ),

                    pygame .Rect (x ,y ,self .CELL_SIZE ,self .CELL_SIZE ))

                else :



                    pygame .draw .rect (screen ,(40 ,40 ,60 ),pygame .Rect (x ,y ,self .CELL_SIZE ,self .CELL_SIZE ))

                    pygame .draw .rect (screen ,(60 ,60 ,90 ),pygame .Rect (x ,y ,self .CELL_SIZE ,self .CELL_SIZE ),1 )





        goal_x =offset_x +self .goal_col *self .CELL_SIZE +4 

        goal_y =offset_y +self .goal_row *self .CELL_SIZE +4 

        pygame .draw .rect (screen ,GREEN ,pygame .Rect (goal_x ,goal_y ,self .CELL_SIZE -8 ,self .CELL_SIZE -8 ))





        start_x =offset_x +0 *self .CELL_SIZE +4 

        start_y =offset_y +0 *self .CELL_SIZE +4 

        pygame .draw .rect (screen ,BLUE ,pygame .Rect (start_x ,start_y ,self .CELL_SIZE -8 ,self .CELL_SIZE -8 ))





        player_x =offset_x +self .player_col *self .CELL_SIZE +4 

        player_y =offset_y +self .player_row *self .CELL_SIZE +4 

        pygame .draw .rect (screen ,CYAN ,pygame .Rect (player_x ,player_y ,self .CELL_SIZE -8 ,self .CELL_SIZE -8 ))





        title =FONT_MEDIUM .render ("BLUDIŠTĚ",True ,YELLOW )

        screen .blit (title ,(50 ,screen .get_height ()-150 ))



        instr =FONT_SMALL .render ("ŠIPKY/WSAD = Pohyb | Dorazit na ZELENÝ CÍL",True ,WHITE )

        screen .blit (instr ,(50 ,screen .get_height ()-100 ))



    def get_hint (self ):

        return "Hledej cestu na zelený čtverec vpravo dole!"

def get_level_class():
    return Maze

