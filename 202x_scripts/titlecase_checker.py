import csv
import codecs
import shutil
import warnings
from tempfile import NamedTemporaryFile


# Patch showwarning to hide superfluous source lines
def _showwarning(message, _category, _filename, _lineno, _file=None, _line=None):
    print(message)
warnings.showwarning = _showwarning


def smart_titlecase(full_title):
    '''Title-case converter that tries to be "smart" by not overriding user-given capitalisation. This means
       that characters can only be promoted to capitals, never demoted, which preserves acronyms etc. 
       Existing titlecase is kept and sentence case is converted to title case. Only fully uppercase input 
       potentially causes unwanted lowercasing of non-initials, therefore these cases are flagged. 
       Titlecasing roughly follows NYT rules (because there are many competing rules and this one seemed to
       be the easiest to implement: https://titlecaseconverter.com/rules/). An exact implementation of these
       rules would require automatic part-of-speech analysis, which is not included. Instead potentially 
       ambiguous cases are flagged for manual inspection.'''
    if full_title.isupper():
        titlecase = smart_titlecase(full_title.title())
        warnings.warn(f'Check automatically converted title "{titlecase}"'
                       ' for accidental lowercasing of acronyms etc.')
        return titlecase
    def upper_initial(string):
        '''Uppercase initial but leave other characters unchanged to preserve acronyms etc.'''
        # If rest of string is all uppercase, trust that capitalisation is correct, e.g. fMRI, iOS
        if string[1:].isupper():
            return string
        return string[0].upper()+string[1:]
    def word_titlecase(word, first_or_last=False):
        try:
            EXCEPTIONS = ('iPhone',)
            idx = [s.lower() for s in EXCEPTIONS].index(word.lower())
            return EXCEPTIONS[idx]
        except ValueError:
            pass
        ALWAYS = ('an', 'and', 'as', 'at', 'but', 'if', 'of', 'or', 'the', 'vs')
        if word.lower() in ALWAYS and not first_or_last:
            return word.lower()
        POS_DEPENDENT = ('a', 'by', 'en', 'for', 'in', 'on', 'to', 'v', 'via')
        if word.lower() in POS_DEPENDENT and not first_or_last:
            if word.islower():
                warnings.warn(f'Verify that "{word}" is an article or preposition in "{full_title}", otherwise manually capitalise it')
            else:
                warnings.warn(f'Verify that "{word}" is an adverb or verb in "{full_title}", otherwise manually lowercase it')
            return word
        if '-' not in word:
            return upper_initial(word)
        compounds = word.split('-')
        # In hyphenated compounds, do not capitalize the second part if it follows a prefix of two or three
        # letters and if the hyphen separates doubled vowels (e.g., “Co-operation”). Otherwise, capitalize
        #  the second part (e.g., “Co-Author”). https://titlecaseconverter.com/rules/
        if len(compounds) == 2:
            if not (
                len(compounds[0]) in (2, 3)
                and compounds[0][-1] in ('a', 'e', 'i', 'o', 'u')
                and compounds[0][-1] == compounds[1][0]
            ):
                compounds[1] = upper_initial(compounds[1])
            return '-'.join([upper_initial(compounds[0]), compounds[1]])
        return '-'.join([word_titlecase(compound) for compound in compounds])
    words = full_title.split()
    bookends = [False] * len(words)
    bookends[0] = bookends[-1] = True
    try:
        colon_flags = [w.endswith(':') for w in words]
        for idx, colon in enumerate(colon_flags):
            if colon:
                bookends[idx:idx+2] = [True] * 2
    except ValueError:
        pass
    try:
        dash_flags = [w.startswith('-') for w in words]
        for idx, dash in enumerate(dash_flags):
            if dash:
                bookends[idx-1:idx+2] = [True] * 3
    except ValueError:
        pass
    return ' '.join([word_titlecase(word, bookend) for word, bookend in zip(words, bookends)])


def get_csv_encoding(csv_path):
    # If you used excel to convert the data file to csv, it'll have a UTF-8 BOM at the beginning of the file
    # check if it's there:
    BUFSIZE = 1024
    with open(csv_path, "rb") as fp:
        chunk = fp.read(BUFSIZE)
        if chunk.startswith(codecs.BOM_UTF8):
            encoding = "utf-8-sig"
        else:
            encoding = "utf-8"
    return encoding


def convert_csv_file(csv_path):
    # process .csv of paper data and match it to file locations on disk
    encoding = get_csv_encoding(csv_path)
    temp_file = NamedTemporaryFile(mode='w', delete=False, encoding=encoding)
    with open(csv_path, 'r', encoding=encoding) as fp:
        reader = csv.DictReader(fp)
        field_names = reader.fieldnames
        if "TitleChecked" not in field_names:
            field_names.append("TitleChecked")
        writer = csv.DictWriter(temp_file, fieldnames=field_names)
        writer.writeheader()
        for row in reader:
            if not row.get("TitleChecked", ""):
                row["Title"] = smart_titlecase(row["Title"].strip())
            row["Abstract"] = row["Abstract"].strip()
            row["OneLiner"] = row["OneLiner"].strip()
            row["AuthorNames"] = row["AuthorNames"].strip()
            row["AuthorEmails"] = row["AuthorEmails"].strip()
            row["AuthorDetails"] = row["AuthorDetails"].strip()
            writer.writerow(row)

    shutil.move(temp_file.name, csv_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Convert paper titles to New York Times titlecase")
    parser.add_argument("--csv", help="path to csv file with metadata", default='../202x_Proceedings_ISMIR/cmt-metadata.csv')

    args = parser.parse_args()
    convert_csv_file(args.csv)
