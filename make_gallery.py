import sys
import os
import shutil
from PIL import Image


GITHUB_USERNAME = "wdsrocha"
GITHUB_REPOSITORY = "wallpapers"


def parse_path(file_path):
    # TODO: handle spaces, parenthesis, unicode, etc. Example of filename that
    # causes headache: "James Ball & INK Studio - IBM 729 (2560 × 1440)"
    return file_path


def progressbar(it, prefix="", size=60, file=sys.stdout):
    """https://stackoverflow.com/a/34482761/7651928"""
    count = len(it)

    def show(j):
        x = int((size * j) / count)
        file.write(f"{prefix}[{'#' * x}{'.' * (size-x)}] {j}/{count}\r")
        file.flush()

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")


def get_all_file_paths(top_dirname):
    # TODO: refactor to get only image paths
    file_paths = []
    for dirname, _, filenames in os.walk(top_dirname):
        for filename in filenames:
            file_path = os.path.join(dirname, filename)
            file_paths.append(file_path)
    return file_paths


def make_thumbnails_dir(thumbnails_dirname):
    shutil.rmtree(thumbnails_dirname, ignore_errors=True)
    os.makedirs(thumbnails_dirname)


def to_thumbnail_filename(filename):
    return f"thumbnail_{parse_path(filename)}"


def to_thumbnail(image_path, thumbnail_dirname, thumbnail_size):
    filename = os.path.basename(image_path)
    thumbnail_filename = to_thumbnail_filename(filename)
    thumbnail_path = os.path.join(thumbnail_dirname, thumbnail_filename)
    im = Image.open(image_path)
    im.thumbnail(thumbnail_size, Image.ANTIALIAS)
    im.save(thumbnail_path)


def convert_images_to_thumbnail(image_paths, thumbnails_dirname,
                                thumbnail_size, file=sys.stdout):
    file.write("Converting images to thumbnail...\n")
    for image_path in progressbar(image_paths):
        to_thumbnail(image_path, thumbnails_dirname, thumbnail_size)


def setup_thumbnails_dir(image_paths, thumbnails_dirname, thumbnail_size):
    # TODO: if dir already exists, ask if user wants to proceed or cancel
    make_thumbnails_dir(thumbnails_dirname)
    convert_images_to_thumbnail(image_paths, thumbnails_dirname,
                                thumbnail_size)


def get_overwrite_warning(md_header_path):
    return (
        "[comment]: # (###################################################)\n"
        "[comment]: # (### WARNING:  Do not edit this file, changes will)\n"
        "[comment]: # (### be overwritten by make_gallery.py!)\n"
        "[comment]: # (### Make changes to)\n"
        f"[comment]: # (###     {md_header_path})\n"
        "[comment]: # (### instead.)\n"
        "[comment]: # (###################################################)\n")


def to_md_section(section_name):
    return f"## {section_name}\n"


def get_raw_image_url(image_path):
    image_path = parse_path(image_path)
    return (
        "https://raw.githubusercontent.com/"
        f"{GITHUB_USERNAME}/{GITHUB_REPOSITORY}/master/{image_path}")


def make_md_gallery(md_header_path, md_file_path, image_paths,
                    thumbnails_dirname):
    md_file = open(md_file_path, "w")
    md_file.write(get_overwrite_warning(md_header_path))
    md_file.write("\n")
    with open(md_header_path, "r") as md_header:
        md_file.write(md_header.read())
    last_image_dirname = str()
    for image_path in image_paths:
        image_dirname, filename = os.path.split(image_path)
        if image_dirname != last_image_dirname:
            md_file.write("\n")
            md_file.write(to_md_section(image_dirname))
            md_file.write("\n")
            last_image_dirname = image_dirname
        thumbnail_path = os.path.join(
            thumbnails_dirname,
            to_thumbnail_filename(filename))
        raw_image_url = get_raw_image_url(image_path)
        md_file.write("[![{}]({})]({})\n".format(
            thumbnail_path, thumbnail_path, raw_image_url))
    md_file.close()


if __name__ == "__main__":
    # TODO: add argparse
    wallpapers_dirname = "wallpapers"
    thumbnails_dirname = "thumbnails"
    thumbnail_size = (128, 128)
    readme_header_path = "readme_header.md"
    readme_path = "README.md"

    image_paths = get_all_file_paths(wallpapers_dirname)
    setup_thumbnails_dir(image_paths, thumbnails_dirname, thumbnail_size)
    # TODO: add option to update readme without having to process whole
    # thumbnails setup again
    make_md_gallery(readme_header_path, readme_path, image_paths,
                    thumbnails_dirname)
