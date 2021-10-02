#!/usr/bin/env python3
""" Renames images and reformats .md according to PH requirements.
 Created by Nicolas Vaughan (nivaca@fastmail.com), 2021. """
import os
import re
import shutil
import sys
import click

# global variables
makebackup = True
dryrun = False
imgdir = "img/"
extensions: list[str] = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
inputfile = ""


def get_names_from_dir() -> list:
    listing = os.listdir(imgdir)
    real_list = []
    if not listing:
        print(f"Error. Empty images dir {imgdir}. Aborting.")
        sys.exit(1)
    for file in listing:
        file_name, file_extension = os.path.splitext(file)
        if file_extension in extensions:
            real_list.append(file)
    return real_list


def parsefile() -> list:
    """ Reads the .md file and extracts all image file names.
    We will assume that an image appears at most once in the md. """
    with open(inputfile, "r", encoding="utf-8") as f:
        lines = f.readlines()
    md_list = []  # list of list of filenames and line numbers in md file
    pattern = r"""figure.html +filename=['"](.+?)['"]"""

    cpattern = re.compile(pattern)
    ln = 1
    for line in lines:
        match = re.search(cpattern, line)
        if match:
            # fn is the matched filename
            fn = match.group(1).strip()

            if fn in [i[0] for i in md_list]:
                print(f"!Error: {fn} is already found in {inputfile}\n"
                      f"  If the image needs to appear more than once,\n"
                      f"  please rename each new occurrance both in the document\n"
                      f"  and in {imgdir}.")
                sys.exit(1)

            # we append a list of file name and line number
            md_list.append([fn, str(ln)])
        ln += 1
    return md_list


def compare_lists_real_to_md(real_list: list, md_list: list) -> bool:
    identical = True
    for f in real_list:
        if f not in md_list:
            identical = False
            print(f"Warning: File {f} in {imgdir} is not referenced in {inputfile}. Ignoring.")
    return identical


def compare_lists_md_to_real(real_list: list, md_list: list) -> bool:
    identical = True
    for f in md_list:
        if f not in real_list:
            identical = False
            print(f"Error: Entry for {f} in {inputfile} has no corresponding file in {imgdir}")
    return identical


def compare_lists(real_list: list, full_md_list: list):
    md_list = [i[0] for i in full_md_list]
    if not compare_lists_md_to_real(real_list, md_list):
        print("Aborting")
        sys.exit(1)
    elif not compare_lists_real_to_md(real_list, md_list):
        ans = input("Continue? [Y/n] ").lower()
        if ans not in ["y", ""]:
            sys.exit(0)
        return True
    else:
        return True


def createbackup(fn: str):
    if makebackup:
        try:
            shutil.copyfile(fn, f"{fn}.bak")
        except OSError:
            print(f"Error: Could not backup {fn}")


def change_names(md_list: list, lesson_name: str) -> bool:
    if not dryrun:
        if makebackup:
            createbackup(inputfile)
        with open(inputfile, "r", encoding="utf-8") as f:
            lines = f.readlines()

        image_count = len(md_list)
        for i in range(image_count):
            full_file_name, ln = md_list[i]
            fn, fn_ext = os.path.splitext(full_file_name)
            # format: lesson-name01.ext, lesson-name02.ext, etc.
            new_fn = lesson_name + str(i + 1).zfill(2) + fn_ext
            lineno = int(ln) - 1  # adjust for 0-index
            oldline = lines[lineno]
            newline = re.sub(rf"{full_file_name}", rf"{new_fn}", oldline)
            lines[lineno] = newline  # change that line in the list
            print(f"{full_file_name} => {new_fn}")
            # perform file rename in img dir
            if not dryrun:
                rename_file(full_file_name, new_fn, imgdir)

        if not dryrun:
            with open(inputfile, "w", encoding="utf-8") as f:
                try:
                    f.writelines(lines)
                    return True
                except IOError:
                    print("!Error: could not write new file.")
                    sys.exit(1)


def rename_file(old_name: str, new_name: str):
    if makebackup:
        createbackup(imgdir + old_name)
    try:
        os.rename(imgdir + old_name, imgdir + new_name)
    except IOError:
        print(f"!Error: could not rename {old_name}.")
        sys.exit(1)


@click.command()
@click.option('--mkbkp', default=True, flag_value=True, help='Backup all files it changes/renames.', show_default=True)
@click.option('--dry', default=False, flag_value=True, help='Dry run (do not make any changes).', show_default=True)
@click.option('--images', default=imgdir, help='Image directory', show_default=True)
@click.argument('mdfile', type=click.Path(exists=True))
def main(mdfile: str, images: str, dry: bool, mkbpk: bool):
    mdfn, mdfn_ext = os.path.splitext(mdfile)
    if mdfn_ext.lower() != 'md':
        click.secho(f'!Error: {mdfile} must have ".md" extension.', fg='red')
        sys.exit(0)


    # we take the lesson's name from the lesson's base file
    lesson_name = os.path.splitext(inputfile)[0]

    real_list = get_names_from_dir(imgdir)

    # this dict contains both filename and the list of line no.
    # of the file names in the md
    md_list = parsefile(inputfile, imgdir, inputfile)

    if dry:
        print("Dry run: no files would be changed")

    if compare_lists(real_list, md_list, imgdir, inputfile):
        change_names(md_list, lesson_name, imgdir, inputfile)


if __name__ == "__main__":
    main()
