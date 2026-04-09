from .shared import *

class RotatingImage (BaseGame ):

    """Level 12: rozpoznání tvaru podle názvu bez rotace."""



    TOTAL_ROUNDS =3 

    OPTIONS_PER_ROUND =8 



    GRID_COLS =4 

    GRID_ROWS =2 

    CELL_W =240 

    CELL_H =210 



    C_BG =(12 ,15 ,35 )

    C_CELL_BG =(36 ,40 ,65 )

    C_CELL_HL =(58 ,64 ,96 )

    C_CORRECT_BG =(28 ,120 ,45 )

    C_WRONG_BG =(145 ,35 ,35 )



    SHAPE_NAMES ={

    "trojuhelnik":"Trojuhelnik",

    "ctverec":"Ctverec",

    "obdelnik":"Obdelnik",

    "petiuhelnik":"Petiuhelnik",

    "sestiuhelnik":"Sestiuhelnik",

    "sedmiuhelnik":"Sedmiuhelnik",

    "osmiuhelnik":"Osmiuhelnik",

    "hvezda":"Hvezda",

    "kruh":"Kruh",

    }



    SHAPE_COLORS ={

    "trojuhelnik":(255 ,170 ,80 ),

    "ctverec":(90 ,190 ,255 ),

    "obdelnik":(120 ,235 ,160 ),

    "petiuhelnik":(240 ,130 ,220 ),

    "sestiuhelnik":(255 ,215 ,90 ),

    "sedmiuhelnik":(170 ,140 ,255 ),

    "osmiuhelnik":(255 ,120 ,120 ),

    "hvezda":(255 ,245 ,110 ),

    "kruh":(110 ,255 ,255 ),

    }



    def __init__ (self ):

        super ().__init__ ()

        self .current_round =0 

        self .correct_count =0 

        self .feedback_timer =0 

        self .last_correct =None 

        self .hover_idx =-1 



        self .shape_pool =list (self .SHAPE_NAMES .keys ())

        random .shuffle (self .shape_pool )

        self .round_targets =self .shape_pool [:self .TOTAL_ROUNDS ]



        self .current_options =[]

        self .correct_option_idx =-1 

        self .selected_idx =-1 

        self ._prepare_round ()



    @staticmethod 

    def _regular_polygon (cx ,cy ,r ,n ):

        pts =[]

        for i in range (n ):

            a =math .radians (360 *i /n -90 )

            pts .append ((cx +r *math .cos (a ),cy +r *math .sin (a )))

        return pts 



    def _star (self ,cx ,cy ,r_out ,r_in ,n =5 ):

        pts =[]

        for i in range (n *2 ):

            r =r_out if i %2 ==0 else r_in 

            a =math .radians (360 *i /(n *2 )-90 )

            pts .append ((cx +r *math .cos (a ),cy +r *math .sin (a )))

        return pts 



    def _draw_poly (self ,surf ,pts ,fill ,outline =(0 ,0 ,0 ),ow =3 ):

        if len (pts )<3 :

            return 

        pygame .draw .polygon (surf ,fill ,pts )

        pygame .draw .polygon (surf ,outline ,pts ,ow )



    def _draw_shape (self ,screen ,shape_name ,cx ,cy ,scale =1.0 ):

        col =self .SHAPE_COLORS .get (shape_name ,CYAN )

        scale =max (0.7 ,scale )



        r_circle =int (45 *scale )

        rect_w =int (112 *scale )

        rect_h =int (68 *scale )

        r_star_out =int (48 *scale )

        r_star_in =int (22 *scale )

        r_poly =int (48 *scale )

        r_tri =int (52 *scale )

        r_sq =int (46 *scale )



        if shape_name =="kruh":

            pygame .draw .circle (screen ,col ,(cx ,cy ),r_circle )

            pygame .draw .circle (screen ,BLACK ,(cx ,cy ),r_circle ,3 )

        elif shape_name =="obdelnik":

            rect =pygame .Rect (cx -rect_w //2 ,cy -rect_h //2 ,rect_w ,rect_h )

            pygame .draw .rect (screen ,col ,rect )

            pygame .draw .rect (screen ,BLACK ,rect ,3 )

        elif shape_name =="hvezda":

            self ._draw_poly (screen ,self ._star (cx ,cy ,r_star_out ,r_star_in ),col )

        elif shape_name =="trojuhelnik":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_tri ,3 ),col )

        elif shape_name =="ctverec":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_sq ,4 ),col )

        elif shape_name =="petiuhelnik":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_poly ,5 ),col )

        elif shape_name =="sestiuhelnik":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_poly ,6 ),col )

        elif shape_name =="sedmiuhelnik":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_poly ,7 ),col )

        elif shape_name =="osmiuhelnik":

            self ._draw_poly (screen ,self ._regular_polygon (cx ,cy ,r_poly ,8 ),col )



    def _prepare_round (self ):

        target =self .round_targets [self .current_round ]

        distractors =[s for s in self .shape_pool if s !=target ]

        distractors =random .sample (distractors ,self .OPTIONS_PER_ROUND -1 )

        self .current_options =[target ]+distractors 

        random .shuffle (self .current_options )

        self .correct_option_idx =self .current_options .index (target )

        self .feedback_timer =0 

        self .last_correct =None 

        self .selected_idx =-1 



    def _cell_at (self ,pos ):

        mx ,my =pos 

        ox =(SCREEN_WIDTH -self .GRID_COLS *self .CELL_W )//2 

        oy =320 

        col =(mx -ox )//self .CELL_W 

        row =(my -oy )//self .CELL_H 

        if 0 <=col <self .GRID_COLS and 0 <=row <self .GRID_ROWS :

            idx =row *self .GRID_COLS +col 

            if idx <self .OPTIONS_PER_ROUND :

                return idx 

        return -1 



    def handle_event (self ,event ):

        if self .won or self .lost :

            return 

        if self .feedback_timer >0 :

            return 



        if event .type ==pygame .MOUSEMOTION :

            self .hover_idx =self ._cell_at (event .pos )



        if event .type ==pygame .MOUSEBUTTONDOWN and event .button ==1 :

            idx =self ._cell_at (event .pos )

            if idx <0 :

                return 



            self .selected_idx =idx 

            if idx ==self .correct_option_idx :

                self .correct_count +=1 

                self .last_correct =True 

                if hasattr (self ,"sfx"):

                    self .sfx .play ("level_success")

            else :

                self .last_correct =False 

                if hasattr (self ,"sfx"):

                    self .sfx .play ("level_fail")

            self .feedback_timer =45 



    def update (self ):

        if self .won or self .lost :

            return 



        if self .feedback_timer >0 :

            self .feedback_timer -=1 

            if self .feedback_timer ==0 :

                self ._advance_round ()



    def _advance_round (self ):

        self .current_round +=1 

        if self .current_round >=self .TOTAL_ROUNDS :

            if self .correct_count >=2 :

                self .won =True 

            else :

                self .lost =True 

        else :

            self ._prepare_round ()



    def draw (self ,screen ):

        screen .fill (self .C_BG )



        if self .won or self .lost :

            self ._draw_end_screen (screen )

            return 



        target_name =self .round_targets [self .current_round ]

        label =self .SHAPE_NAMES [target_name ]



        title =FONT_MEDIUM .render ("ROZPOZNEJ TVAR",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -title .get_width ()//2 ,18 ))



        ask =FONT_SMALL .render (f"Najdi: {label }",True ,YELLOW )

        screen .blit (ask ,(SCREEN_WIDTH //2 -ask .get_width ()//2 ,78 ))



        info =FONT_SMALL .render (

        f"Kolo: {self .current_round +1 }/{self .TOTAL_ROUNDS }   Spravne: {self .correct_count }",

        True ,

        WHITE ,

        )

        screen .blit (info ,(SCREEN_WIDTH //2 -info .get_width ()//2 ,120 ))



        ox =(SCREEN_WIDTH -self .GRID_COLS *self .CELL_W )//2 

        oy =320 



        for i in range (self .OPTIONS_PER_ROUND ):

            col =i %self .GRID_COLS 

            row =i //self .GRID_COLS 

            rx =ox +col *self .CELL_W 

            ry =oy +row *self .CELL_H 

            rect =pygame .Rect (rx ,ry ,self .CELL_W -10 ,self .CELL_H -10 )



            bg =self .C_CELL_HL if i ==self .hover_idx else self .C_CELL_BG 

            if self .feedback_timer >0 :

                if i ==self .correct_option_idx :

                    bg =self .C_CORRECT_BG 

                elif i ==self .selected_idx and not self .last_correct :

                    bg =self .C_WRONG_BG 



            pygame .draw .rect (screen ,bg ,rect ,border_radius =8 )

            pygame .draw .rect (screen ,(90 ,96 ,130 ),rect ,2 ,border_radius =8 )



            ccx =rect .centerx 

            ccy =rect .centery +4 

            pop_scale =1.0 

            if self .feedback_timer >0 and i ==self .correct_option_idx :

                phase =self .feedback_timer /45.0 

                pop_scale =1.10 +0.10 *phase 

            self ._draw_shape (screen ,self .current_options [i ],ccx ,ccy ,pop_scale )



            num =FONT_TINY .render (str (i +1 ),True ,GRAY )

            screen .blit (num ,(rect .x +8 ,rect .y +6 ))



        ins =FONT_TINY .render ("Vyber tvar podle nazvu nahore.",True ,LIGHT_GRAY )

        screen .blit (ins ,(SCREEN_WIDTH //2 -ins .get_width ()//2 ,SCREEN_HEIGHT -30 ))



    def _draw_end_screen (self ,screen ):

        if self .won :

            t =FONT_LARGE .render ("LEVEL COMPLETE!",True ,GREEN )

            msg =FONT_SMALL .render ("Skvela prace, tvary mas pod kontrolou.",True ,YELLOW )

        else :

            t =FONT_LARGE .render ("GAME OVER",True ,RED )

            msg =FONT_SMALL .render ("Potrebujes alespon 2 spravne odpovedi ze 3.",True ,LIGHT_GRAY )



        screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -90 ))

        sc =FONT_MEDIUM .render (f"Spravne: {self .correct_count } / {self .TOTAL_ROUNDS }",True ,WHITE )

        screen .blit (sc ,(SCREEN_WIDTH //2 -sc .get_width ()//2 ,SCREEN_HEIGHT //2 +5 ))

        screen .blit (msg ,(SCREEN_WIDTH //2 -msg .get_width ()//2 ,SCREEN_HEIGHT //2 +70 ))



    def get_hint (self ):

        return "Sleduj nazev nahore a vyber odpovidajici tvar. Tvary nejsou otocene."

def get_level_class():
    return RotatingImage

