# MegaMaid

MegaMaid is a `Site Sucker`. It's primary usefulness is in digital archival. Or bit hoarding. Or whatever
you feel like calling it. It's primary strengths are the ability to apply an arbitrary number of regular
expressions across an arbitrary number of sites.

![Suck! Suck! Suck!](https://github.com/fuzzy/megamaid/blob/main/assets/suck.gif)

Currently it supports HTTP(s) with or with out a proxy. FTP support is planned.

## Usage

```
usage: megamaid.py [-h] [-p RE [RE ...]] [-r] [-tL N] URL [URL ...]

positional arguments:
  URL                   URL(s) to traverse.

options:
  -h, --help            show this help message and exit
  -p RE [RE ...], --pattern RE [RE ...]
                        Specify a pattern to match against links.
  -r, --recursive       Recursively fetch files from the same site.
  -tL N, --trim-lead N  Strip `N` leading components from the output path.
```


## Examples

To mirror all installation ISO and USB IMG media for OpenBSD, across all architectures, one could use a
command like:

```
$ ./megamaid.py -p '.*install[0-9][0-9]\.(iso|img)$' -r https://ftp.usa.openbsd.org/pub/OpenBSD/
```

Let's say you wanted to mirror, FreeBSD, NetBSD, and OpenBSD, and you've got the fastest mirrors for each
system lined up. To handle this in one command, you might do something like:

```
$ ./megamaid.py -p '.*(install[0-9][0-9]|FreeBSD-[0-9].*|NetBSD-[0-9].*)\.(iso|img)$' -r https://ftp.usa.openbsd.org/pub/OpenBSD/ http://ftp.freebsd.org/pub/FreeBSD/releases/ISO-IMAGES/ http://cdn.netbsd.org/pub/NetBSD/
```

You can seperate the patterns out or combine them or do whatever you like, just remember, here be dragons.
`If you have a problem, and you say: "I know! I'll use a regular expression.", you now have two problems.`


To carry the previous example further, let's add some mirroring of the linux kernel source code. Now, I'm
not so much of a crazy person that I want to mirror every release tarball.  The first release tarball of
each series, and all the patches however, that works out for me quite nicely. So let's add that to the command
that we used in our last example:

```
$ ./megamaid.py -p '.*(install[0-9][0-9]|FreeBSD-[0-9].*|NetBSD-[0-9].*)\.(iso|img)$' '^.*(linux-[0-9].*\.0\.tar|patch-[0-9]*\.[0-9]*\.[0-9]*)\.xz$' -r https://ftp.usa.openbsd.org/pub/OpenBSD/ http://ftp.freebsd.org/pub/FreeBSD/releases/ISO-IMAGES/ http://cdn.netbsd.org/pub/NetBSD/ https://ftp.mirrorservice.org/sites/ftp.kernel.org/pub/linux/kernel/
```

Oh no! In examining the results of my mirroring command, I learned that there was a lot of OpenBSD installation
media I was missing! (Dramatization)

So if I want to be more explicit with what I get from the OpenBSD mirror, as well as chop off the leading hostname
directory, I can pull out and modify that pattern:

```sh
./megamaid.py -tL 1 \
 -p '.*(FreeBSD-[0-9].*|NetBSD-[0-9].*)\.(iso|img)$' # FreeBSD and NetBSD install media \
 '^.*(linux-[0-9].*\.0\.tar|patch-[0-9]*\.[0-9]*\.[0-9]*)\.xz$' # Linux kernel source and patches \
 '^.*(install|floppy|inst|kc|cd|cdrom|upgr|upgrade|floppy[A-Z])[0-9][0-9]\.(fs|img|iso)$' # OpenBSD Install media \
 -r https://ftp.usa.openbsd.org/pub/OpenBSD/ \
 http://ftp.freebsd.org/pub/FreeBSD/releases/ISO-IMAGES/ \
 http://cdn.netbsd.org/pub/NetBSD/ \
 https://ftp.mirrorservice.org/sites/ftp.kernel.org/pub/linux/kernel/
```

And there you go, all ready for public consumption and stuff.

## Conclusion

So as you can see, this tool has the ability to combine lots of mirroring jobs into a single manageable....or at
least wrappable tool, that can be fired off from cron jobs as well as manually. It's a **VERY EARLY WIP** but it
is moving quickly.
