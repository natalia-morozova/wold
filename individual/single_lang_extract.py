# encoding: utf-8

"""
Extract single language data (for English and Dutch).all
"""

from collections import defaultdict
import csv
import re

# PROFILE FOR CELEX
PROFILE_EN = {
    'p'   : 'p',
    'b'   : 'b',
    't'   : 't',
    'd'   : 'd',
    'k'   : 'k',
    'g'   : 'ɡ',
    'N'   : 'ŋ',
    'm'   : 'm',
    'n'   : 'n',
    'l'   : 'l',
    'r'   : 'r',
    'f'   : 'f',
    'v'   : 'v',
    'T'   : 'θ',
    'D'   : 'ð',
    's'   : 's',
    'z'   : 'z',
    'S'   : 'ʃ',
    'Z'   : 'ʒ',
    'j'   : 'j',
    'x'   : 'x',
    'h'   : 'h',
    'w'   : 'w',
    'tS'  : 'tʃ',
    'dZ'  : 'dʒ',
    'N,'  : 'ŋ̩',
    'm,'  : 'm̩',
    'n,'  : 'n̩',
    'l,'  : 'l̩',
    'r*'  : 'ɹ',
    'I'   : 'ɪ',
    'E'   : 'ɛ',
    '&'   : 'æ',
    'V'   : 'ʌ',
    'O'   : 'ɒ',
    'U'   : 'ʊ',
    '@'   : 'ə',
    'i:'  : 'iː',
    'A'   : 'ɑ',
    'A:'  : 'ɑː',
    'e:'  : 'eː',
    'O:'  : 'ɔː',
    'u:'  : 'uː',
    '3:'  : 'ɜː',
    'eI'  : 'eɪ',
    'aI'  : 'aɪ',
    'OI'  : 'ɔɪ',
    '@U'  : 'əʊ',
    'aU'  : 'aʊ',
    'I@'  : 'ɪə',
    'E@'  : 'ɛə',
    'U@'  : 'ʊə',
    '&~'  : 'æ̃',
    'A~:' : 'ɑ̃ː',
    '&~:' : 'æ̃ː',
    'O~:' : 'ɔ̃ː',
}

PROFILE_NL = {
    'p'   : 'p',
    'b'   : 'b',
    't'   : 't',
    'd'   : 'd',
    'k'   : 'k',
    'g'   : 'ɡ',
    'N'   : 'ŋ',
    'm'   : 'm',
    'n'   : 'n',
    'l'   : 'l',
    'r'   : 'r',
    'f'   : 'f',
    'v'   : 'v',
    's'   : 's',
    'z'   : 'z',
    'S'   : 'ʃ',
    'Z'   : 'ʒ',
    'j'   : 'j',
    'x'   : 'x',
    'G'   : 'ɣ',
    'h'   : 'h',
    'w'   : 'ʋ',
    'dZ'  : 'dʒ',
    'i:'  : 'iː',
    'y:'  : 'yː',
    'e:'  : 'eː',
    'a:'  : 'aː',
    'o:'  : 'oː',
    'u:'  : 'uː',
    'I'   : 'ɪ',
    'E'   : 'ɛ',
    'A'   : 'ɑ',
    'O'   : 'ɔ',
    'U'   : 'ʏ',
    'U:'  : 'œː', # confirm
    '@'   : 'ə',
    '&:'  : 'øː',
    'E:'  : 'ɛː',
    'i::' : 'iːː',
    'O:'  : 'ɔː',
    'y::' : 'yːː', 
    'EI' : 'ɛi',
    'UI' : 'œy',
    'AU' : 'ɑu',
}

# PATH TO CELEX
CELEX_PATH = "/home/tresoldi/celex2"

def apply_profile(text, profile):
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace(" ", "")

    mapped = []
    while True:
        for i in range(len(text), 0, -1):
            substr = text[:i]
            if substr in profile:
                mapped.append(profile[substr])
                text = text[len(substr):]
                break
            
            if i == 1:
                input([str(mapped), text])
                mapped.append("???")
                text = text[1:]
                break
    
        if not text:
            break
            
    return ' '.join(mapped)


