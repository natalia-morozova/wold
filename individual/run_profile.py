# encoding: utf-8

import argparse
from collections import Counter
import csv
import tabulate

from segments import Profile, Tokenizer
from pyclts import TranscriptionSystem
import pyclts.models

BIPA = TranscriptionSystem('bipa')

SOUND_CLASSES = (
    pyclts.models.Vowel,
    pyclts.models.Consonant,
    pyclts.models.Marker,
    pyclts.models.Cluster,
    pyclts.models.ComplexSound,
    pyclts.models.Diphthong,
    pyclts.models.Tone)


def my_tokenizer(form, prf):
    form = "^%s$" % form.replace(" ", "{} ")

    i = 0
    tokens = []
    while True:
        added = False
        for length in range(len(form[i:]), 0, -1):
            needle = form[i:i+length]
            if needle in prf:
                tokens.append(prf[needle])
                i += length
                added = True
                break

        if not added:
            if form[i] == ' ':
                tokens.append("#")
            else:
                tokens.append('<%s>' % form[i])
            i += 1

        if i == len(form):
            break

    # Remove NULLs
    tokens = [token for token in tokens if token != "NULL"]

    return ' '.join(tokens)


def main(args):
    print(args)

    # Read raw profile, solving bug in `segments`,
    # and add the space character fix
    profile_file = "%s.profile.tsv" % args.glottocode
    with open(profile_file, encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        my_profile = {row['Grapheme'] : row['IPA'] for row in reader}
    my_profile["{}"] = "NULL"

    # Read the lexical data
    with open('%s.tsv' % args.glottocode, encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        # collect entries
        data = []
        for row in reader:


            #form = "^%s$" % row['Form'].strip()
            form = row['Form'].strip()

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
                'Segments':             my_tokenizer(form, my_profile),
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
            isinstance(sound, SOUND_CLASSES)
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

    # either show the errors or write output
    if err_count == 0:
        FIELDS = ['ID', 'Source_ID', 'Word_ID', 'Doculect',
            'Glottocode', 'Concept', 'Concepticon_Gloss',
            'Concepticon_ID', 'original_script', 'Value',
            'Form', 'Segments']

        with open('%s.segmented.tsv' % args.glottocode, 'w', encoding='utf8') as output:
            # write header
            output.write('\t'.join(FIELDS))
            output.write('\n')

            for row in data:
                buf = [row[field] for field in FIELDS]
                output.write('\t'.join(buf))
                output.write('\n')

    else:
    	# show total number of errors
        print("Total errors:", err_count-1)

        # show list of unknowns
        unk_counter = Counter(unknown)
        unk_table = [
            [entry[0], str([entry[0]]), entry[1]] for entry in unk_counter.most_common(args.seg_cases)
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
