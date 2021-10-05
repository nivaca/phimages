#!/usr/bin/env python3
""" Renames images and reformats .md according to PH requirements.
 Created by Nicolas Vaughan (nivaca@fastmail.com), 2021. """
import click
import os
import re
import shutil
import sys

VERSION = "0.1 (2021-10-04)"


def get_names_from_dir(params: dict) -> list:
    listing = os.listdir(params["imgdir"])
    real_list = []
    if not listing:
        click.secho(f'Error. Empty images dir {params["imgdir"]}. Aborting.', fg='red')
        sys.exit(1)
    for file in listing:
        file_name, file_extension = os.path.splitext(file)
        if file_extension in params["extensions"]:
            real_list.append(file)
    return real_list


def detect_image_inclusion_pattern(params: dict, lines: list) -> str:
    possible_patterns = [r"""{% include figure.html +filename=['"](.+?)['"]""",
                         r"""<img .*?src=['"](.+?)['"]"""]
    plist = []
    for pattern in possible_patterns:
        cpattern = re.compile(pattern)
        for line in lines:
            match = re.search(cpattern, line)
            if match and pattern not in plist:
                plist.append(pattern)

    count = len(plist)
    if count == 0:
        click.secho(f'Error: No image references found in {params["baseinputfile"]}\n'
                    f'Nothing to do here.', fg='red')
        sys.exit(1)
    elif count > 1:
        click.secho(f'Error: Found more than one image reference pattern in '
                    f'{(params["baseinputfile"])}:', fg='red')
        for pat in plist:
            click.secho(f"    {pat}", fg='red')
        click.secho(f'You must choose only *one* of these patterns, '
                    f'although the recommended one in PH is:', fg='red')
        click.secho("""  {% include figure.html filename="<image-filename.ext>" """
                    """caption="<image caption>" %}""", fg='red')
        sys.exit(1)
    else:
        return plist[0]


def parsefile(params: dict) -> list:
    """ Reads the .md file and extracts all image file names.
    We will assume that an image appears at most once in the md. """
    with open(params["inputfile"], "r", encoding="utf-8") as f:
        lines = f.readlines()

    pattern = detect_image_inclusion_pattern(params, lines)

    md_list = []  # list of list of filenames and line numbers in md file
    # pattern = r"""figure.html +filename=['"](.+?)['"]"""

    cpattern = re.compile(pattern)
    ln = 1
    for line in lines:
        match = re.search(cpattern, line)
        if match:
            # fn is the matched filename
            fn = match.group(1).strip()

            # ignore urls
            if re.search(r"https?:", fn):
                continue

            if fn in [i[0] for i in md_list]:
                click.secho(f'Error: {fn} is already found in {params["baseinputfile"]}\n'
                            f'If the image needs to appear more than once,\n'
                            f'please rename each new occurrance both in the document\n'
                            f'and in {params["imgdir"]}.', fg='red')
                sys.exit(1)

            # we append a list of file name and line number
            md_list.append([fn, str(ln)])
        ln += 1
    if len(md_list) == 0:
        click.secho(f'Error: No image references found in {params["baseinputfile"]}\n'
                    f'Nothing to do here.', fg='red')
        sys.exit(1)
    return md_list


def compare_lists_real_to_md(params: dict) -> bool:
    identical = True
    for f in params["real_list"]:
        if f not in params["md_list"]:
            identical = False
            click.secho(f'Warning: File {f} in {params["imgdir"]} is not referenced '
                        f'in {params["baseinputfile"]}.\n'
                        f'  It will be ignored, but you should delete it '
                        f'if it is not really needed.', fg='yellow')
    return identical


def compare_lists_md_to_real(params: dict) -> bool:
    identical = True
    for f in params["md_list"]:
        if f not in params["real_list"]:
            identical = False
            click.secho(f'Error: Reference in {params["baseinputfile"]} for {f} '
                        f'has no corresponding file in images directory.', fg='red')
    return identical


def compare_lists(params: dict):
    if not compare_lists_md_to_real(params):
        click.secho("Aborting", fg='red')
        sys.exit(1)
    elif not compare_lists_real_to_md(params):
        ans = input("Continue? [Y/n] ").lower()
        if ans not in ["y", ""]:
            sys.exit(0)
        return True
    else:
        return True


def createbackup(fname: str) -> bool:
    try:
        shutil.copyfile(fname, f"{fname}.bak")
        return True
    except OSError:
        click.secho(f"Error: Could not backup {fname}", fg='red')
        return False


def change_names(params: dict) -> bool:
    if not params["dryrun"]:
        if params["mkbkp"]:
            createbackup(params["inputfile"])
        with open(params["inputfile"], "r", encoding="utf-8") as f:
            lines = f.readlines()

        image_count = len(params["full_md_list"])
        for i in range(image_count):
            full_fname, ln = params["full_md_list"][i]
            fn, fn_ext = os.path.splitext(full_fname)
            # format: lesson-name01.ext, lesson-name02.ext, etc.
            new_fname = params["lesson_name"] + str(i + 1).zfill(2) + fn_ext
            lineno = int(ln) - 1  # adjust for 0-index
            oldline = lines[lineno]
            newline = re.sub(rf"{full_fname}", rf"{new_fname}", oldline)
            lines[lineno] = newline  # change that line in the list
            click.secho(f"{full_fname} => {new_fname}", fg='blue')
            # perform file rename in img dir
            if not params["dryrun"]:
                rename_file(full_fname, new_fname, params)

        if not params["dryrun"]:
            with open(params["inputfile"], "w", encoding="utf-8") as f:
                try:
                    f.writelines(lines)
                    return True
                except IOError:
                    click.secho("!Error: could not write new file.", fg='red')
                    sys.exit(1)


