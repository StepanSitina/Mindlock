from .shared import *

class TimeBomb (BaseGame ):

    """Časová Bomba – Explosive Puzzle.  3-6 kabelů s barvou + vzorem,

    displej ukazuje kód, manuál s pravidly.  Falešné kabely zrychlí čas."""





    CABLE_COLORS =[

    ("červená",(220 ,30 ,30 )),

    ("modrá",(30 ,100 ,220 )),

    ("žlutá",(230 ,220 ,30 )),

    ("zelená",(30 ,180 ,50 )),

    ("černá",(40 ,40 ,40 )),

    ("bílá",(230 ,230 ,230 )),

    ]



    PATTERNS =["pruhy","tečky","spirála","rovná"]



    DISPLAY_CODES =list ("ABCDEFGH")+list ("12345678")



    def __init__ (self ):

        super ().__init__ ()

        self .num_cables =random .randint (3 ,6 )

        self .cables =self ._generate_cables ()

        self .display_code =random .choice (self .DISPLAY_CODES )

        self .rules ,self .correct_index =self ._generate_rules ()

        self .timer_max =60 *FPS 

        self .timer =self .timer_max 

        self .speed_mult =1.0 

        self .cut_index =-1 

        self .message =""

        self .beep_interval =60 

        self .beep_counter =0 





    def _generate_cables (self ):

        cables =[]

        used =set ()

        for _ in range (self .num_cables ):

            while True :

                ci =random .randint (0 ,len (self .CABLE_COLORS )-1 )

                pi =random .randint (0 ,len (self .PATTERNS )-1 )

                key =(ci ,pi )

                if key not in used :

                    used .add (key )

                    break 

            name ,rgb =self .CABLE_COLORS [ci ]

            pattern =self .PATTERNS [pi ]

            fake =random .random ()<0.2 

            cables .append ({

            "color_name":name ,"color":rgb ,"pattern":pattern ,

            "cut":False ,"fake":fake ,

            })



        if all (c ["fake"]for c in cables ):

            cables [random .randint (0 ,len (cables )-1 )]["fake"]=False 

        return cables 



    def _generate_rules (self ):

        """Vytvoří 3-4 pravidla a z nich deterministicky určí správný kabel."""

        rules =[]

        correct =None 





        if self .display_code .isalpha ():

            letter =self .display_code 

            target_pattern =random .choice (self .PATTERNS )

            candidates =[i for i ,c in enumerate (self .cables )

            if c ["pattern"]==target_pattern and not c ["fake"]]

            if candidates :

                idx =candidates [0 ]

                rules .append (f"Pokud displej ukazuje písmeno {letter }, "

                f"přestřihni první kabel se vzorem '{target_pattern }'.")

                correct =idx 

        else :

            num =int (self .display_code )

            if num %2 ==0 :

                candidates =[i for i ,c in enumerate (self .cables )

                if c ["color_name"]=="modrá"and not c ["fake"]]

                if candidates :

                    rules .append ("Pokud je číslo na displeji sudé, "

                    "přestřihni první modrý kabel.")

                    correct =candidates [0 ]

                else :

                    rules .append ("Pokud je číslo na displeji sudé a nikde není modrý, "

                    "přestřihni poslední kabel.")

                    non_fake =[i for i ,c in enumerate (self .cables )if not c ["fake"]]

                    correct =non_fake [-1 ]if non_fake else len (self .cables )-1 

            else :

                candidates =[i for i ,c in enumerate (self .cables )

                if c ["color_name"]=="červená"and not c ["fake"]]

                if candidates :

                    rules .append ("Pokud je číslo na displeji liché, "

                    "přestřihni první červený kabel.")

                    correct =candidates [0 ]

                else :

                    rules .append ("Pokud je číslo liché a není červený, "

                    "přestřihni první kabel.")

                    non_fake =[i for i ,c in enumerate (self .cables )if not c ["fake"]]

                    correct =non_fake [0 ]if non_fake else 0 





        if correct is None :

            non_fake =[i for i ,c in enumerate (self .cables )if not c ["fake"]]

            correct =non_fake [0 ]if non_fake else 0 

            rules .append ("Pokud žádné pravidlo neplatí, přestřihni první kabel.")





        color_names =[c ["color_name"]for c in self .cables ]

        if "žlutá"in color_names :

            yi =color_names .index ("žlutá")

            left_blue =yi >0 and color_names [yi -1 ]=="modrá"

            right_blue =yi <len (color_names )-1 and color_names [yi +1 ]=="modrá"

            if left_blue and right_blue :

                rules .append ("Žlutý kabel mezi dvěma modrými – NIKDY ho nestříhej!")

            else :

                rules .append ("Pokud žlutý kabel NENÍ mezi dvěma modrými, můžeš ho ignorovat.")





        red_count =sum (1 for c in self .cables if c ["color_name"]=="červená")

        if red_count >2 :

            rules .append (f"Pozor: {red_count } červené kabely! Nech si je na konec.")

        elif red_count ==0 :

            rules .append ("Žádný červený kabel – buď opatrný s modrými.")





        rules .append ("Falešné kabely vypadají nevinně, ale zrychlí časovač!")



        return rules ,correct 





    def handle_event (self ,event ):

        if self .won or self .lost :

            return 

        if event .type ==pygame .MOUSEBUTTONDOWN :

            pos =event .pos 

            for i in range (self .num_cables ):

                if self .cables [i ]["cut"]:

                    continue 

                rect =self ._cable_rect (i )

                if rect .collidepoint (pos ):

                    self ._cut_cable (i )

                    return 



    def _cable_rect (self ,i ):

        cable_cx =SCREEN_WIDTH //3 

        total_w =self .num_cables *100 +(self .num_cables -1 )*30 

        start_x =cable_cx -total_w //2 

        x =start_x +i *130 

        return pygame .Rect (x ,340 ,100 ,220 )



    def _cut_cable (self ,i ):

        self .cables [i ]["cut"]=True 

        if self .cables [i ]["fake"]:

            self .speed_mult +=0.5 

            self .message ="Falešný kabel! Časovač se zrychlil!"

            return 

        if i ==self .correct_index :

            self .won =True 

            self .message ="BOMBA DEAKTIVOVÁNA!"

        else :

            self .speed_mult *=3.0 

            self .message ="Špatný kabel! Čas se zrychlil 3×!"





    def update (self ):

        if self .won or self .lost :

            return 

        self .timer -=self .speed_mult 

        if self .timer <=0 :

            self .timer =0 

            self .lost =True 

            self .message ="Čas vypršel! VÝBUCH!"



        frac =self .timer /self .timer_max 

        self .beep_interval =max (5 ,int (60 *frac ))

        self .beep_counter +=1 

        if self .beep_counter >=self .beep_interval :

            self .beep_counter =0 

            self ._beep ()



    def _beep (self ):

        try :

            freq =int (600 +(1 -self .timer /self .timer_max )*800 )

            dur =40 

            buf =bytearray (dur *44100 *2 //1000 )

            for s in range (len (buf )//2 ):

                t =s /44100 

                val =int (16000 *math .sin (2 *math .pi *freq *t ))

                buf [2 *s ]=val &0xFF 

                buf [2 *s +1 ]=(val >>8 )&0xFF 

            snd =pygame .mixer .Sound (buffer =bytes (buf ))

            base_vol =0.15 

            if hasattr (self ,"sfx"):

                base_vol *=self .sfx .master_volume 

            snd .set_volume (base_vol )

            snd .play ()

        except Exception :

            pass 





    def draw (self ,screen ):

        screen .fill (DARK_BLUE )





        cable_cx =SCREEN_WIDTH //3 





        frac =self .timer /self .timer_max 

        title_col =RED if frac <0.3 else YELLOW 

        title =FONT_LARGE .render ("CASOVA BOMBA",True ,title_col )

        screen .blit (title ,title .get_rect (centerx =cable_cx ,top =15 ))





        secs =max (0 ,self .timer /FPS )

        t_col =RED if secs <5 else YELLOW 

        timer_txt =FONT_LARGE .render (f"{secs :.1f}s",True ,t_col )

        screen .blit (timer_txt ,timer_txt .get_rect (centerx =cable_cx ,top =90 ))





        code_rect =pygame .Rect (cable_cx -60 ,160 ,120 ,60 )

        pygame .draw .rect (screen ,(10 ,10 ,10 ),code_rect )

        pygame .draw .rect (screen ,CYAN ,code_rect ,3 )

        code_txt =FONT_LARGE .render (self .display_code ,True ,(0 ,255 ,100 ))

        screen .blit (code_txt ,code_txt .get_rect (center =code_rect .center ))

        lbl =FONT_TINY .render ("KÓD",True ,GRAY )

        screen .blit (lbl ,lbl .get_rect (centerx =cable_cx ,top =225 ))





        for i in range (self .num_cables ):

            self ._draw_cable (screen ,i )





        if self .message :

            mc =GREEN if self .won else RED 

            mt =FONT_MEDIUM .render (self .message ,True ,mc )

            screen .blit (mt ,mt .get_rect (centerx =cable_cx ,top =590 ))





        if not self .won and not self .lost :

            it =FONT_SMALL .render ("Klikni na kabel k přestřihnutí!",True ,WHITE )

            screen .blit (it ,it .get_rect (centerx =cable_cx ,top =650 ))





        if self .speed_mult >1.0 :

            sp =FONT_TINY .render (f"Rychlost: x{self .speed_mult :.1f}",True ,RED )

            screen .blit (sp ,(10 ,10 ))





        manual_x =SCREEN_WIDTH //2 +40 

        manual_w =SCREEN_WIDTH //2 -80 

        panel =pygame .Rect (manual_x ,15 ,manual_w ,SCREEN_HEIGHT -30 )

        pygame .draw .rect (screen ,(20 ,15 ,35 ),panel ,border_radius =10 )

        pygame .draw .rect (screen ,(100 ,80 ,40 ),panel ,3 ,border_radius =10 )



        mt =FONT_MEDIUM .render ("MANUAL",True ,YELLOW )

        screen .blit (mt ,mt .get_rect (centerx =panel .centerx ,top =panel .top +12 ))





        cy =panel .top +60 

        cs =FONT_TINY .render ("Kabely:",True ,CYAN )

        screen .blit (cs ,(manual_x +15 ,cy ))

        cy +=24 

        for i ,c in enumerate (self .cables ):

            txt =f"  {i +1 }: {c ['color_name']} ({c ['pattern']})"

            ct =FONT_TINY .render (txt ,True ,WHITE )

            screen .blit (ct ,(manual_x +15 ,cy ))

            cy +=22 





        cy +=10 

        rl =FONT_TINY .render ("Pravidla:",True ,CYAN )

        screen .blit (rl ,(manual_x +15 ,cy ))

        cy +=26 

        for ri ,rule in enumerate (self .rules ):

            rule_col =(255 ,200 ,100 )if ri ==0 else LIGHT_GRAY 



            words =rule .split ()

            line ="• "

            for w in words :

                test =line +w +" "

                tw =FONT_TINY .size (test )[0 ]

                if tw >manual_w -30 :

                    rt =FONT_TINY .render (line ,True ,rule_col )

                    screen .blit (rt ,(manual_x +15 ,cy ))

                    cy +=22 

                    line ="  "+w +" "

                else :

                    line =test 

            if line .strip ():

                rt =FONT_TINY .render (line ,True ,rule_col )

                screen .blit (rt ,(manual_x +15 ,cy ))

                cy +=22 

            cy +=4 



    def _draw_cable (self ,screen ,i ):

        rect =self ._cable_rect (i )

        cable =self .cables [i ]

        col =cable ["color"]



        if cable ["cut"]:



            pygame .draw .rect (screen ,(50 ,50 ,50 ),rect )

            pygame .draw .rect (screen ,GRAY ,rect ,2 )

            pygame .draw .line (screen ,RED ,rect .topleft ,rect .bottomright ,4 )

            pygame .draw .line (screen ,RED ,rect .topright ,rect .bottomleft ,4 )

            return 





        pygame .draw .rect (screen ,col ,rect ,border_radius =6 )

        pygame .draw .rect (screen ,WHITE ,rect ,3 ,border_radius =6 )





        cx ,cy =rect .centerx ,rect .centery 

        pat =cable ["pattern"]

        if pat =="pruhy":

            for dy in range (-60 ,70 ,20 ):

                pygame .draw .line (screen ,BLACK ,(rect .left +8 ,cy +dy ),

                (rect .right -8 ,cy +dy ),2 )

        elif pat =="tečky":

            for dx in range (-30 ,40 ,20 ):

                for dy in range (-70 ,80 ,20 ):

                    pygame .draw .circle (screen ,BLACK ,(cx +dx ,cy +dy ),4 )

        elif pat =="spirála":

            pts =[]

            for a in range (0 ,720 ,15 ):

                r =5 +a /60 

                px =cx +r *math .cos (math .radians (a ))

                py =cy +r *math .sin (math .radians (a ))

                pts .append ((int (px ),int (py )))

            if len (pts )>1 :

                pygame .draw .lines (screen ,BLACK ,False ,pts ,2 )

        else :

            pygame .draw .line (screen ,BLACK ,(cx ,rect .top +10 ),

            (cx ,rect .bottom -10 ),4 )





        lbl1 =FONT_TINY .render (cable ["color_name"],True ,WHITE )

        lbl2 =FONT_TINY .render (cable ["pattern"],True ,LIGHT_GRAY )

        screen .blit (lbl1 ,lbl1 .get_rect (centerx =cx ,top =rect .bottom +4 ))

        screen .blit (lbl2 ,lbl2 .get_rect (centerx =cx ,top =rect .bottom +22 ))



    def get_hint (self ):

        c =self .cables [self .correct_index ]

        return (f"Správný kabel je #{self .correct_index +1 }: "

        f"{c ['color_name']}, vzor {c ['pattern']}.")

def get_level_class():
    return TimeBomb

