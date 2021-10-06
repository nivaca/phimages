# phimages

A Python script which checks if the images referred to in a lesson document (.md) actually exist in an images directory, and whether their naming scheme conforms to The Programming Historian (PH) standards.

## Requirements

- [Python](https://www.python.org/) 3.6+
- [Click](https://click.palletsprojects.com) 8.0+

Click is required for the CLI. To install it you can either:

- use PIP: `pip install --user click`
- use your system's package manager (e.g. on Arch Linux you can run: `sudo pacman -S python-click`)

For more details see [here](https://click.palletsprojects.com/en/8.0.x/quickstart/)

## Installation

Simply clone this repo (`git clone https://github.com/nivaca/phimages`) and symlink to your user's bin directory (or to anywhere your PATH variable points to).

You can also [download the script file](https://raw.githubusercontent.com/nivaca/phimages/main/phimages.py) directly from GitHub, as it's a standalone program.


## Usage

To run the script type this in the terminal:

```sh
python3 phimages.py <lessonfile.md> --imgdir <imagesdirectory/>
```

Available options are:

```
  --listimages   Lists all image references in the document and all images in
                 the image directory.
  --version      Displays the script version.
  --checkonly    Only check the files.
  --mkbkp        Backup all files it changes/renames.  [default: True]
  --dryrun       Dry run (do not make any changes).  [default: False]
  --imgdir TEXT  Image directory  [default: img/]
  --help         Show this message and exit.
```

For instance:

```sh
python3 ~/dev/Python/phimages/phimages.py fichas-lectura-cod-imagenes.md --imgdir ~/editions/PH/ph-submissions/images/fichas-zotero --dryrun
```


## Bugs etc.

Please create a GitHub [issue](https://github.com/nivaca/phimages/issues), including the script version. (You can look it up with the `--version` option.)


## Version history

- 0.1 (2021-10-04): first release