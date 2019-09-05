import attr
import glob
from clldutils.path import Path
from pylexibank.dataset import Lexeme
from pylexibank.providers import clld
import os.path
import re

from segments import Profile, Tokenizer
import unicodedata

@attr.s
class WOLDLexeme(Lexeme):
    Word_ID = attr.ib(default=None)
    word_source = attr.ib(default=None)
    Borrowed = attr.ib(default=None)
    BorrowedScore = attr.ib(default=None)
    comment_on_borrowed = attr.ib(default=None)
    Analyzability = attr.ib(default=None)
    Simplicity_score = attr.ib(default=None)
    reference = attr.ib(default=None)
    numeric_frequency = attr.ib(default=None)
    age_label = attr.ib(default=None)
    gloss = attr.ib(default=None)
    integration = attr.ib(default=None)
    salience = attr.ib(default=None)
    effect = attr.ib(default=None)
    contact_situation = attr.ib(default=None)
    original_script = attr.ib(default=None)


class Dataset(clld.CLLD):
    __cldf_url__ = (
        "http://cdstar.shh.mpg.de/bitstreams/EAEA0-92F4-126F-089F-0/wold_dataset.cldf.zip"
    )
    dir = Path(__file__).parent
    id = "wold"
    lexeme_class = WOLDLexeme
    
    doc_tokenizers = None

    def tokenizer(self, form, doculect):
        tok_form = '^%s$' % form
        tokens = self.doc_tokenizers[doculect](
            unicodedata.normalize('NFC', tok_form),
            column="IPA")
            
        return tokens.split()
        
    def clean_form(self, form):
        # we cannot use clldutils.text.strip_brackets(), as brackets most
        # of the time contain phonological material
        form = re.sub("\(\d\)", "", form)
        
        # To split with clldutils.text, we'd need a regex pattern, as
        # we need to include the spaces around the tilde...
        form = form.split(",")[0]
        form = form.split(" ~ ")[0]

        return form.strip()

    def cmd_install(self, **kw):
        # Read individual orthographic profiles, extract the corresponding
        # doculect ids (here, glottocodes), and build the appropriate
        # tokenizers
        profile_files = sorted(glob.glob(str(self.dir / "etc" / "*.prof")))
        doculect_codes = [os.path.splitext(os.path.basename(pf))[0] for pf in profile_files]

        self.doc_tokenizers = {
            doculect: Tokenizer(profile=Profile.from_file(pf, form='NFC'),
            errors_replace=lambda c: '<{0}>'.format(c))
            for pf, doculect in zip(profile_files, doculect_codes)
        }

        # Cache the Concepticon IDs
        concepticon = {
            x.attributes["wold_id"]: x.concepticon_id for x in self.conceptlist.concepts.values()
        }

        # cache the field names for CLDF output
        fields = self.lexeme_class.fieldnames()
        
        # Write data to CLDF
        with self.cldf as ds:
            vocab_ids = [v["ID"] for v in self.original_cldf["contributions.csv"]]

            # add sources
            self.add_sources(ds)

            # add languages and build map for choosing the right profile
            lang_map = {}
            for row in self.original_cldf["LanguageTable"]:
                gc, iso = row["Glottocode"], row["ISO639P3code"]
                if gc == "tzot1264":
                    gc, iso = "tzot1259", "tzo"
                if row["ID"] in vocab_ids:
                    ds.add_language(ID=row["ID"], Name=row["Name"], Glottocode=gc, ISO639P3code=iso)

                # Add to map only those which are receivers
                if int(row['ID']) <= 41:
                    lang_map[row['ID']]= gc

            # add parameters
            for row in self.original_cldf["ParameterTable"]:
                ds.add_concept(
                    ID=row["ID"], Name=row.pop("Name"), Concepticon_ID=concepticon.get(row["ID"])
                )

            # Being explicit on what we are adding
            for row in self.original_cldf["FormTable"]:
                if row["Language_ID"] in vocab_ids:
                    # Copy the raw Form to Value, clean form, and tokenize
                    row['Value'] = row['Form']
                    row['Form'] = self.clean_form(row['Form'])
                    row['Segments'] = self.tokenizer(row['Form'],
                            lang_map[row['Language_ID']])
                
                    # Note: We count words marked as "probably borrowed" as loans.
                    row['Loan'] = float(row["BorrowedScore"]) > 0.6
                 
                    ds.add_form_with_segments(**{k: v for k, v in row.items() if k in fields})            

