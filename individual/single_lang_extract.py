# encoding: utf-8

"""
Extract single language data (for English and Dutch).all
"""

from collections import defaultdict
import csv

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
CELEX_PATH = "/home/tresoldi/ownCloud/CALC/Data/celex2"

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
                

def main(ref, lang_id, output_file, lang_name):
    with open("../cldf/forms.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        data = [
            row['Form'] for row in reader
            if row['Language_ID'] == lang_id
        ]
    
    transcr = {}
    for form in data:
        # clean form for transcription
        clean_form = form.replace("(1)", "")
        clean_form = clean_form.replace("(2)", "")
        clean_form = clean_form.strip()
    
        transcr[form] = list(set(ref.get(clean_form, ['???'])))

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
