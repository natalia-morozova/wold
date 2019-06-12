# encoding: utf-8

import argparse
from collections import Counter
import csv
import tabulate

from segments import Tokenizer
from pyclts import TranscriptionSystem
import pyclts.models

BIPA = TranscriptionSystem('bipa')

def main(args):
    print(args)

    # build the tokenize for the requested glottocode
    tokenizer = Tokenizer(profile="%s.profile.tsv" % args.glottocode)

    # Read the lexical data
    with open('%s.tsv' % args.glottocode) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        # collect entries
        data = []
        for row in reader:
            form = "^%s$" % row['Form'].strip()

            entry = {
                'ID':                   row['ID'],
                'Source_ID':            row['Source_ID'],
                'Word_ID':              row['Word_ID'],
                'Doculect':             row['Doculect'],
                'Glottocode':           row['Glottocode'],
                'Concept':              row['Concept'],
                'Concepticon_Gloss':    row['Concepticon_Gloss'],
                'Concepticon_ID':       row['Concepticon_ID'],
                'original_script':      row['original_script'],
                'Value':                row['Value'],
                'Form':                 form,
                'Segments':             tokenizer(form),
            }

            data.append(entry)

    # Check all entries
    errors = []
    unknown = []
    err_count = 0
    for row in data:
        segments = row['Segments'].split()
        sounds = [BIPA[segment] for segment in segments]
        valids = [
            isinstance(sound, (pyclts.models.Vowel, pyclts.models.Consonant))
            for sound in sounds
        ]

        for snd_idx, (sound, valid) in enumerate(zip(sounds, valids)):
            if valid:
                continue

            # buffer of the errors
            buf = [
                str(err_count+1),
                row['ID'],
                row['Concepticon_Gloss'],
                row['Form'],
                str(snd_idx+1),
                sound.source,
                ' '.join(segments),
            ]
            err_count += 1

            # add to list of errors
            errors.append(buf)
            unknown.append(sound.source)

    # show list of unknowns
    unk_counter = Counter(unknown)
    unk_table = [
        [entry[0], entry[1]] for entry in unk_counter.most_common(args.seg_cases)
    ]
    print("Most common source errors")
    print("=========================")
    print(tabulate.tabulate(unk_table))
    print()

    # show cases in order
    err_table = [['#', 'Row', 'Concept', 'Form', 'Sound #', 'Sound Value', 'Segments']]
    err_table += [
        entry for entry in errors[:args.num_cases]
    ]
    print("First error cases")
    print("=================")
    print(tabulate.tabulate(err_table))

if __name__ == "__main__":
    # define parser
    parser = argparse.ArgumentParser(description='Apply a profile')
    parser.add_argument('glottocode', type=str,
        help="Specify the glottocode to work with")
    parser.add_argument('--num_cases', type=int, default=30,
        help="Maximum number of cases to list, defaults to 30.")
    parser.add_argument('--seg_cases', type=int, default=30,
        help="Maximum number of segment errors to list, defaults to 30.")

    args = parser.parse_args()
    main(args)
