#!/usr/bin/env python3
""" Renames images and reformats .md according to PH requirements.
 Created by Nicolas Vaughan (nivaca@fastmail.com), 2021. """
import os
import re
import shutil
import sys
import click

# Global variables
Makebackup = True
Dryrun = False
Imgdir = "img/"
Extensions: list[str] = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
Inputfile = ""


def get_names_from_dir() -> list:
    listing = os.listdir(Imgdir)
    real_list = []
    if not listing:
        print(f"Error. Empty images dir {Imgdir}. Aborting.")
        sys.exit(1)
    for file in listing:
        file_name, file_extension = os.path.splitext(file)
        if file_extension in Extensions:
            real_list.append(file)
    return real_list


def parsefile() -> list:
    """ Reads the .md file and extracts all image file names.
    We will assume that an image appears at most once in the md. """
    with open(Inputfile, "r", encoding="utf-8") as f:
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
                print(f"!Error: {fn} is already found in {Inputfile}\n"
                      f"  If the image needs to appear more than once,\n"
                      f"  please rename each new occurrance both in the document\n"
                      f"  and in {Imgdir}.")
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
            print(f"Warning: File {f} in {Imgdir} is not referenced in {Inputfile}. Ignoring.")
    return identical


def compare_lists_md_to_real(real_list: list, md_list: list) -> bool:
    identical = True
    for f in md_list:
        if f not in real_list:
            identical = False
            print(f"Error: Entry for {f} in {Inputfile} has no corresponding file in {Imgdir}")
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
    if Makebackup:
        try:
            shutil.copyfile(fn, f"{fn}.bak")
        except OSError:
            print(f"Error: Could not backup {fn}")


def change_names(md_list: list, lesson_name: str) -> bool:
    if not Dryrun:
        if Makebackup:
            createbackup(Inputfile)
        with open(Inputfile, "r", encoding="utf-8") as f:
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
            if not Dryrun:
                rename_file(full_file_name, new_fn)

        if not Dryrun:
            with open(Inputfile, "w", encoding="utf-8") as f:
                try:
                    f.writelines(lines)
                    return True
                except IOError:
                    print("!Error: could not write new file.")
                    sys.exit(1)


def rename_file(old_name: str, new_name: str):
    if Makebackup:
        createbackup(Imgdir + old_name)
    try:
        os.rename(Imgdir + old_name, Imgdir + new_name)
    except IOError:
        print(f"!Error: could not rename {old_name}.")
        sys.exit(1)


@click.command()
@click.option('--mkbkp', default=True, flag_value=True, help='Backup all files it changes/renames.', show_default=True)
@click.option('--dryrun', default=False, flag_value=True, help='Dry run (do not make any changes).', show_default=True)
@click.option('--imgdir', default=Imgdir, help='Image directory', show_default=True)
@click.argument('inputfile', type=click.Path(exists=True))
def main(inputfile: str, imgdir: str, dryrun: bool, mkbkp: bool):
    mdfn, mdfn_ext = os.path.splitext(inputfile)
    if mdfn_ext.lower() != 'md':
        click.secho(f'Error: input file ({inputfile}) must have ".md" extension.', fg='red')
        sys.exit(0)
    else:
        global Inputfile
        Inputfile = inputfile

    global Makebackup
    if not mkbkp:
        Makebackup = False

    global Imgdir
    Imgdir = imgdir

    global Dryrun
    if dryrun:
        Dryrun = True

    # we take the lesson's name from the lesson's base file
    lesson_name = os.path.splitext(Inputfile)[0]

    real_list = get_names_from_dir()

    # this dict contains both filename and the list of line no.
    # of the file names in the md
    md_list = parsefile()

    if Dryrun:
        print("Dry run: no files would be changed")

    if compare_lists(real_list, md_list):
        change_names(md_list, lesson_name)


if __name__ == "__main__":
    main()