def rename_file(old_fname: str, new_fname: str, params: dict):
    if params["mkbkp"]:
        createbackup(params["imgdir"] + old_fname)
    try:
        os.rename(params["imgdir"] + old_fname, params["imgdir"] + new_fname)
    except IOError:
        click.secho(f"Error: could not rename {old_fname}.", fg='red')
        sys.exit(1)


def perform_tests(params: dict) -> bool:
    rescomp = compare_lists(params)
    if params["checkonly"]:
        return rescomp and check_names(params)
    else:
        # we don't need to check names only when renaming etc.
        return rescomp


def check_names(params: dict) -> bool:
    pattern = params["lesson_name"] + r"\d{1,3}\.\w{3,4}"
    result = True
    errors = 0
    # format: lesson-name01.ext, lesson-name02.ext, etc.
    for fn in params["md_list"]:
        if not re.match(pattern, fn):
            egfname = params["lesson_name"] + "03.png"
            click.secho(f"Error: {fn} does not comply with pattern required (e.g. {egfname})",
                        fg='red')
            errors += 1
            result = False
    if not result:
        if errors > 1:
            err_noun = "errors"
        else:
            err_noun = "error"
        click.secho(f"{errors} {err_noun} found in file naming pattern.", fg='red')
    return result


def list_images(params: dict):
    params["md_list"].sort()
    images = params["md_list"]
    count = len(images)
    if count > 1:
        nounending = "s"
    else:
        nounending = ""
    click.secho(f'{count} image reference{nounending} found in {params["baseinputfile"]}:', fg='blue')
    for i in images:
        print(f'  {os.path.basename(i)}')

    params["real_list"].sort()
    images = params["real_list"]
    count = len(images)
    if count > 1:
        nounending = "s"
    else:
        nounending = ""
    click.secho(f'{count} image{nounending} found in {params["imgdir"]}:', fg='blue')
    for i in params["real_list"]:
        print(f'  {os.path.basename(i)}')


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +                               main()                               +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@click.command()
@click.option('--listimgs', default=False, flag_value=True,
              help='Lists all image references in the document and in the image directory.', show_default=True)
@click.option('--version', default=False, flag_value=True, help='Displays the script version.', show_default=False)
@click.option('--checkonly', default=False, flag_value=True, help='Only check the files.', show_default=True)
@click.option('--mkbkp', default=True, flag_value=True, help='Backup all files it changes/renames.', show_default=True)
@click.option('--dryrun', default=False, flag_value=True, help='Dry run (do not make any changes).', show_default=True)
@click.option('--imgdir', default='img/', help='Image directory', show_default=True)
# @click.argument('inputfile', type=click.Path(exists=True))
@click.argument('inputfile', default='')
def main(inputfile: str, imgdir: str, dryrun: bool, mkbkp: bool, checkonly: bool, version: bool, listimgs: bool):
    if version:
        click.secho(f"phimages.ph version {VERSION}.\n"
                    f"Created by Nicolas Vaughan (https://github.com/nivaca),\n"
                    f"under a CC BY-NC-SA 4.0 license.\n"
                    f"See https://creativecommons.org/licenses/by-nc-sa/4.0/", fg='blue')
        sys.exit(0)

    if not inputfile:
        click.secho(f"Usage: phimages.py [OPTIONS] INPUTFILE\n"
                    f"Try 'phimages.py --help' for help.", fg='blue')
        click.secho(f"Error: Missing argument 'INPUTFILE'.", fg='red')
        sys.exit(1)

    mdfn, mdfn_ext = os.path.splitext(inputfile)
    if mdfn_ext.lower() != '.md':
        click.secho(f'Error: input file ({inputfile}) must have ".md" extension.', fg='red')
        sys.exit(0)

    params = {
        "inputfile": inputfile,
        "baseinputfile": os.path.basename(inputfile),
        "lesson_name": os.path.splitext(inputfile)[0],
        "extensions": ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif'],
        "imgdir": imgdir,
        "checkonly": checkonly,
        "dryrun": dryrun,
        "mkbkp": mkbkp,
    }

    if dryrun:
        click.secho("Dry run: no files will be changed", fg='blue')

    if checkonly:
        click.secho("Performing tests only.", fg='blue')

    params["real_list"] = get_names_from_dir(params)

    # this dict contains both filename and the list of line no.
    # of the file names in the md
    params["full_md_list"] = parsefile(params)
    params["md_list"] = [i[0] for i in params["full_md_list"]]

    if listimgs:
        list_images(params)
        sys.exit(0)

    if perform_tests(params):
        click.secho(f"Image files in {imgdir} and image links in {inputfile} seem to match.", fg="blue")
        if not checkonly:
            change_names(params)


if __name__ == "__main__":
    main()
