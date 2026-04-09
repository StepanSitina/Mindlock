from .shared import *

class CipherBreaker (BaseGame ):

    """Cipher Breaker – decrypt a Caesar-shifted word using given shift table."""



    SHIFT_TABLE ={

    "A":"D","B":"E","C":"F","D":"G","E":"H",

    "F":"I","G":"J","H":"K","I":"L","J":"M",

    "K":"N","L":"O","M":"P","N":"Q","O":"R",

    "P":"S","Q":"T","R":"U","S":"V","T":"W",

    "U":"X","V":"Y","W":"Z","X":"A","Y":"B",

    "Z":"C",

    }



    REVERSE ={}



    WORDS =[

    "PUZZLE","MIRROR","CIPHER","QUANTUM","SWITCH",

    "BRAIN","LOGIC","PORTAL","ENIGMA","NEBULA",

    ]



    def __init__ (self ):

        super ().__init__ ()



        for k ,v in self .SHIFT_TABLE .items ():

            self .REVERSE [v ]=k 



        self .plain =random .choice (self .WORDS )

        self .encrypted ="".join (self .SHIFT_TABLE .get (c ,c )for c in self .plain )

        self .answer =""

        self .wrong_attempts =0 

        self .max_attempts =4 

        self .feedback =""

        self .feedback_timer =0 

        self .show_table =True 



    def handle_event (self ,event ):

        if event .type !=pygame .KEYDOWN or self .won or self .lost :

            return 

        if event .key ==pygame .K_TAB :

            self .show_table =not self .show_table 

            return 

        if event .key ==pygame .K_BACKSPACE :

            self .answer =self .answer [:-1 ]

            return 

        if event .key ==pygame .K_RETURN :

            if self .answer .upper ()==self .plain :

                self .won =True 

            else :

                self .wrong_attempts +=1 

                self .feedback =f"SPATNE! ({self .max_attempts -self .wrong_attempts } zbyvaji)"

                self .feedback_timer =90 

                self .answer =""

                if self .wrong_attempts >=self .max_attempts :

                    self .lost =True 

            return 

        if event .unicode .isalpha ()and len (self .answer )<len (self .plain )+2 :

            self .answer +=event .unicode .upper ()



    def update (self ):

        if self .feedback_timer >0 :

            self .feedback_timer -=1 



    def draw (self ,screen ):

        screen .fill ((15 ,10 ,30 ))



        title =FONT_LARGE .render ("CIPHER BREAKER",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -title .get_width ()//2 ,20 ))



        inst =FONT_SMALL .render ("Desifruj slovo pomoci tabulky (posun +3). Napís a stiskni ENTER.",True ,WHITE )

        screen .blit (inst ,(SCREEN_WIDTH //2 -inst .get_width ()//2 ,85 ))





        enc_label =FONT_SMALL .render ("Zasifrovane:",True ,YELLOW )

        screen .blit (enc_label ,(SCREEN_WIDTH //2 -350 ,150 ))

        enc_text =FONT_LARGE .render (self .encrypted ,True ,(255 ,100 ,100 ))

        screen .blit (enc_text ,(SCREEN_WIDTH //2 -100 ,140 ))





        ans_label =FONT_SMALL .render ("Tvoje odpoved:",True ,YELLOW )

        screen .blit (ans_label ,(SCREEN_WIDTH //2 -350 ,230 ))

        ans_box =pygame .Rect (SCREEN_WIDTH //2 -100 ,225 ,400 ,55 )

        pygame .draw .rect (screen ,(30 ,30 ,60 ),ans_box )

        pygame .draw .rect (screen ,CYAN ,ans_box ,2 )

        ans_text =FONT_LARGE .render (self .answer +"_",True ,GREEN )

        screen .blit (ans_text ,(ans_box .x +10 ,ans_box .y +5 ))





        att =FONT_SMALL .render (

        f"Pokusy: {self .wrong_attempts }/{self .max_attempts }",True ,

        RED if self .wrong_attempts >=3 else WHITE )

        screen .blit (att ,(SCREEN_WIDTH //2 -att .get_width ()//2 ,300 ))





        if self .show_table :

            tbl_y =370 

            tbl_label =FONT_SMALL .render ("SIFROVACI TABULKA (posun +3):",True ,YELLOW )

            screen .blit (tbl_label ,(SCREEN_WIDTH //2 -tbl_label .get_width ()//2 ,tbl_y -30 ))

            letters ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            row1 ="  ".join (letters )

            row2 ="  ".join (self .SHIFT_TABLE [c ]for c in letters )

            r1 =FONT_TINY .render ("PLAIN:    "+row1 ,True ,(180 ,180 ,220 ))

            r2 =FONT_TINY .render ("CIPHER:  "+row2 ,True ,(255 ,140 ,140 ))

            screen .blit (r1 ,(SCREEN_WIDTH //2 -r1 .get_width ()//2 ,tbl_y ))

            screen .blit (r2 ,(SCREEN_WIDTH //2 -r2 .get_width ()//2 ,tbl_y +28 ))

            tip =FONT_TINY .render ("Kazde pismeno v CIPHER odpovida pismenu v PLAIN (napr. D->A, H->E)",True ,LIGHT_GRAY )

            screen .blit (tip ,(SCREEN_WIDTH //2 -tip .get_width ()//2 ,tbl_y +62 ))



        tab_hint =FONT_TINY .render ("TAB = zobrazit/skrýt tabulku",True ,(100 ,100 ,130 ))

        screen .blit (tab_hint ,(SCREEN_WIDTH //2 -tab_hint .get_width ()//2 ,SCREEN_HEIGHT -40 ))





        if self .feedback_timer >0 and self .feedback :

            ft =FONT_MEDIUM .render (self .feedback ,True ,RED )

            screen .blit (ft ,(SCREEN_WIDTH //2 -ft .get_width ()//2 ,SCREEN_HEIGHT //2 +100 ))





        if self .won :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render (f"SPRAVNE! Slovo: {self .plain }",True ,GREEN )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))

        if self .lost :

            ov =pygame .Surface ((SCREEN_WIDTH ,SCREEN_HEIGHT ),pygame .SRCALPHA )

            ov .fill ((0 ,0 ,0 ,150 ))

            screen .blit (ov ,(0 ,0 ))

            t =FONT_LARGE .render (f"KONEC! Slovo bylo: {self .plain }",True ,RED )

            screen .blit (t ,(SCREEN_WIDTH //2 -t .get_width ()//2 ,SCREEN_HEIGHT //2 -40 ))



    def get_hint (self ):

        return f"Posun je +3. Prvni pismeno desifrovane: {self .plain [0 ]}"

def get_level_class():
    return CipherBreaker

