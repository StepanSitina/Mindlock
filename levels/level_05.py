from .shared import *

class NumberSort (BaseGame ):

    """Seřaď rovnice podle výsledků od nejmenšího k největšímu"""



    def __init__ (self ):

        super ().__init__ ()

        self ._generate_equations ()



    @staticmethod 

    def _make_equation (answer ):

        """Return (equation_string, answer) for a given integer answer."""

        kind =random .randint (0 ,5 )

        if kind ==0 :

            c =random .randint (2 ,6 )

            return f"{c }x = {c *answer }",answer 

        elif kind ==1 :

            b =random .randint (3 ,30 )

            return f"x + {b } = {answer +b }",answer 

        elif kind ==2 :

            b =random .randint (2 ,min (answer -1 ,25 ))if answer >2 else 1 

            return f"x - {b } = {answer -b }",answer 

        elif kind ==3 :

            c =random .choice ([2 ,3 ,4 ,5 ])

            return f"x / {c } = {answer //c }"if answer %c ==0 else f"x + {c } = {answer +c }",answer 

        elif kind ==4 :

            b =random .randint (1 ,15 )

            return f"2x + {b } = {2 *answer +b }",answer 

        else :

            b =random .randint (1 ,12 )

            return f"3x - {b } = {3 *answer -b }",answer 



    def _generate_equations (self ):

        """Generate 4 equations with unique integer answers in [3..95]."""

        answers =random .sample (range (3 ,96 ),4 )

        self .equations =[self ._make_equation (a )for a in answers ]

        random .shuffle (self .equations )

        self .answers =[ans for _ ,ans in self .equations ]

        self .sorted_correct =sorted (self .answers )

        self .player_order =[]

        self .clicked_indices =set ()



    def handle_event (self ,event ):

        if event .type ==pygame .MOUSEBUTTONDOWN :

            sw =pygame .display .get_surface ().get_width ()

            sh =pygame .display .get_surface ().get_height ()

            s =min (sw /1920 ,sh /1080 )

            pos =event .pos 

            cols =4 

            btn_w =int (280 *s )

            btn_h =int (90 *s )

            gap_x =int (300 *s )

            gap_y =int (120 *s )

            total_w =cols *gap_x -(gap_x -btn_w )

            start_x =(sw -total_w )//2 

            start_y =int (280 *s )

            for i in range (len (self .equations )):

                col =i %cols 

                row =i //cols 

                x =start_x +col *gap_x 

                y =start_y +row *gap_y 

                if pygame .Rect (x ,y ,btn_w ,btn_h ).collidepoint (pos ):

                    if i not in self .clicked_indices :

                        ans =self .answers [i ]

                        self .player_order .append (ans )

                        self .clicked_indices .add (i )

                        if len (self .player_order )==len (self .answers ):

                            if self .player_order ==self .sorted_correct :

                                self .won =True 

                            else :

                                self .lost =True 

                    break 



    def draw (self ,screen ):

        sw ,sh =screen .get_size ()

        s =min (sw /1920 ,sh /1080 )

        screen .fill (DARK_BLUE )



        f_title =pygame .font .Font (None ,max (20 ,int (72 *s )))

        f_eq =pygame .font .Font (None ,max (14 ,int (36 *s )))

        f_info =pygame .font .Font (None ,max (12 ,int (30 *s )))



        title =f_title .render ("SEŘAĎ ROVNICE",True ,CYAN )

        screen .blit (title ,title .get_rect (center =(sw //2 ,int (50 *s ))))



        sub =f_info .render ("Vyřeš rovnice a klikej od nejmenšího výsledku k největšímu",True ,(200 ,200 ,255 ))

        screen .blit (sub ,sub .get_rect (center =(sw //2 ,int (110 *s ))))



        cols =4 

        btn_w =int (280 *s )

        btn_h =int (90 *s )

        gap_x =int (300 *s )

        gap_y =int (120 *s )

        total_w =cols *gap_x -(gap_x -btn_w )

        start_x =(sw -total_w )//2 

        start_y =int (280 *s )



        for i ,(eq_str ,ans )in enumerate (self .equations ):

            col =i %cols 

            row =i //cols 

            x =start_x +col *gap_x 

            y =start_y +row *gap_y 

            rect =pygame .Rect (x ,y ,btn_w ,btn_h )

            if i in self .clicked_indices :

                pygame .draw .rect (screen ,(40 ,40 ,60 ),rect )

                pygame .draw .rect (screen ,GRAY ,rect ,2 )

                t =f_eq .render (f"{eq_str }  [{ans }]",True ,GRAY )

            else :

                pygame .draw .rect (screen ,BLUE ,rect )

                pygame .draw .rect (screen ,WHITE ,rect ,3 )

                t =f_eq .render (eq_str ,True ,WHITE )

            screen .blit (t ,t .get_rect (center =rect .center ))





        if self .player_order :

            result =" < ".join (str (n )for n in self .player_order )

        else :

            result ="?"

        rt =f_info .render (f"Tvůj výběr: {result }",True ,YELLOW )

        screen .blit (rt ,rt .get_rect (center =(sw //2 ,sh -int (80 *s ))))



    def get_hint (self ):

        return f"Správné pořadí výsledků: {' < '.join (str (n )for n in self .sorted_correct )}"

def get_level_class():
    return NumberSort

