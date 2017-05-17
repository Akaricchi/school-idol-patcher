#!/usr/bin/env python3

import subprocess
import tempfile
import pathlib
import logging
import re
import xml.etree.ElementTree as xml


log = logging.getLogger(__name__)


APKTOOL_CMD = ['apktool']
JARSIGNER_CMD = [
    'jarsigner',
    # '-verbose',
    '-sigalg', 'SHA1withRSA',
    '-digestalg', 'SHA1',
]


def patch_root(dirpath):
    stub = """
    .locals 1

    const/4 v0, 0x0

    return v0
"""

    methods = ('isSuBinaryPresent', 'isInappropriateEnvSuspected')
    mexpr = "(?:%s)" % '|'.join(methods)

    log.info("Removing root detection code")

    path = tuple(dirpath.glob('smali/klb/android/*/GameEngineActivity.smali'))[0]
    smali = path.read_text()

    smali = re.sub(
        r'(\.method private %s\(\)Z)(.*?)(\.end method)' % mexpr,
        r'\1%s\3' % stub,
        smali,
        flags=re.DOTALL | re.MULTILINE
    )

    path.write_text(smali)


def patch_permissions(dirpath):
    log.info("Fixing app permissions")

    path = dirpath / 'AndroidManifest.xml'
    tree = xml.parse(str(path))
    root = tree.getroot()

    pkey = '{http://schemas.android.com/apk/res/android}name'
    pval = 'android.permission.WRITE_EXTERNAL_STORAGE'

    for permission in root.findall('./uses-permission'):
        if permission.attrib[pkey] == pval:
            log.info("Permissions look ok, not touching the manifest")
            return

    log.info("Adding missing permission: %s", pval)
    xml.SubElement(root, 'uses-permission', {
        pkey: pval
    })

    tree.write(str(path))


def apply_patches(dirpath):
    patch_root(dirpath)
    patch_permissions(dirpath)


def parse_args(argv):
    import argparse

    p = argparse.ArgumentParser(
        prog=argv[0],
        description='Patch a School Idol Festival APK for use on rooted devices.'
    )

    p.add_argument('input',
        help='path to the original SIF APK',
    )

    p.add_argument('-o', '--out',
        help='path to the resulting rootpatched APK',
        default=None,
        dest='output',
    )

    p.add_argument('-s', '--sign',
        help='sign the APK with jarsigner (required to install it on Android)',
        default=None,
        dest='keyalias',
    )

    p.add_argument('-k', '--keystore',
        help='path to the keystore used to sign the APK',
        default=None,
        dest='keystore',
    )

    return p.parse_args()


def main(argv):
    logging.basicConfig(level=logging.INFO)

    args = parse_args(argv)

    sif_apk = pathlib.Path(args.input).resolve()

    if args.output is None:
        out_apk = sif_apk.with_name(sif_apk.stem + '_rootpatched' + sif_apk.suffix)
    else:
        out_apk = pathlib.Path(args.output).absolute()

    with tempfile.TemporaryDirectory(prefix='sifpatch') as tempdir:
        log.info("Decoding APK %r with apktool", str(sif_apk))
        subprocess.call(APKTOOL_CMD + ['decode', str(sif_apk), '-fo', tempdir])

        log.info("Applying patches")
        apply_patches(pathlib.Path(tempdir).resolve())

        log.info("Rebuilding APK %r with apktool", str(out_apk))
        subprocess.call(APKTOOL_CMD + ['build', tempdir, '-o', str(out_apk)])

        if args.keyalias:
            log.info("Signing the new APK")
            sigcmd = list(JARSIGNER_CMD)

            if args.keystore is not None:
                sigcmd += ['-keystore', args.keystore]

            sigcmd += [str(out_apk)]

            if args.keyalias is not None:
                sigcmd += [args.keyalias]

            subprocess.call(sigcmd)
        else:
            log.warn("You didn't tell me to sign the APK, you won't be able to install it until you sign it yourself")

    log.info("Patching finished. New APK is: %r", str(out_apk))


if __name__ == '__main__':
    import sys
    main(sys.argv)
