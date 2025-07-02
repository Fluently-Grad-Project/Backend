from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import DailyWord, FCMToken, WordOfTheDay
from app.Notification.fcm import WordOfTheDayPayload, send_word_notification


def insert_word_of_the_day_data(db: Session):
    words_data = [
        {
            "word": "facade",
            "parts_of_speech": "Noun",
            "description": "the front of a building",
            "example": "the facade of this bank is made of limestone",
        },
        {
            "word": "mitigate",
            "parts_of_speech": "Verb",
            "description": "to make something less harmful, unpleasant, or bad",
            "example": "Getting a lot of sleep and drinking plenty of fluids can mitigate the effects of the flu",
        },
        {
            "word": "Thrilling",
            "parts_of_speech": "Adjective",
            "description": "Very exciting or suspenseful; giving a rush of adrenaline.",
            "example": "Each scene was more thrilling than the last-I was on the edge of my seat.",
        },
        {
            "word": "sedentary",
            "parts_of_speech": "Adjective",
            "description": "involving little exercise or physical activity",
            "example": "My doctor says I should start playing sport because my lifestyle is too sedentary",
        },
        {
            "word": "incentive",
            "parts_of_speech": "Noun",
            "description": "something that encourages a person or organization to do something",
            "example": "Bonus payments provide an incentive to work harder",
        },
        {
            "word": "nauseous",
            "parts_of_speech": "Adjective",
            "description": "Causing a feeling of disgust or sickness.",
            "example": "The smell of rotten eggs was so nauseous that I had to leave the room",
        },
        {
            "word": "unspoiled",
            "parts_of_speech": "Adjective",
            "description": "(place)beautiful because it has not been changed or damaged by people.",
            "example": "With its unspoiled natural beauty, Vietnam is becoming a destination for more and more foreign visitors.",
        },
        {
            "word": "implacable",
            "parts_of_speech": "Adjective",
            "description": "(opinion or feeling) unable to be changed, satisfied, or stopped.",
            "example": "The dictator was implacable, refusing all attempts at negotiation",
        },
        {
            "word": "luscious",
            "parts_of_speech": "Adjective",
            "description": "describe something that has a delicious taste or smell; juicy.",
            "example": "Because the bread smelled luscious, Tom decided to go into the bakery.",
        },
        {
            "word": "Freak out",
            "parts_of_speech": "Phrasal verb (also used as a noun: 'a freak-out')",
            "description": "Get very scared or angry.",
            "example": "She freaked out when she saw the spider on her pillow.",
        },
        {
            "word": "Cameo",
            "parts_of_speech": "Noun",
            "description": "a brief appearance by a famous person in a film.",
            "example": "The director made a surprise cameo in the last scene.",
        },
        {
            "word": "Dope",
            "parts_of_speech": "Adjective",
            "description": "Awesome, excellent, or cool.",
            "example": "Your sneakers are so dope!.",
        },
        {
            "word": "Salty",
            "parts_of_speech": "Adjective",
            "description": "Being irritated, bitter, or overly upset (often about something unreasonable).",
            "example": "Why are you so salty? It's just a game!.",
        },
        {
            "word": "Hangry",
            "parts_of_speech": "Adjective",
            "description": "When you are so hungry that you are angry!.",
            "example": "Don't talk to me before breakfast—I get hangry!.",
        },
        {
            "word": "Lit",
            "parts_of_speech": "Adjective",
            "description": "Amazing, Exciting, or Fun",
            "example": "The concert was so lit! Everybody was dancing and having a great time.",
        },
        {
            "word": "Sus",
            "parts_of_speech": "Adjective",
            "description": "Suspicious",
            "example": "His behavior was kind of sus; he kept looking around like he was hiding something.",
        },
        {
            "word": "Bummer",
            "parts_of_speech": "Noun",
            "description": "A disappointment",
            "example": "That's such a bummer. I'm sorry that happened.",
        },
        {
            "word": "Screw up",
            "parts_of_speech": "Verb",
            "description": "To make a mistake",
            "example": "Sorry I screwed up and forgot our plans.",
        },
        {
            "word": "carillon",
            "parts_of_speech": "noun",
            "description": "a set of stationary bells hung in a tower",
            "example": "At noon on Tuesday, some church bells and carillons in the Netherlands didn't sound like they usually do.",
        },
        {
            "word": "Ace",
            "parts_of_speech": "Verb",
            "description": "To Perform Exceptionally Well",
            "example": "He aced the exam!.",
        },
        {
            "word": "eloquent",
            "parts_of_speech": "Adjective",
            "description": "An eloquent speaker or writer expresses ideas forcefully and fluently",
            "example": "She received high marks for her eloquent essay about gardening with her grandmother.",
        },
        {
            "word": "Resilient",
            "parts_of_speech": "Adjective",
            "description": "Able to recover quickly from difficulties",
            "example": "After losing her job, she showed how resilient she was by starting her own business.",
        },
        {
            "word": "Ambiguous",
            "parts_of_speech": "Adjective",
            "description": "Extremely large in size, quantity, or degree; gigantic.",
            "example": "An enormous elephant stood near the waterhole.",
        },
        {
            "word": "Sophisticated",
            "parts_of_speech": "Adjective",
            "description": "Having refined knowledge, culture, or taste; elegant.",
            "example": "His sophisticated manners impressed everyone at the dinner party.",
        },
        {
            "word": "Superb",
            "parts_of_speech": "Adjective",
            "description": "Of the highest quality; exceptionally good, excellent, or magnificent.",
            "example": "The chef prepared a superb five-course meal.",
        },
        {
            "word": "Awful",
            "parts_of_speech": "Adjective",
            "description": "Extremely bad/unpleasant.",
            "example": "The food was awful – I couldn't eat it.",
        },
        {
            "word": "Gratitude",
            "parts_of_speech": "Noun",
            "description": "A feeling of deep appreciation, thankfulness, or recognition for kindness, benefits, or favors received.",
            "example": "She expressed her gratitude with a heartfelt thank-you note.",
        },
        {
            "word": "Bed Rotting",
            "parts_of_speech": "Noun",
            "description": "when someone spends excessive time in bed doing passive activities (self-caring.), sometimes to the point of neglecting responsibilities.",
            "example": "I'm bed rotting all weekend—no plans, just snacks and Netflix.",
        },
        {
            "word": "Euphoria",
            "parts_of_speech": "Noun",
            "description": "A state of intense happiness, excitement, or confidence, often overwhelming or temporary.",
            "example": "That first sip of coffee gave me a little euphoria.",
        },
        {
            "word": "Compact",
            "parts_of_speech": "Adjective",
            "description": "Tiny, Closely packed or condensed; designed to save space.",
            "example": "She bought a compact car for city driving.",
        },
        {
            "word": "Gloomy",
            "parts_of_speech": "Adjective",
            "description": "Causing or reflecting sadness, hopelessness.",
            "example": "His gloomy mood ruined the party vibe.",
        },
        {
            "word": "Fascinating",
            "parts_of_speech": "Adjective",
            "description": "Extremely interesting or captivating; holding attention irresistibly.",
            "example": "She has a fascinating ability to remember every detail.",
        },
        
    {
        "word": "Vibes",
        "parts_of_speech": "Noun",
        "description": "The emotional atmosphere or energy of a place or situation",
        "example": "This café has such good vibes—I could stay here all day.",
    },
    {
        "word": "Serene",
        "parts_of_speech": "Adjective",
        "description": "Calm, peaceful, and untroubled",
        "example": "The lake looked serene in the early morning light.",
    },
    {
        "word": "Flex",
        "parts_of_speech": "Verb",
        "description": "To show off something impressive",
        "example": "She flexed her new coding skills at the hackathon.",
    },
    {
        "word": "Meticulous",
        "parts_of_speech": "Adjective",
        "description": "Showing great attention to detail",
        "example": "His meticulous planning ensured the event went smoothly.",
    },
    {
        "word": "Ghost",
        "parts_of_speech": "Verb",
        "description": "To suddenly stop all communication with someone",
        "example": "After two dates, he totally ghosted me.",
    },
    {
        "word": "Pristine",
        "parts_of_speech": "Adjective",
        "description": "In perfect condition; spotlessly clean",
        "example": "The antique vase was in pristine condition.",
    },
    {
        "word": "Extra",
        "parts_of_speech": "Adjective",
        "description": "Over-the-top, excessive",
        "example": "Her birthday decorations were so extra—balloons covered every inch!",
    },
    {
        "word": "Diligent",
        "parts_of_speech": "Adjective",
        "description": "Showing care and effort in one's work",
        "example": "The diligent student always completed assignments early.",
    },
    {
        "word": "Yeet",
        "parts_of_speech": "Verb",
        "description": "To throw something with force",
        "example": "He yeeted the empty can into the recycling bin.",
    },
    {
        "word": "Vivid",
        "parts_of_speech": "Adjective",
        "description": "Producing powerful feelings or strong images",
        "example": "She gave a vivid description of her trip to the mountains.",
    },
    {
        "word": "Simp",
        "parts_of_speech": "Verb",
        "description": "To obsess over someone you like",
        "example": "He's always simping for that celebrity on Twitter.",
    },
    {
        "word": "Majestic",
        "parts_of_speech": "Adjective",
        "description": "Having impressive beauty or dignity",
        "example": "The majestic eagle soared above the cliffs.",
    },
    {
        "word": "Noob",
        "parts_of_speech": "Noun",
        "description": "A beginner or inexperienced person",
        "example": "I'm such a noob at this game—can you help me?",
    },
    {
        "word": "Exquisite",
        "parts_of_speech": "Adjective",
        "description": "Extremely beautiful and delicate",
        "example": "The jewelry featured exquisite craftsmanship.",
    },
    {
        "word": "Glow-up",
        "parts_of_speech": "Noun",
        "description": "A transformation for the better",
        "example": "Her high school glow-up was incredible!",
    },
    {
        "word": "Pragmatic",
        "parts_of_speech": "Adjective",
        "description": "Dealing with things sensibly",
        "example": "We need a pragmatic solution to this problem.",
    },
    {
        "word": "Fam",
        "parts_of_speech": "Noun",
        "description": "Close friends or family",
        "example": "I'm going out with the fam tonight.",
    },
    {
        "word": "Tenacious",
        "parts_of_speech": "Adjective",
        "description": "Persistent, not giving up easily",
        "example": "Her tenacious attitude helped her overcome obstacles.",
    },
    {
        "word": "Salvage",
        "parts_of_speech": "Verb",
        "description": "To rescue or save something",
        "example": "We managed to salvage some furniture from the fire.",
    },
    {
        "word": "Boujee",
        "parts_of_speech": "Adjective",
        "description": "Fancy or high-class",
        "example": "They stayed at a boujee resort in the Maldives.",
    },
    {
        "word": "Ephemeral",
        "parts_of_speech": "Adjective",
        "description": "Lasting for a very short time",
        "example": "The ephemeral beauty of cherry blossoms is celebrated in Japan.",
    },
    {
        "word": "Snatched",
        "parts_of_speech": "Adjective",
        "description": "Looking extremely good",
        "example": "Your outfit is absolutely snatched today!",
    },
    {
        "word": "Pinnacle",
        "parts_of_speech": "Noun",
        "description": "The highest point of achievement",
        "example": "Winning the Oscar was the pinnacle of her career.",
    },

    {
        "word": "Binge",
        "parts_of_speech": "Verb",
        "description": "To consume a lot of something quickly",
        "example": "I binged the entire series in one weekend.",
    },
    {
        "word": "Pensive",
        "parts_of_speech": "Adjective",
        "description": "Engaged in deep thought",
        "example": "She had a pensive expression as she stared out the window.",
    },
    {
        "word": "Drab",
        "parts_of_speech": "Adjective",
        "description": "Dull and boring",
        "example": "The office walls were painted a drab gray.",
    },
    {
        "word": "Zen",
        "parts_of_speech": "Adjective",
        "description": "Peaceful and calm",
        "example": "After yoga, I feel totally zen.",
    },
    {
        "word": "Quirky",
        "parts_of_speech": "Adjective",
        "description": "Unusual in an attractive way",
        "example": "I love her quirky sense of style.",
    },
    {
        "word": "FOMO",
        "parts_of_speech": "Noun",
        "description": "Fear of missing out",
        "example": "I wasn't going to go, but I got FOMO at the last minute.",
    },
    {
        "word": "Mellow",
        "parts_of_speech": "Adjective",
        "description": "Relaxed and unhurried",
        "example": "We had a mellow evening just watching movies.",
    },
    {
        "word": "Radiant",
        "parts_of_speech": "Adjective",
        "description": "Shining brightly; full of joy",
        "example": "The bride looked radiant in her wedding dress.",
    },
    {
        "word": "Slay",
        "parts_of_speech": "Verb",
        "description": "To do something exceptionally well",
        "example": "She absolutely slayed her performance.",
    },
    {
        "word": "Tedious",
        "parts_of_speech": "Adjective",
        "description": "Too long, slow, or dull",
        "example": "Filling out these forms is so tedious.",
    },
    {
        "word": "Venture",
        "parts_of_speech": "Noun",
        "description": "A risky undertaking",
        "example": "Starting a business is quite a venture.",
    },
    {
        "word": "Yikes",
        "parts_of_speech": "Exclamation",
        "description": "Expression of alarm or concern",
        "example": "Yikes! I almost forgot about the meeting!",
    },
    {
        "word": "Zesty",
        "parts_of_speech": "Adjective",
        "description": "Full of flavor or energy",
        "example": "The salad had a zesty lemon dressing.",
    },
    {
        "word": "Nifty",
        "parts_of_speech": "Adjective",
        "description": "Particularly good or effective",
        "example": "That's a nifty little gadget you've got there.",
    },
    {
        "word": "Ominous",
        "parts_of_speech": "Adjective",
        "description": "Suggesting something bad will happen",
        "example": "The dark clouds looked ominous.",
    },
    {
        "word": "Pique",
        "parts_of_speech": "Verb",
        "description": "To stimulate interest or curiosity",
        "example": "The mysterious trailer piqued my interest in the movie.",
    },
    {
        "word": "Janky",
        "parts_of_speech": "Adjective",
        "description": "Of poor quality; unreliable",
        "example": "My phone's been really janky lately.",
    },
    {
        "word": "Vexed",
        "parts_of_speech": "Adjective",
        "description": "Annoyed, frustrated, or worried",
        "example": "He was clearly vexed by the constant interruptions.",
    },
    {
        "word": "Ubiquitous",
        "parts_of_speech": "Adjective",
        "description": "Present everywhere",
        "example": "Smartphones have become ubiquitous in modern society.",
    },
    {
        "word": "Tweak",
        "parts_of_speech": "Verb",
        "description": "To make small adjustments",
        "example": "I just need to tweak the design a bit.",
    },
    {
        "word": "Savage",
        "parts_of_speech": "Adjective",
        "description": "Extremely good or impressive",
        "example": "That comeback was absolutely savage!",
    },
    {
        "word": "Rant",
        "parts_of_speech": "Verb",
        "description": "To speak or shout at length",
        "example": "He went on a rant about poor customer service.",
    },
    {
        "word": "Quaint",
        "parts_of_speech": "Adjective",
        "description": "Attractively unusual or old-fashioned",
        "example": "We stayed in a quaint little cottage by the sea.",
    },
    {
        "word": "Optimal",
        "parts_of_speech": "Adjective",
        "description": "Best or most favorable",
        "example": "This temperature is optimal for baking bread.",
    },
    {
        "word": "Nostalgic",
        "parts_of_speech": "Adjective",
        "description": "Longing for the past",
        "example": "Seeing my old school made me feel nostalgic.",
    },
    {
        "word": "Mundane",
        "parts_of_speech": "Adjective",
        "description": "Dull or ordinary",
        "example": "I need a break from these mundane tasks.",
    },
    {
        "word": "Lush",
        "parts_of_speech": "Adjective",
        "description": "Growing luxuriantly",
        "example": "The garden was lush after all the rain.",
    },
    {
        "word": "Keen",
        "parts_of_speech": "Adjective",
        "description": "Eager or enthusiastic",
        "example": "She's keen to start her new job.",
    },
    {
        "word": "Jovial",
        "parts_of_speech": "Adjective",
        "description": "Cheerful and friendly",
        "example": "His jovial personality made him popular at parties.",
    },
    {
        "word": "Irate",
        "parts_of_speech": "Adjective",
        "description": "Feeling or characterized by great anger",
        "example": "Customers became irate when the flight was canceled.",
    },
    {
        "word": "Humblebrag",
        "parts_of_speech": "Noun",
        "description": "A modest statement that's actually a boast",
        "example": "Saying 'Ugh, my hair looks awful today' when it looks great is a humblebrag.",
    },
    {
        "word": "Gritty",
        "parts_of_speech": "Adjective",
        "description": "Showing courage and determination",
        "example": "The team showed gritty determination to win.",
    },
    {
        "word": "Fleek",
        "parts_of_speech": "Adjective",
        "description": "Perfectly done or styled",
        "example": "Her eyebrows were on fleek today.",
    },
    {
        "word": "Eccentric",
        "parts_of_speech": "Adjective",
        "description": "Unconventional and slightly strange",
        "example": "The eccentric professor collected unusual artifacts.",
    },
    {
        "word": "Dank",
        "parts_of_speech": "Adjective",
        "description": "Excellent (or unpleasantly damp)",
        "example": "Those memes are absolutely dank.",
    },
    {
        "word": "Crisp",
        "parts_of_speech": "Adjective",
        "description": "Fresh and clean",
        "example": "The morning air was crisp and cool.",
    },
    {
        "word": "Bogus",
        "parts_of_speech": "Adjective",
        "description": "Fake or false",
        "example": "That's a totally bogus excuse.",
    },
    {
        "word": "Aesthetic",
        "parts_of_speech": "Adjective",
        "description": "Concerned with beauty",
        "example": "Her Instagram feed has a very cohesive aesthetic.",
    },
    {
        "word": "Yonder",
        "parts_of_speech": "Adverb",
        "description": "At some distance in the direction indicated",
        "example": "The village lies yonder, beyond the hills.",
    },
    {
        "word": "Xenial",
        "parts_of_speech": "Adjective",
        "description": "Relating to hospitality between host and guest",
        "example": "The xenial traditions of the region were fascinating.",
    },
    {
        "word": "Woke",
        "parts_of_speech": "Adjective",
        "description": "Aware of social injustices",
        "example": "The documentary really made me more woke about these issues.",
    },

    {
        "word": "Uncanny",
        "parts_of_speech": "Adjective",
        "description": "Strange or mysterious",
        "example": "The resemblance between the twins was uncanny.",
    },
    {
        "word": "Tranquil",
        "parts_of_speech": "Adjective",
        "description": "Free from disturbance",
        "example": "The garden was a tranquil retreat.",
    },
    {
        "word": "Squad",
        "parts_of_speech": "Noun",
        "description": "A group of friends",
        "example": "I'm going to the movies with my squad.",
    },
    {
        "word": "Robust",
        "parts_of_speech": "Adjective",
        "description": "Strong and healthy",
        "example": "The company reported robust earnings this quarter.",
    },
    {
        "word": "Quibble",
        "parts_of_speech": "Verb",
        "description": "Argue about trivial matters",
        "example": "Let's not quibble over small details.",
    },
    {
        "word": "Prolific",
        "parts_of_speech": "Adjective",
        "description": "Producing much fruit or work",
        "example": "He was a prolific writer, publishing dozens of novels.",
    },
    {
        "word": "Opaque",
        "parts_of_speech": "Adjective",
        "description": "Not able to be seen through",
        "example": "The glass was opaque, preventing us from seeing inside.",
    },
    {
        "word": "Nimble",
        "parts_of_speech": "Adjective",
        "description": "Quick and light in movement",
        "example": "The nimble athlete easily avoided the defenders.",
    },
    {
        "word": "Mirth",
        "parts_of_speech": "Noun",
        "description": "Amusement, especially as expressed in laughter",
        "example": "The comedy show filled the room with mirth.",
    },
    {
        "word": "Lithe",
        "parts_of_speech": "Adjective",
        "description": "Thin, supple, and graceful",
        "example": "The dancer had a lithe, graceful body.",
    },
    {
        "word": "Kitsch",
        "parts_of_speech": "Noun",
        "description": "Art or objects considered tasteless but appreciated ironically",
        "example": "The apartment was decorated with vintage kitsch from the 1950s.",
    },
    {
        "word": "Jubilant",
        "parts_of_speech": "Adjective",
        "description": "Feeling or expressing great happiness",
        "example": "The team was jubilant after their victory.",
    },
    {
        "word": "Innate",
        "parts_of_speech": "Adjective",
        "description": "Inborn; natural",
        "example": "She seems to have an innate talent for music.",
    },
    {
        "word": "Haven",
        "parts_of_speech": "Noun",
        "description": "A place of safety",
        "example": "The library was her haven from the noisy dorm.",
    },
    {
        "word": "Gloat",
        "parts_of_speech": "Verb",
        "description": "Contemplate or dwell on one's own success with smugness",
        "example": "It's not nice to gloat when you win.",
    },
    {
        "word": "Fervent",
        "parts_of_speech": "Adjective",
        "description": "Having or displaying passionate intensity",
        "example": "She was a fervent supporter of animal rights.",
    },
    {
        "word": "Epic",
        "parts_of_speech": "Adjective",
        "description": "Heroic or grand in scale",
        "example": "We had an epic road trip across the country.",
    },
    {
        "word": "Dapper",
        "parts_of_speech": "Adjective",
        "description": "Neat and trim in dress",
        "example": "He looked quite dapper in his new suit.",
    },
    {
        "word": "Cajole",
        "parts_of_speech": "Verb",
        "description": "Persuade with flattery",
        "example": "She managed to cajole him into helping with the project.",
    },
    {
        "word": "Brisk",
        "parts_of_speech": "Adjective",
        "description": "Active and energetic",
        "example": "We went for a brisk walk in the park.",
    },
    {
        "word": "Aplomb",
        "parts_of_speech": "Noun",
        "description": "Self-confidence, especially in a demanding situation",
        "example": "She handled the difficult questions with aplomb.",
    },
    {
        "word": "Zenith",
        "parts_of_speech": "Noun",
        "description": "The highest point",
        "example": "Her career reached its zenith when she won the award.",
    },
    {
        "word": "Yummy",
        "parts_of_speech": "Adjective",
        "description": "Delicious",
        "example": "This cake is absolutely yummy!",
    },
    {
        "word": "Xeric",
        "parts_of_speech": "Adjective",
        "description": "Adapted to a dry environment",
        "example": "Cacti are xeric plants that thrive in deserts.",
    },
    {
        "word": "Witty",
        "parts_of_speech": "Adjective",
        "description": "Showing quick and inventive verbal humor",
        "example": "Her witty remarks kept everyone entertained.",
    },
    {
        "word": "Vex",
        "parts_of_speech": "Verb",
        "description": "Make someone feel annoyed or frustrated",
        "example": "The difficult puzzle vexed him for hours.",
    },
    {
        "word": "Unfazed",
        "parts_of_speech": "Adjective",
        "description": "Not surprised or worried",
        "example": "She was unfazed by the sudden change in plans.",
    },
    {
        "word": "Tepid",
        "parts_of_speech": "Adjective",
        "description": "Only slightly warm",
        "example": "The coffee had gone tepid by the time I drank it.",
    },
    {
        "word": "Svelte",
        "parts_of_speech": "Adjective",
        "description": "Slender and elegant",
        "example": "The model had a svelte figure.",
    },
    {
        "word": "Ruddy",
        "parts_of_speech": "Adjective",
        "description": "Having a healthy red color",
        "example": "His face was ruddy from the cold wind.",
    },
    {
        "word": "Quell",
        "parts_of_speech": "Verb",
        "description": "Put an end to something",
        "example": "The police worked to quell the riot.",
    },
    {
        "word": "Posh",
        "parts_of_speech": "Adjective",
        "description": "Elegant or stylishly luxurious",
        "example": "They stayed at a posh hotel in London.",
    },
    {
        "word": "Ogle",
        "parts_of_speech": "Verb",
        "description": "Stare at in a lecherous manner",
        "example": "It's rude to ogle people like that.",
    },
    {
        "word": "Nosh",
        "parts_of_speech": "Verb",
        "description": "Eat food enthusiastically",
        "example": "We noshed on snacks while watching the game.",
    },
    {
        "word": "Moxie",
        "parts_of_speech": "Noun",
        "description": "Force of character, determination",
        "example": "You've got to admire her moxie.",
    },
    {
        "word": "Lurk",
        "parts_of_speech": "Verb",
        "description": "Remain hidden to ambush",
        "example": "He tends to lurk in online forums without posting.",
    },
    {
        "word": "Kudos",
        "parts_of_speech": "Noun",
        "description": "Praise and honor received for achievement",
        "example": "Kudos to you for finishing the marathon!",
    },
    {
        "word": "Jaded",
        "parts_of_speech": "Adjective",
        "description": "Tired or lacking enthusiasm",
        "example": "After years in the job, he'd become jaded about it.",
    },
    {
        "word": "Inept",
        "parts_of_speech": "Adjective",
        "description": "Having or showing no skill",
        "example": "His inept handling of the situation made things worse.",
    },
    {
        "word": "Haggle",
        "parts_of_speech": "Verb",
        "description": "Dispute or bargain persistently",
        "example": "We managed to haggle the price down a bit.",
    },
    {
        "word": "Glitch",
        "parts_of_speech": "Noun",
        "description": "A sudden malfunction",
        "example": "There was a glitch in the system that caused delays.",
    },
    {
        "word": "Frolic",
        "parts_of_speech": "Verb",
        "description": "Play or move about cheerfully",
        "example": "The children frolicked in the park.",
    },
    {
        "word": "Eerie",
        "parts_of_speech": "Adjective",
        "description": "Strange and frightening",
        "example": "The abandoned house had an eerie atmosphere.",
    },
    {
        "word": "Dwindle",
        "parts_of_speech": "Verb",
        "description": "Diminish gradually in size or amount",
        "example": "Our supplies began to dwindle as the week progressed.",
    },
    {
        "word": "Covet",
        "parts_of_speech": "Verb",
        "description": "Yearn to possess something",
        "example": "She coveted her neighbor's beautiful garden.",
    },
    {
        "word": "Bland",
        "parts_of_speech": "Adjective",
        "description": "Lacking strong features or characteristics",
        "example": "The soup was rather bland and needed more seasoning.",
    },

    {
        "word": "Vibe",
        "parts_of_speech": "Noun",
        "description": "The emotional atmosphere or feeling of a place or situation",
        "example": "This café has such a chill vibe."
    },
    {
        "word": "Flex",
        "parts_of_speech": "Verb",
        "description": "To show off something impressive",
        "example": "He flexed his new gaming setup on Instagram."
    },
    {
        "word": "Ghost",
        "parts_of_speech": "Verb",
        "description": "To suddenly stop all communication with someone",
        "example": "After two dates, she just ghosted me."
    },
    {
        "word": "Extra",
        "parts_of_speech": "Adjective",
        "description": "Over-the-top, dramatic, or excessive",
        "example": "Bringing a marching band to prom was so extra."
    },
    {
        "word": "FOMO",
        "parts_of_speech": "Noun",
        "description": "Fear of missing out on exciting events",
        "example": "I got FOMO seeing everyone at the concert without me."
    },
    {
        "word": "Glow-up",
        "parts_of_speech": "Noun",
        "description": "A dramatic transformation for the better",
        "example": "Her high school glow-up was incredible."
    },
    {
        "word": "Snack",
        "parts_of_speech": "Noun",
        "description": "An attractive person (slang)",
        "example": "That new actor is a total snack."
    },
    {
        "word": "Tea",
        "parts_of_speech": "Noun",
        "description": "Gossip or juicy information",
        "example": "Spill the tea about what happened last night!"
    },
    {
        "word": "Woke",
        "parts_of_speech": "Adjective",
        "description": "Aware of social injustices",
        "example": "She's very woke about environmental issues."
    },
    {
        "word": "Yas",
        "parts_of_speech": "Exclamation",
        "description": "An expression of excitement or approval",
        "example": "Yas queen! You look amazing!"
    },
    {
        "word": "Binge",
        "parts_of_speech": "Verb",
        "description": "To consume large amounts of media quickly",
        "example": "We binged the entire season in one night."
    },
    {
        "word": "Cancel",
        "parts_of_speech": "Verb",
        "description": "To stop supporting someone publicly",
        "example": "People tried to cancel the comedian over old jokes."
    },
    {
        "word": "Doomscroll",
        "parts_of_speech": "Verb",
        "description": "To obsessively read negative news online",
        "example": "I stayed up doomscrolling about the election."
    },
    {
        "word": "Eco-friendly",
        "parts_of_speech": "Adjective",
        "description": "Not harmful to the environment",
        "example": "We switched to eco-friendly packaging."
    },
    {
        "word": "Fintech",
        "parts_of_speech": "Noun",
        "description": "Technology in the financial sector",
        "example": "Mobile banking apps are part of the fintech revolution."
    },
    {
        "word": "GOAT",
        "parts_of_speech": "Noun",
        "description": "Greatest of All Time (acronym)",
        "example": "Many consider Serena Williams the GOAT of tennis."
    },
    {
        "word": "Hack",
        "parts_of_speech": "Noun",
        "description": "A clever solution or shortcut",
        "example": "This ice cube tray hack saves so much time."
    },
    {
        "word": "Influencer",
        "parts_of_speech": "Noun",
        "description": "Someone who affects purchase decisions",
        "example": "The beauty influencer recommended this moisturizer."
    },
    {
        "word": "JOMO",
        "parts_of_speech": "Noun",
        "description": "Joy of missing out (opposite of FOMO)",
        "example": "I'm feeling major JOMO staying home tonight."
    },
    {
        "word": "Meme",
        "parts_of_speech": "Noun",
        "description": "Humorous internet content that spreads quickly",
        "example": "That cat meme had me laughing all day."
    },
    {
        "word": "Noob",
        "parts_of_speech": "Noun",
        "description": "A beginner or inexperienced person",
        "example": "I'm such a noob at this game."
    },
    {
        "word": "OOTD",
        "parts_of_speech": "Noun",
        "description": "Outfit of the day (social media term)",
        "example": "She posted her OOTD on Instagram."
    },
    {
        "word": "Pog",
        "parts_of_speech": "Adjective",
        "description": "Exciting or impressive (gaming slang)",
        "example": "That goal was absolutely pog!"
    },
    {
        "word": "Quarantine",
        "parts_of_speech": "Verb",
        "description": "To isolate due to health concerns",
        "example": "We had to quarantine after our trip."
    },
    {
        "word": "Rizz",
        "parts_of_speech": "Noun",
        "description": "Charisma or ability to attract others",
        "example": "He's got serious rizz with the ladies."
    },
    {
        "word": "Simp",
        "parts_of_speech": "Noun",
        "description": "Someone who does too much for someone they like",
        "example": "He's such a simp for his crush."
    },
    {
        "word": "Throwback",
        "parts_of_speech": "Noun",
        "description": "A nostalgic memory or item from the past",
        "example": "Here's a throwback to our 2010 vacation."
    },
    {
        "word": "Unplug",
        "parts_of_speech": "Verb",
        "description": "To disconnect from technology",
        "example": "I need to unplug this weekend."
    },
    {
        "word": "Viral",
        "parts_of_speech": "Adjective",
        "description": "Spreading rapidly online",
        "example": "That dance video went viral overnight."
    },
    {
        "word": "Wanderlust",
        "parts_of_speech": "Noun",
        "description": "A strong desire to travel",
        "example": "Looking at travel photos gives me wanderlust."
    },
    {
        "word": "Zoom",
        "parts_of_speech": "Verb",
        "description": "To video conference (from Zoom software)",
        "example": "Let's zoom tomorrow to discuss the project."
    },
    {
        "word": "Adorable",
        "parts_of_speech": "Adjective",
        "description": "Extremely cute or charming",
        "example": "The puppy was absolutely adorable."
    },
    {
        "word": "Breathtaking",
        "parts_of_speech": "Adjective",
        "description": "Stunningly beautiful",
        "example": "The sunset over the ocean was breathtaking."
    },
    {
        "word": "Chill",
        "parts_of_speech": "Adjective",
        "description": "Relaxed or easygoing",
        "example": "He's got such a chill personality."
    },
    {
        "word": "Dope",
        "parts_of_speech": "Adjective",
        "description": "Excellent or cool",
        "example": "Those new sneakers are dope!"
    },
    {
        "word": "Epic",
        "parts_of_speech": "Adjective",
        "description": "Remarkably great",
        "example": "The concert last night was epic."
    },
    {
        "word": "Fierce",
        "parts_of_speech": "Adjective",
        "description": "Powerful and determined",
        "example": "She gave a fierce performance."
    },
    {
        "word": "Gorgeous",
        "parts_of_speech": "Adjective",
        "description": "Beautiful or attractive",
        "example": "You look gorgeous in that dress."
    },
    {
        "word": "Hilarious",
        "parts_of_speech": "Adjective",
        "description": "Extremely funny",
        "example": "The comedian's jokes were hilarious."
    },
    {
        "word": "Iconic",
        "parts_of_speech": "Adjective",
        "description": "Widely recognized and admired",
        "example": "That red carpet look was iconic."
    },
    {
        "word": "Janky",
        "parts_of_speech": "Adjective",
        "description": "Of poor quality or unreliable",
        "example": "My phone's been acting janky lately."
    },

    {
        "word": "Legendary",
        "parts_of_speech": "Adjective",
        "description": "Remarkable enough to be famous",
        "example": "Their parties are legendary."
    },
    {
        "word": "Majestic",
        "parts_of_speech": "Adjective",
        "description": "Having impressive beauty",
        "example": "The mountains looked majestic at sunrise."
    },
    {
        "word": "Nifty",
        "parts_of_speech": "Adjective",
        "description": "Particularly good or effective",
        "example": "That's a nifty little gadget."
    },
    {
        "word": "Outstanding",
        "parts_of_speech": "Adjective",
        "description": "Exceptionally good",
        "example": "Your work has been outstanding."
    },
    {
        "word": "Phenomenal",
        "parts_of_speech": "Adjective",
        "description": "Remarkable or exceptional",
        "example": "The food at that restaurant was phenomenal."
    },
    {
        "word": "Quirky",
        "parts_of_speech": "Adjective",
        "description": "Unusual in an attractive way",
        "example": "I love her quirky sense of style."
    },
    {
        "word": "Rad",
        "parts_of_speech": "Adjective",
        "description": "Excellent or cool",
        "example": "That skateboard trick was rad."
    },
    {
        "word": "Savage",
        "parts_of_speech": "Adjective",
        "description": "Extremely impressive or harsh",
        "example": "Her comeback was absolutely savage."
    },
    {
        "word": "Trendy",
        "parts_of_speech": "Adjective",
        "description": "Very fashionable",
        "example": "That café is the trendy spot right now."
    },
    {
        "word": "Unreal",
        "parts_of_speech": "Adjective",
        "description": "Incredibly good",
        "example": "The graphics in that game are unreal."
    },
    {
        "word": "Vivid",
        "parts_of_speech": "Adjective",
        "description": "Producing powerful feelings",
        "example": "She gave a vivid description."
    },
    {
        "word": "Wholesome",
        "parts_of_speech": "Adjective",
        "description": "Promoting health or well-being",
        "example": "Their friendship is so wholesome."
    },
    {
        "word": "Xenial",
        "parts_of_speech": "Adjective",
        "description": "Friendly to strangers",
        "example": "The small town had a xenial atmosphere."
    },
    {
        "word": "Yummy",
        "parts_of_speech": "Adjective",
        "description": "Very tasty",
        "example": "This cake is absolutely yummy."
    },
    {
        "word": "Zesty",
        "parts_of_speech": "Adjective",
        "description": "Having strong pleasant flavor",
        "example": "The dressing was nice and zesty."
    },
    {
    "word": "Dismiss",
    "parts_of_speech": "Verb",
    "description": "To stop associating with someone or something; to disregard or reject",
    "example": "After the argument, she decided to dismiss him from her life completely.",
   },
   {
    "word": "Compliant",
    "parts_of_speech": "Adjective",
    "description": "Disposed to act in accordance with someone's wishes; obedient or yielding",
    "example": "The employee was always compliant with company policies.",
},
{
    "word": "Diffuse",
    "parts_of_speech": "Adjective",
    "description": "Spread out; not concentrated in one place",
    "example": "The light from the lamp was diffuse, creating a soft glow in the room.",
},
{
    "word": "Digression",
    "parts_of_speech": "Noun",
    "description": "A temporary departure from the main subject in speech or writing",
    "example": "The professor's digression about his vacation actually helped explain the economic concept better.",
},
{
    "word": "Facilitate",
    "parts_of_speech": "Verb",
    "description": "To make (an action or process) easier or less difficult",
    "example": "The new software will facilitate faster data analysis for our team.",
},
{
    "word": "Implicit",
    "parts_of_speech": "Adjective",
    "description": "Suggested or understood though not directly expressed",
    "example": "There was an implicit agreement that we wouldn't discuss politics at family dinners.",
},
{
    "word": "Approbation",
    "parts_of_speech": "Noun",
    "description": "Official acceptance, approval, or agreement",
    "example": "The new policy received widespread approbation from the board members.",
},
{
    "word": "Appropriate",
    "parts_of_speech": "Adjective",
    "description": "Suitable or proper for a particular person, place, or situation",
    "example": "Jeans are not appropriate attire for a formal wedding.",
},

    {
        "word": "Bombastic",
        "parts_of_speech": "Adjective",
        "description": "Ostentatiously lofty in style; inflated",
        "example": "The politician's bombastic speech was full of grandiose promises but little substance.",
    },
    {
        "word": "Contention",
        "parts_of_speech": "Noun",
        "description": "The act of competing, as for profit or a prize",
        "example": "There was fierce contention between the two companies for the government contract.",
    },
    {
        "word": "Audacity",
        "parts_of_speech": "Noun",
        "description": "Aggressive boldness in social situations",
        "example": "She had the audacity to correct the CEO during the board meeting.",
    },
    {
        "word": "Betray",
        "parts_of_speech": "Verb",
        "description": "To reveal or make known something, usually unintentionally",
        "example": "His nervous smile betrayed his lack of confidence in the plan.",
    },
    {
        "word": "Constituent",
        "parts_of_speech": "Noun",
        "description": "An abstract part of something",
        "example": "Trust is a key constituent of any healthy relationship.",
    },
    {
        "word": "Discrete",
        "parts_of_speech": "Adjective",
        "description": "Constituting a separate entity or part",
        "example": "The course is divided into five discrete modules.",
    },
    {
        "word": "Disinterested",
        "parts_of_speech": "Adjective",
        "description": "Unbiased; neutral",
        "example": "We need a disinterested third party to mediate the dispute.",
    },
    {
        "word": "Economical",
        "parts_of_speech": "Adjective",
        "description": "Avoiding waste; efficient",
        "example": "Her economical use of words made the report clear and concise.",
    },
    {
        "word": "Chronological",
        "parts_of_speech": "Adjective",
        "description": "Arranged in or relating to time order",
        "example": "The biography presents the events in chronological order.",
    },
    {
        "word": "Console",
        "parts_of_speech": "Verb, Noun",
        "description": "Lessen the suffering or grief (verb); a control panel or small table (noun)",
        "example": "She tried to console her friend after the loss (verb). The game console stopped working (noun).",
    },
    {
        "word": "Consolidate",
        "parts_of_speech": "Verb",
        "description": "Unite, combine, solidify, make coherent",
        "example": "The company plans to consolidate its operations into one central office.",
    },
    {
        "word": "Disabuse",
        "parts_of_speech": "Verb",
        "description": "Free someone from a mistake in thinking",
        "example": "Let me disabuse you of the notion that this will be easy.",
    },
    {
        "word": "Dispatch",
        "parts_of_speech": "Noun, Verb",
        "description": "Speed, promptness (noun); send off or deal with quickly (verb)",
        "example": "He completed the task with remarkable dispatch (noun). We'll dispatch the package today (verb).",
    },
    {
        "word": "Feasible",
        "parts_of_speech": "Adjective",
        "description": "Possible; logical or likely; suitable",
        "example": "After reviewing the budget, the plan seems feasible.",
    },
    {
        "word": "Homogeneous",
        "parts_of_speech": "Adjective",
        "description": "Of the same kind; uniform throughout",
        "example": "The test group was homogeneous in age and background.",
    },
    {
        "word": "Pronounced",
        "parts_of_speech": "Adjective",
        "description": "Distinct, strong, clearly indicated",
        "example": "There was a pronounced difference between the two approaches.",
    },


    {
        "word": "Succeeding",
        "parts_of_speech": "Adjective",
        "description": "Coming after or following",
        "example": "The succeeding chapters will cover more advanced topics.",
    },
    {
        "word": "Synchronous",
        "parts_of_speech": "Adjective",
        "description": "Happening at the same time; occurring at the same rate and thus happening together repeatedly",
        "example": "The dancers' movements were perfectly synchronous with the music.",
    },
    {
        "word": "Verbose",
        "parts_of_speech": "Adjective",
        "description": "Using more words than needed; wordy",
        "example": "His verbose explanation could have been summarized in two sentences.",
    },
    {
        "word": "Virtual",
        "parts_of_speech": "Adjective",
        "description": "Existing only in the mind or by means of a computer network; existing in results or in essence though not in actual fact",
        "example": "The team held a virtual meeting using video conferencing software.",
    },
    {
        "word": "Volatile",
        "parts_of_speech": "Adjective",
        "description": "1. Varying, inconstant, fleeting 2. Tending to violence, explosive",
        "example": "1. The stock market has been particularly volatile this month. 2. The chemical compound is highly volatile and must be handled with care.",
    },

    {
        "word": "Table",
        "parts_of_speech": "Verb",
        "description": "To lay aside a proposal or discussion for later consideration, often as a way to postpone it indefinitely",
        "example": "The committee voted to table the controversial motion until their next meeting.",
    },
    {
    "word": "Aftermath",
    "parts_of_speech": "Noun",
    "description": "The consequences or effects following a significant (often negative) event",
    "example": "In the aftermath of the hurricane, volunteers helped rebuild damaged homes.",
},
{
    "word": "Subjective",
    "parts_of_speech": "Adjective",
    "description": "Existing in the mind or relating to one's own thoughts, opinions, or emotions; personal and influenced by individual perspective",
    "example": "Art criticism is often subjective, as people experience paintings differently.",
},
{
    "word": "Stingy",
    "parts_of_speech": "Adjective",
    "description": "Not generous with money; unwilling to spend or give",
    "example": "The stingy millionaire refused to donate even a small amount to charity.",
},
{
    "word": "Static",
    "parts_of_speech": "Adjective",
    "description": "1. Fixed in place; not moving or changing 2. Lacking movement, vitality, or progress",
    "example": "1. The stock prices remained static for weeks. 2. The play's static plot failed to engage the audience.",
},

    {
        "word": "Oblige",
        "parts_of_speech": "Verb",
        "description": "To do as someone asks or desires in order to help or please them",
        "example": "She obliged her guests with fresh coffee and pastries.",
    },
    {
        "word": "Opportune",
        "parts_of_speech": "Adjective",
        "description": "Well-chosen or particularly favorable time",
        "example": "The rain came at an opportune moment, just as we finished the outdoor ceremony.",
    },
    {
        "word": "Intend",
        "parts_of_speech": "Verb",
        "description": "To have as a plan or purpose",
        "example": "We intend to complete the project by Friday.",
    },
    {
        "word": "Concern",
        "parts_of_speech": "Noun/Verb",
        "description": "1. (n) A matter of interest or importance 2. (v) To cause worry",
        "example": "1. Safety is our primary concern. 2. The news concerned all the investors.",
    },
    {
        "word": "Issue",
        "parts_of_speech": "Noun",
        "description": "An important topic or problem for debate or discussion",
        "example": "The privacy issues surrounding mobile apps are increasingly complex.",
    },
    {
        "word": "Approach",
        "parts_of_speech": "Verb",
        "description": "To come near or nearer to something in distance",
        "example": "As we approached the city, traffic grew heavier.",
    },
    {
        "word": "Establish",
        "parts_of_speech": "Verb",
        "description": "To set up or found something on a firm basis",
        "example": "The colony was established in 1604 and grew rapidly.",
    },
    {
        "word": "Utter",
        "parts_of_speech": "Verb/Adjective",
        "description": "1. (v) To say something aloud 2. (adj) Complete",
        "example": "1. She didn't utter a word during the meeting. 2. It was utter chaos after the announcement.",
    },
    {
        "word": "Apparent",
        "parts_of_speech": "Adjective",
        "description": "Clearly visible or understood; obvious",
        "example": "It became apparent that we would need more time to finish.",
    }
]



    
    for word_data in words_data:
        # Check if word already exists
        existing_word = db.query(WordOfTheDay).filter_by(word=word_data["word"]).first()
        if not existing_word:
            word_entry = WordOfTheDay(
                word=word_data["word"],
                parts_of_speech=word_data["parts_of_speech"],
                description=word_data["description"],
                example=word_data["example"],
            )
            db.add(word_entry)

    db.commit()