# TODO: American/British?
def read_celex(filename, profile, ortho, phono):
    # read all data
    with open("%s/%s" % (CELEX_PATH, filename)) as handler:
        data = [
            line.strip().split("\\") for line in handler
        ]

    # get only orthography and disc
    transcr = defaultdict(list)
    for entry in data:
        transcr[entry[ortho]].append(apply_profile(entry[phono], profile))
#        if "U:" in entry[phono]:
#            print(entry[ortho], entry[phono], apply_profile(entry[phono], profile))
#            input()

    
    return transcr
                
# exceptions
EN_TRANSCRIPT = {
    "unripe" : "ʌ n r aɪ p",
    "untie": "ʌ n t aɪ",
    }
DU_TRANSCRIPT = {
    "geitje": "x ɛi t j ə",
    "inwijdingsplechtigheid":"ɪ n ʋ ɛi d ɪ ŋ s p l ɛ x t ə x h ɛi t",
    "banyan":"b ɑ n j a n",
    "lichaamshaar":"l ɪ x aː m s h aː r",
    "mannetjes-":"m ɑ n ə t j ə s",
    "outrigger":"ɑu t r i ɣ ə r",
  "tatoeëring":"t a t u eː r ɪ ŋ",
    "wc": "ʋ eɪ s eɪ",

}

# replace for missing forms
EN_REPL = {
  "(be) silent" : "silent",
  "(finger)nail" : "nail", 
  "(good) luck" : "luck",
  "(sea)gull" : "gull",
  "(sting)ray" : "ray",
  "(tree-)stump" : "stump",
  "chili (pepper)" : "chilli",
  "judgment" : "judgement",
  "molar (tooth)" : "molar",
  "petrol(eum)" : "petrol",
  "temple(s)" : "temple",
  "wake (up)" : "wake",
  "wood(s)" : "wood",
  "banyan" : "banian",
  "hankie" : "hanky",
  "hiccough" : "hiccup",
  "how?" : "how",
  "what?":"what",
  "when?":"when",
  "where?":"where",
  "which?":"which",
  "who?":"who",
  "why?":"why",
  
  "be born" : ["be", "born", False],
  "birth certificate" : ["birth", "certificate", False],
  "driving licence" : ["driving", "licence", False],
  "fishing line" : ["fishing", "line", False],
  "fishing net": ["fishing", "net", False],
  "grass-skirt": ["grass", "skirt", False],
  "how many?" : ["how", "many", False],
  "how much?" : ["how", "much", False],
  "in front of": ["in", "front","of", False],
  "let go":["let", "go", False],
  "lightning bolt":["lightning", "bolt", False],
  "make love":["make", "love", False],
  "number plate":["number", "plate", False],
  "pubic hair":["pubic", "hair", False],
  "sugar cane":["sugar","cane", False],
  "to last":["to", "last", False],
  "tree trunk":["tree", "trunk", False],
  "turn around":["turn", "around", False],
  "doorpost" : ["door", "post", True],
  "fishhook" : ["fish", "hook", True],
  "netbag" : ["net", "bag", True],
  "shoulderblade":["shoulder", "blade", True],
}
DU_REPL = {
  "aan land gaan" : ["aan", "land", "gaan", False],
  "alcoholische drank" : ["alcoholische", "drank", False],
  "bos(je)" : "bos",
  "dakspar" : ["dak", "spar", True],
  "dennenappel" : ["dennen", "appel", True],
  "dorst hebben" : ["dorst", "hebben", False],
  "een scheet laten" : ["een", "scheet", "laten", False],
  "gaan liggen" : ["gaan", "liggen", False],
  "geboren worden" : ["geboren", "worden", False],
  "getij(de)" : "getij",
  "getrouwde man" : ["getrouwde", "man", False],
  "getrouwde vrouw" : ["getrouwde", "vrouw", False],
  "gevorkte tak" : ["gevorkte", "tak", False],
  "grasrokje" : ["gras", "rokje", True],
  "honger hebben" : ["honger", "hebben", False],
  "houden van": ["houden", "van", False],
  "in dienst nemen": ["in", "dienst", "nemen", False],
  "koelte toewaaien" : ["koelte", "toewaaien", False],
  "laat zijn" : ["laat", "zijn", False],
  "laten vallen" : ["laten", "vallen", False],
  "lemen baksteen" : ["lemen", "baksteen", False],
  "maniokbrood" : ["maniok", "brood", True],
  "naar beneden" : ["naar", "beneden", False],
  "naar beneden gaan": ["naar", "beneden", "gaan", False],
  "naar boven gaan" : ["naar", "boven", "gaan", False],
  "naar huis gaan":["naar", "huis", "gaan", False],
  "rode peper" :["rode", "peper", False],
  "ruggengraat" : ["ruggen", "graat", True],
  "schoonkind":["schoon", "kind", True],
  "schuldig zijn":["schuldig", "zijn", False],
  "seks hebben":["seks", "hebben", False],
  "sle(d)e":"slede",
  "spijt hebben":["spijt","hebben", False],
  "water putten":["water", "putten", False],
  "wild zwijn":["wild","zwijn", False],
  "zich haasten":["zich","haasten", False],
  "zich herinneren":["zich","herinneren", False],
  "zich omdraaien":["zich","omdraaien",False],
  "zich overgeven":["zich","overgeven", False],
  "zich terugtrekken":["zich","terugtrekken", False],
  "zoete aardappel":["zoete","aardappel", False],
  "zus(ter)":"zus",
  "zwanger worden":["zwanger","worden", False],
  
  "graafstok" : ["graaf", "stok", True],
  "initiatieplechtigheid" : ["initiatie", "plechtigheid", True],
  "inwijdingsplechtigheid" : ["inwijding", "plechtigheid", True],
  "insect":"insekt",
  
  "maïs":"mais",
  "nettas":["net", "tas", False],
  "paddenstoel":["padden", "stoel", True],
  "schroevendraaier":["schroeven", "draaier", True],
  "vergaderhuis":["vergader", "huis", True],
  "vissengif":["vissen","gif",True],
  "voetafdruk":["voet", "afdruk", True],
  
  "vrouwtjes-": "vrouwtjes",



}

