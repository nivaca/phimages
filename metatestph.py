#!/usr/bin/env python3
""" Test phimages.py across all PH submissions directories.
 Created by Nicolas Vaughan (nivaca@fastmail.com), 2021. """

import click
import os
import re
import shutil
import sys
import subprocess
from pprint import pprint as pp


chkonly = True

# must end in 'ph-submissions/'
baselocalrepodir = '/home/nivaca/editions/PH/ph-submissions/'
baseimgdir = baselocalrepodir + 'images/'

endict = {
    "lessonsdir": 'en/lessons/',
    "translationsdir": 'en/translations/',
    "lessonslist": [],
    "translationslist": [],
}

esdict = {
    "lessonsdir": 'es/lecciones/',
    "translationsdir": 'es/traducciones/',
    "lessonslist": [],
    "translationslist": [],
    "prunedtranslationslist": [],
    "prunedlessonslist": [],
    "prunedmdlist": [],
}

frdict = {
    "lessonsdir": 'fr/lecons/',
    "translationsdir": 'fr/traductions/',
    "lessonslist": [],
    "translationslist": [],
}

# ptdict = {
#     "les_dir": 'en/lessons/',
#     "tr_dir": 'en/translations/',
# }

imagefiles = []
for i in os.listdir(baseimgdir):
    full = baseimgdir + i
    if re.match(f'^published', i):
        continue
    if os.path.isdir(full):
        imagefiles.append(full)

shortimagefiles = [os.path.basename(i) for i in imagefiles]

endict["lessonslist"] = [i for i in os.listdir(baselocalrepodir + endict["lessonsdir"])]
endict["translationslist"] = [i for i in os.listdir(baselocalrepodir + endict["translationsdir"])]
endict["fullmdlist"] = endict["lessonslist"] + endict["translationslist"]

for i in os.listdir(baselocalrepodir + esdict["lessonsdir"]):
    entry = baselocalrepodir + esdict["lessonsdir"] + i
    esdict["lessonslist"].append(entry)

for i in os.listdir(baselocalrepodir + esdict["translationsdir"]):
    entry = baselocalrepodir + esdict["translationsdir"] + i
    esdict["translationslist"].append(entry)

esdict["fullmdlist"] = esdict["lessonslist"] + esdict["translationslist"]

frdict["lessonslist"] = [i for i in os.listdir(baselocalrepodir + frdict["lessonsdir"])]
frdict["translationslist"] = [i for i in os.listdir(baselocalrepodir + frdict["translationsdir"])]
frdict["fullmdlist"] = frdict["lessonslist"] + frdict["translationslist"]

for mdfile in esdict["lessonslist"]:
    if os.path.splitext(mdfile)[1].lower() != '.md':
        continue
    if os.path.splitext(mdfile)[0].lower() == 'readme':
        continue
    lesson_name = os.path.splitext(os.path.basename(mdfile))[0]  # remove extension
    if lesson_name not in shortimagefiles:
        continue
    esdict["prunedlessonslist"].append(lesson_name)

for mdfile in esdict["translationslist"]:
    if os.path.splitext(mdfile)[1].lower() != '.md':
        continue
    if os.path.splitext(mdfile)[0].lower() == 'readme':
        continue
    lesson_name = os.path.splitext(os.path.basename(mdfile))[0]  # remove extension
    if lesson_name not in shortimagefiles:
        continue
    esdict["prunedtranslationslist"].append(lesson_name)


esdict["prunedmdlist"] = esdict["prunedlessonslist"] + esdict["prunedtranslationslist"]

if chkonly:
    chkonlyopt = '--checkonly'
else:
    chkonlyopt = '--chkonly False'

for entry in esdict["prunedmdlist"]:
    mdfn = baselocalrepodir + esdict["lessonsdir"] + entry + '.md'
    msg = f"Processing ‘{entry}.md’"
    msglen = len(msg)
    print()
    print(msglen * '*')
    print(f"{msg}")
    print(msglen * '*')
    cmd = ['python3',
           'phimages.py',
           mdfn,
           '--imgdir',
           baseimgdir + entry + '/',
           chkonlyopt,
           ]
    output = subprocess.run(cmd)
    # pp(output)
    if "n" in input("\nContinue? (Y/n) ").lower():
        sys.exit(0)
