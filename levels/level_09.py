from .shared import *

class Hangman (BaseGame ):

    """Guess word - Hangman with categories and riddle hints - NOW IN ENGLISH"""

    def __init__ (self ):

        super ().__init__ ()

        self .categories ={

        "ANIMALS":["DOG","CAT","BIRD","HORSE","ELEPHANT"],

        "FOOD":["PIZZA","BREAD","CHEESE","APPLE","CHICKEN"],

        "COUNTRIES":["FRANCE","GERMANY","JAPAN","BRAZIL","CANADA"],

        "SPORTS":["TENNIS","HOCKEY","SOCCER","BOXING","SWIMMING"]

        }

        self .riddles ={

        "DOG":"Domestikovaný před 15 000 lety z vlků, tento věrný společník se dokáže naučit stovky slov a dokáže vycítit nemoci.",

        "CAT":"Uctíváni jako bohové ve starověkém Egyptě, tito tichí lovci tráví 70 % svého života spánkem.",

        "BIRD":"Jediní žijící potomci dinosaurů, některé druhy dokážou létat pozpátku, jiné plavou, ale nikdy nelétají.",

        "HORSE":"Bucephalus Alexandra Velikého byl jeden z nich; spí ve stoje a mohou běžet už pár hodin po narození.",

        "ELEPHANT":"Největší suchozemský savec na Zemi, oplakává své mrtvé, bojí se včel a jeho kly jsou vlastně přerostlé zuby.",

        "PIZZA":"Pokrm, který se z Neapole rozšířil po celém světě, odrůda Margherita byla pojmenována po italské královně v roce 1889.",

        "BREAD":"Jeden z nejstarších připravených lidských pokrmů sahající 14 000 let zpět, starověcí Egypťané jej používali jako měnu.",

        "CHEESE":"Náhodně objeveno, když se mléko skladovalo v žaludcích zvířat; některé zrající druhy jsou legálně považovány za živé kvůli roztočům.",

        "APPLE":"Newton údajně objevil gravitaci díky jablku; jeho semena obsahují sloučeninu, která se mění na kyanid.",

        "CHICKEN":"Pochází z kohouta lesního jihovýchodní Asie, na Zemi jich je třikrát více než lidí.",

        "FRANCE":"Domov věže, kterou místní kdysi nenáviděli, Louvru, který byl pevností, a nejnavštěvovanější země světa.",

        "GERMANY":"Evropská země centrální pro obě světové války, známá inženýrstvím, dálnicemi bez omezení rychlosti a Oktoberfestem.",

        "JAPAN":"Ostrovní stát s největším počtem automatů na obyvatele, kde se vlaky omlouvají, i když mají zpoždění jen několik sekund.",

        "BRAZIL":"Pojmenována podle stromu, hostí největší karneval na světě a obsahuje 60 % amazonského deštného pralesa.",

        "CANADA":"Druhá největší země světa podle rozlohy, má více jezer než zbytek světa dohromady.",

        "TENNIS":"Sport, kde 'love' znamená nula, původně se hrál holýma rukama v francouzských klášterech.",

        "HOCKEY":"Sport hraný na zamrzlé vodě, kde vulkanizovaný gumový kotouč může letět rychlostí přes 170 km/h.",

        "SOCCER":"Nejoblíbenější sport na světě; jeho největší turnaj byl kdysi rozhodnut gólem zvaným 'Ruka Boží'.",

        "BOXING":"Známý jako 'sladká věda', staří Řekové si na Olympia omotávali pěsti koženými pásky, aby soutěžili.",

        "SWIMMING":"Benjamin Franklin vynalezl ploutve pro plavání; lidé jsou jediní primáti, kteří si ho přirozeně užívají."

        }

        self .category =random .choice (list (self .categories .keys ()))

        self .word =random .choice (self .categories [self .category ])

        self .riddle =self .riddles .get (self .word ,"")

        self .guessed =set ()

        self .wrong =0 

        self .max_wrong =6 

        self .hint_visible =False 

        self .hint_space_count =0 

        self .hint_space_timer =0 



    def handle_event (self ,event ):

        if event .type ==pygame .KEYDOWN :



            if event .key ==pygame .K_SPACE :

                self .hint_space_count +=1 

                self .hint_space_timer =25 

                if self .hint_space_count >=2 :

                    self .hint_visible =not self .hint_visible 

                    self .hint_space_count =0 

                return 

            if event .unicode .isalpha ():

                letter =event .unicode .upper ()

                if letter not in self .guessed :

                    self .guessed .add (letter )

                    if letter not in self .word :

                        self .wrong +=1 



                    if all (l in self .guessed for l in self .word ):

                        self .won =True 

                    if self .wrong >=self .max_wrong :

                        self .lost =True 



    def update (self ):

        if self .hint_space_timer >0 :

            self .hint_space_timer -=1 

        else :

            self .hint_space_count =0 



    def draw (self ,screen ):

        screen .fill (DARK_BLUE )

        title =FONT_LARGE .render ("HANGMAN",True ,CYAN )

        screen .blit (title ,(SCREEN_WIDTH //2 -150 ,30 ))



        cat_text =FONT_SMALL .render (f"Category: {self .category }",True ,CYAN )

        screen .blit (cat_text ,(SCREEN_WIDTH //2 -150 ,80 ))





        if self .riddle and self .hint_visible :

            max_w =80 

            words =self .riddle .split ()

            lines =[]

            cur =""

            for w in words :

                if len (cur )+len (w )+1 <=max_w :

                    cur =cur +" "+w if cur else w 

                else :

                    lines .append (cur )

                    cur =w 

            if cur :

                lines .append (cur )

            for li ,line in enumerate (lines ):

                rt =FONT_TINY .render (line ,True ,(200 ,200 ,255 ))

                screen .blit (rt ,(SCREEN_WIDTH //2 -rt .get_width ()//2 ,120 +li *22 ))

        elif not self .hint_visible :

            ht =FONT_TINY .render ("Napoveda: 2x SPACE",True ,(120 ,120 ,150 ))

            screen .blit (ht ,(SCREEN_WIDTH //2 -ht .get_width ()//2 ,120 ))



        word_display =" ".join (l if l in self .guessed else "_"for l in self .word )

        word_text =FONT_LARGE .render (word_display ,True ,YELLOW )

        screen .blit (word_text ,(SCREEN_WIDTH //2 -200 ,230 ))



        guessed_text =FONT_SMALL .render (f"Hádaná písmena: {' '.join (sorted (self .guessed ))}",True ,WHITE )

        screen .blit (guessed_text ,(SCREEN_WIDTH //2 -300 ,380 ))



        wrong_text =FONT_MEDIUM .render (f"Chyby: {self .wrong }/{self .max_wrong }",True ,RED )

        screen .blit (wrong_text ,(SCREEN_WIDTH //2 -150 ,500 ))





        if self .lost :

            lost_text =FONT_LARGE .render (f"PROHRAUL! Slovo: {self .word }",True ,RED )

            screen .blit (lost_text ,(SCREEN_WIDTH //2 -300 ,650 ))



    def get_hint (self ):

        return self .riddle if self .riddle else "No hint available."

def get_level_class():
    return Hangman