def main(ref, lang_id, output_file, lang_name):
    with open("../cldf/forms.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        data = [
            row['Form'] for row in reader
            if row['Language_ID'] == lang_id
        ]
    
    # Which replacement dict to use
    if lang_id == "13":
        REPLACEMENT = EN_REPL
        TRANSCRIPT = EN_TRANSCRIPT
    else:
        REPLACEMENT = DU_REPL
        TRANSCRIPT = DU_TRANSCRIPT
   
    transcr = {}
    for form in data:
        if form in TRANSCRIPT:
            transcr[form] = [TRANSCRIPT[form]]
            continue
    
        # Run replacements
        if form in REPLACEMENT:
            form_to_use = REPLACEMENT[form]
        else:
            form_to_use = form

        if isinstance(form_to_use, list):
            phonos = [ref.get(sub_form, ['???']) for sub_form in form_to_use[:-1]]
            phonos = [list(set(ph))[0] for ph in phonos]
            
            if form_to_use[-1]:
                phono = [' '.join(phonos)]
            else:
                phono = [' # '.join(phonos)]
        else:
            # clean form for transcription
            clean_form = form_to_use.replace("(1)", "")
            clean_form = clean_form.replace("(2)", "")
            clean_form = clean_form.replace("(3)", "")
            clean_form = clean_form.strip()
        
            phono = list(set(ref.get(clean_form, ['???'])))
            if len(phono) > 1:
                phono = [phono[0]]
    
        transcr[form] = phono

    # output
    with open(output_file, 'w') as handler:
        handler.write("Grapheme\tIPA\tLanguages\n")

        for form in sorted(transcr):
            output_form = "^%s$" % form
            output_ipa = " ".join(transcr[form])
            buf = [output_form, output_ipa, lang_name]
        
            handler.write("\t".join(buf))
            handler.write("\n")


if __name__ == "__main__":
    # Read CELEX data
    english = read_celex('english/epw/epw.cd', PROFILE_EN, ortho=1, phono=8)
    dutch = read_celex('dutch/dpw/dpw.cd', PROFILE_NL, ortho=1, phono=6)

    # dutch 12, english 13
    main(english, "13", "stan1293.profile.tsv", "English")
    main(dutch, "12", "dutc1256.profile.tsv", "Dutch")