def schedule_word_of_the_day():
    scheduler = BackgroundScheduler()
    # Runs every day at midnight (00:00)
    scheduler.add_job(
        assign_todays_word,
        trigger=CronTrigger(hour=0, minute=0),
        name="Assign Word of the Day",
    )
    scheduler.start()


def assign_todays_word(db: Session):

    today = date.today()
    existing_word = db.query(DailyWord).filter(DailyWord.date == today).first()
    if existing_word:
        return
    random_word = db.query(WordOfTheDay).order_by(func.random()).first()

    # Assign it as today's word
    daily_word = DailyWord(date=today, word_id=random_word.id)
    db.add(daily_word)
    db.commit()


def send_daily_word_notification(db: Session):
    today = date.today()
    daily_word = db.query(DailyWord).filter(DailyWord.date == today).first()
    if not daily_word:
        raise HTTPException(status_code=404, detail="Today's word not found")
    fcm_tokens = db.query(FCMToken).filter(FCMToken.is_active.is_(True)).all()
    if not fcm_tokens:
        raise HTTPException(status_code=404, detail="No active FCM tokens found")
    for token in fcm_tokens:
        word_data = WordOfTheDayPayload(
            word=daily_word.word.word,
            parts_of_speech=daily_word.word.parts_of_speech,
            description=daily_word.word.description,
            example=daily_word.word.example,
        )
        send_word_notification(token=token.token, word_data=word_data)
