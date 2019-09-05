import attr
import glob
from clldutils.path import Path
from pylexibank.dataset import Lexeme
from pylexibank.providers import clld
import os.path

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
                    row['Segments'] = self.tokenizer(row['Form'],
                            lang_map[row['Language_ID']])
                
                    # Note: We count words marked as "probably borrowed" as loans.
                    row['Loan'] = float(row["BorrowedScore"]) > 0.6
                    
                    ds.add_form_with_segments(**{k: v for k, v in row.items() if k in fields})            
                
                    a = """
                
                    ds.add_form_with_segments(
                        Language_ID=row['Language_ID'],
                        Parameter_ID=row['Parameter_ID'],
                        Value=row['Form'],
                        Form=row['Form'],
                        Segments=self.tokenizer(row['Form'],
                            lang_map[row['Language_ID']]),
                        Source=row['Source'],
                        # Note: We count words marked as "probably borrowed" as loans.
                        Loan = float(row["BorrowedScore"]) > 0.6,
                        Word_ID = row['Word_ID'],
                        word_source = row['word_source'],
                        Borrowed = row['Borrowed'],
                        BorrowedScore = row['BorrowedScore'],
                        comment_on_borrowed = row['comment_on_borrowed'],
                        Analyzability = row['Analyzability'],
                        #Simplicity_score = row['Simplicity_score'],
                        reference = row['reference'],
                        numeric_frequency = row['numeric_frequency'],
                        age_label = row['age_label'],
                        gloss = row['gloss'],
                        integration = row['integration'],
                        salience = row['salience'],
                        effect = row['effect'],
                        #contact_situation = row['contact_situation'],
                        original_script = row['original_script'],
                    )

                 #   row["Value"] = row["Form"]
                 #   row['Form'] = None
                   #row["Segments"] = self.tokenizer(None, row['Value'],
                    #        column="IPA")

                #    ds.add_form_with_segments(**{k: v for k, v in row.items()})
                """
