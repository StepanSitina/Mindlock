from .shared import *

class CableConnect (BaseGame ):

    """Spoj barevné kabely – HARD: 6 párů, 2 návnady, zámky, 3 pokusy."""





    ALL_COLORS =[

    (255 ,0 ,0 ),

    (0 ,200 ,0 ),

    (0 ,100 ,255 ),

    (255 ,255 ,0 ),

    (0 ,255 ,255 ),

    (255 ,0 ,255 ),

    (255 ,140 ,0 ),

    (160 ,0 ,255 ),

    ]

    ALL_NAMES =["CERV","ZEL","MODR","ZLUT","CYAN","MAG","ORAN","FIAL"]



    NUM_PAIRS =6 

    NUM_RIGHT =8 



    def __init__ (self ):

        super ().__init__ ()





        self .left_cables =list (range (self .NUM_PAIRS ))





        self .right_cables =list (range (self .NUM_RIGHT ))

        random .shuffle (self .right_cables )



        self .connections ={}

        self .used_right =set ()

        self .selected =None 





        self .max_wrong =3 

        self .wrong_count =0 







        self .lock_prereqs ={4 :0 ,5 :2 }





        self .flash_timer =0 

        self .flash_color =(255 ,255 ,255 )

        self .flash_msg =""





    def _is_locked (self ,right_color_id ):

        if right_color_id not in self .lock_prereqs :

            return False 

        prereq =self .lock_prereqs [right_color_id ]

        for li in self .connections :

            if self .left_cables [li ]==prereq :

                return False 

        return True 



    def _flash (self ,msg ,color ,duration =60 ):

        self .flash_msg =msg 

        self .flash_color =color 

        self .flash_timer =duration 



    def _strike (self ,msg ):

        self .wrong_count +=1 

        self ._flash (msg ,(255 ,50 ,50 ),70 )

        if self .wrong_count >=self .max_wrong :

            self .lost =True 





    def _try_connect (self ,left_i ,right_i ):

        if left_i in self .connections or right_i in self .used_right :

            self ._flash ("UZ SPOJENO!",(255 ,160 ,0 ))

            return 



        rc =self .right_cables [right_i ]



        if self ._is_locked (rc ):

            self ._strike ("ZAMCENO! Spoj nejdriv prerequisitu.")

            return 



        lc =self .left_cables [left_i ]

        if lc !=rc :

            self ._strike ("SPATNA BARVA!")

            return 





        self .connections [left_i ]=right_i 

        self .used_right .add (right_i )

        self ._flash ("SPOJENO!",(0 ,255 ,80 ),40 )



        if len (self .connections )==self .NUM_PAIRS :

            self .won =True 





    def handle_event (self ,event ):

        if event .type !=pygame .MOUSEBUTTONDOWN :

            return 

        if self .won or self .lost :

            return 



        pos =event .pos 





        for i in range (self .NUM_PAIRS ):

            x ,y =350 ,190 +i *100 

            if pygame .Rect (x -35 ,y -35 ,70 ,70 ).collidepoint (pos ):

                if i in self .connections :

                    break 

                if self .selected and self .selected [0 ]=="right":

                    self ._try_connect (i ,self .selected [1 ])

                    self .selected =None 

                else :

                    self .selected =("left",i )

                return 





        for i in range (self .NUM_RIGHT ):

            x ,y =SCREEN_WIDTH -350 ,155 +i *88 

            if pygame .Rect (x -35 ,y -35 ,70 ,70 ).collidepoint (pos ):

                if i in self .used_right :

                    break 

                if self .selected and self .selected [0 ]=="left":

                    self ._try_connect (self .selected [1 ],i )

                    self .selected =None 

                else :

                    self .selected =("right",i )

                return 



    def update (self ):

        if self .flash_timer >0 :

            self .flash_timer -=1 





    def _node_pos_left (self ,i ):

        return 350 ,190 +i *100 



    def _node_pos_right (self ,i ):

        return SCREEN_WIDTH -350 ,155 +i *88 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )



        title =FONT_LARGE .render ("KABELY",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -title .get_width ()//2 ,15 ))





        strikes ="X "*self .wrong_count +"O "*(self .max_wrong -self .wrong_count )

        sc =RED if self .wrong_count >=2 else WHITE 

        st =FONT_SMALL .render (f"Pokusy: {strikes .strip ()}",True ,sc )

        screen .blit (st ,(SCREEN_WIDTH //2 -st .get_width ()//2 ,70 ))





        for i in range (self .NUM_PAIRS ):

            x ,y =self ._node_pos_left (i )

            ci =self .left_cables [i ]

            color =self .ALL_COLORS [ci ]

            done =i in self .connections 

            sel =self .selected ==("left",i )



            if done :

                dim =(color [0 ]//3 ,color [1 ]//3 ,color [2 ]//3 )

                pygame .draw .circle (screen ,dim ,(x ,y ),28 )

                pygame .draw .circle (screen ,(100 ,100 ,100 ),(x ,y ),28 ,2 )

            else :

                pygame .draw .circle (screen ,color ,(x ,y ),28 )

                bc =YELLOW if sel else WHITE 

                pygame .draw .circle (screen ,bc ,(x ,y ),28 ,5 if sel else 3 )



            lbl =FONT_TINY .render (self .ALL_NAMES [ci ],True ,BLACK if not done else GRAY )

            screen .blit (lbl ,lbl .get_rect (center =(x ,y )))





        for i in range (self .NUM_RIGHT ):

            x ,y =self ._node_pos_right (i )

            ci =self .right_cables [i ]

            color =self .ALL_COLORS [ci ]

            done =i in self .used_right 

            sel =self .selected ==("right",i )

            locked =self ._is_locked (ci )



            if done :

                dim =(color [0 ]//3 ,color [1 ]//3 ,color [2 ]//3 )

                pygame .draw .circle (screen ,dim ,(x ,y ),28 )

                pygame .draw .circle (screen ,(100 ,100 ,100 ),(x ,y ),28 ,2 )

            elif locked :

                pygame .draw .circle (screen ,(50 ,50 ,60 ),(x ,y ),28 )

                pygame .draw .circle (screen ,(90 ,90 ,100 ),(x ,y ),28 ,3 )

                lt =FONT_TINY .render ("LOCK",True ,(140 ,140 ,160 ))

                screen .blit (lt ,lt .get_rect (center =(x ,y )))

            else :

                pygame .draw .circle (screen ,color ,(x ,y ),28 )

                bc =YELLOW if sel else WHITE 

                pygame .draw .circle (screen ,bc ,(x ,y ),28 ,5 if sel else 3 )

                lbl =FONT_TINY .render (self .ALL_NAMES [ci ],True ,BLACK )

                screen .blit (lbl ,lbl .get_rect (center =(x ,y )))





        for li ,ri in self .connections .items ():

            x1 ,y1 =self ._node_pos_left (li )

            x2 ,y2 =self ._node_pos_right (ri )

            lc =self .ALL_COLORS [self .left_cables [li ]]

            pygame .draw .line (screen ,lc ,(x1 ,y1 ),(x2 ,y2 ),5 )





        if self .flash_timer >0 and self .flash_msg :

            ft =FONT_MEDIUM .render (self .flash_msg ,True ,self .flash_color )

            screen .blit (ft ,(SCREEN_WIDTH //2 -ft .get_width ()//2 ,

            SCREEN_HEIGHT //2 +220 ))





        rules =[

        "PRAVIDLA:",

        "1. Spoj stejne barvy",

        "2. ORAN + FIAL = navnady!",

        "3. CYAN: odemkni CERV",

        "4. MAG: odemkni MODR",

        f"5. Max {self .max_wrong } chyby",

        ]

        ry_start =190 

        for ri ,rule in enumerate (rules ):

            rc =YELLOW if ri ==0 else (180 ,180 ,200 )

            rt =FONT_TINY .render (rule ,True ,rc )

            screen .blit (rt ,(SCREEN_WIDTH -230 ,ry_start +ri *24 ))





        ct =FONT_SMALL .render (

        f"Pripojeno: {len (self .connections )}/{self .NUM_PAIRS }",True ,YELLOW )

        screen .blit (ct ,(SCREEN_WIDTH //2 -ct .get_width ()//2 ,SCREEN_HEIGHT -80 ))



        instr =FONT_TINY .render (

        "KLIKNI VLEVO -> PAK VPRAVO  |  "

        "Pozor na navnady a zamky!",True ,LIGHT_GRAY )

        screen .blit (instr ,(SCREEN_WIDTH //2 -instr .get_width ()//2 ,

        SCREEN_HEIGHT -40 ))





        if self .won :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render ("KABELY SPOJENY!",True ,GREEN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,

            SCREEN_HEIGHT //2 -40 ))



        if self .lost :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render ("PRILIS MNOHO CHYB!",True ,RED )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,

            SCREEN_HEIGHT //2 -40 ))



    def get_hint (self ):

        return "ORAN a FIAL jsou navnady! Spoj CERV pred CYAN, MODR pred MAG."

def get_level_class():
    return CableConnect

