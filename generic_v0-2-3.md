# bioimage.io generic specification
Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
Note that those resources are described with a type-specific RDF.
Use this generic resource description, if none of the known specific types matches your resource.

**General notes on this documentation:**
| symbol | explanation |
| --- | --- |
| `field`<sub>type hint</sub> | A fields's <sub>expected type</sub> may be shortened. If so, the abbreviated or full type is displayed below the field's description and can expanded to view further (nested) details if available. |
| Union[A, B, ...] | indicates that a field value may be of type A or B, etc.|
| Literal[a, b, ...] | indicates that a field value must be the specific value a or b, etc.|
| Type* := Type (restrictions) | A field Type* followed by an asterisk indicates that annotations, e.g. value restriction apply. These are listed in parentheses in the expanded type description. They are not always intuitively understandable and merely a hint at more complex validation.|
| \<type\>.v\<major\>_\<minor\>.\<sub spec\> | Subparts of a spec might be taken from another spec type or format version. |
| `field` ≝ `default` | Default field values are indicated after '=' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class.|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
| ∈📦  | Files referenced in fields which are marked with '∈📦 ' are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included well as 'rdf.yaml'. |

## `type`<sub> str</sub>
The resource type assigns a broad category to the resource.



## `format_version`<sub> Literal[0.2.3]</sub> ≝ `0.2.3`
The format version of this resource specification
(not the `version` of the resource description)
When creating a new resource always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



## `description`<sub> str</sub>




## `name`<sub> str</sub>
A human-friendly name of the resource description



## `attachments`<sub> Optional[Attachments]</sub> ≝ `None`
file and other attachments

<details><summary>Optional[Attachments]

</summary>


**Attachments:**
### `attachments.files`<sub> Sequence</sub> ≝ `()`
∈📦 File attachments


Sequence[Union[Url (max_length=2083 allowed_schemes=['http', 'https']), RelativeFilePath]]

</details>

## `authors`<sub> Sequence[Author]</sub> ≝ `()`
The authors are the creators of the RDF and the primary points of contact.

<details><summary>Sequence[Author]

</summary>


**Author:**
### `authors.i.name`<sub> str</sub>
Full name



### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`
GitHub user name



### `authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[str (AfterValidator(validate_orcid_id))]

</details>

## `badges`<sub> Sequence[Badge]</sub> ≝ `()`
badges associated with this resource

<details><summary>Sequence[Badge]

</summary>


**Badge:**
### `badges.i.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#badgesilabel) 'Open in Colab'



### `badges.i.icon`<sub> Optional</sub> ≝ `None`
badge icon
[*Example:*](#badgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'


Optional[Url (max_length=2083 allowed_schemes=['http', 'https'])]

### `badges.i.url`<sub> Url</sub>
target URL
[*Example:*](#badgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

## `cite`<sub> Sequence[CiteEntry]</sub> ≝ `()`
citations

<details><summary>Sequence[CiteEntry]

</summary>


**CiteEntry:**
### `cite.i.text`<sub> str</sub>
free text description



### `cite.i.doi`<sub> Optional</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)

<details><summary>Optional[str*]

</summary>

Optional[str
(StringConstraints(strip_whitespace=None, to_upper=None, to_lower=None, strict=None, min_length=None, max_length=None, pattern='^10\\.[0-9]{4}.+$'))]

</details>

### `cite.i.url`<sub> Optional[str]</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

## `config`<sub> _internal.base_nodes.ConfigNode</sub> ≝ ``
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a github repo URL in `config` since we already have the
`git_repo` field defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    bioimage_io:  # here is the domain name
        my_custom_key: 3837283
        another_key:
            nested: value
    imagej:       # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource
(packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files)
[*Example:*](#config) {'bioimage_io': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `()`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) 'cover.png'

<details><summary>Sequence[Union[Url*, RelativeFilePath]*]

</summary>

Sequence of Union[Url (max_length=2083 allowed_schemes=['http', 'https']), RelativeFilePath]
(WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False))

</details>

## `documentation`<sub> Union</sub> ≝ `None`
∈📦 URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md', '…']


Union[Url (max_length=2083 allowed_schemes=['http', 'https']), RelativeFilePath, None]

## `download_url`<sub> Optional</sub> ≝ `None`
URL to download the resource from (deprecated)


Optional[Url (max_length=2083 allowed_schemes=['http', 'https'])]

## `git_repo`<sub> Optional[str]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration

<details><summary>Union[Url*, RelativeFilePath, str*, None]

</summary>

Union of
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- RelativeFilePath
- str (Len(min_length=1, max_length=2))
- None


</details>

## `id`<sub> Optional[str]</sub> ≝ `None`
bioimage.io wide, unique identifier assigned by the [bioimage.io collection](https://github.com/bioimage-io/collection-bioimage-io)



## `license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#license) ['MIT', 'CC-BY-4.0', 'BSD-2-Clause']

<details><summary>Union[Literal[0BSD, ..., ZPL-2.1], Literal[AGPL-1.0, ..., wxWindows], str, None]

</summary>

Union of
- Literal of
  - 0BSD
  - AAL
  - Abstyles
  - AdaCore-doc
  - Adobe-2006
  - Adobe-Glyph
  - ADSL
  - AFL-1.1
  - AFL-1.2
  - AFL-2.0
  - AFL-2.1
  - AFL-3.0
  - Afmparse
  - AGPL-1.0-only
  - AGPL-1.0-or-later
  - AGPL-3.0-only
  - AGPL-3.0-or-later
  - Aladdin
  - AMDPLPA
  - AML
  - AMPAS
  - ANTLR-PD
  - ANTLR-PD-fallback
  - Apache-1.0
  - Apache-1.1
  - Apache-2.0
  - APAFML
  - APL-1.0
  - App-s2p
  - APSL-1.0
  - APSL-1.1
  - APSL-1.2
  - APSL-2.0
  - Arphic-1999
  - Artistic-1.0
  - Artistic-1.0-cl8
  - Artistic-1.0-Perl
  - Artistic-2.0
  - ASWF-Digital-Assets-1.0
  - ASWF-Digital-Assets-1.1
  - Baekmuk
  - Bahyph
  - Barr
  - Beerware
  - Bitstream-Charter
  - Bitstream-Vera
  - BitTorrent-1.0
  - BitTorrent-1.1
  - blessing
  - BlueOak-1.0.0
  - Boehm-GC
  - Borceux
  - Brian-Gladman-3-Clause
  - BSD-1-Clause
  - BSD-2-Clause
  - BSD-2-Clause-Patent
  - BSD-2-Clause-Views
  - BSD-3-Clause
  - BSD-3-Clause-Attribution
  - BSD-3-Clause-Clear
  - BSD-3-Clause-LBNL
  - BSD-3-Clause-Modification
  - BSD-3-Clause-No-Military-License
  - BSD-3-Clause-No-Nuclear-License
  - BSD-3-Clause-No-Nuclear-License-2014
  - BSD-3-Clause-No-Nuclear-Warranty
  - BSD-3-Clause-Open-MPI
  - BSD-4-Clause
  - BSD-4-Clause-Shortened
  - BSD-4-Clause-UC
  - BSD-4.3RENO
  - BSD-4.3TAHOE
  - BSD-Advertising-Acknowledgement
  - BSD-Attribution-HPND-disclaimer
  - BSD-Protection
  - BSD-Source-Code
  - BSL-1.0
  - BUSL-1.1
  - bzip2-1.0.6
  - C-UDA-1.0
  - CAL-1.0
  - CAL-1.0-Combined-Work-Exception
  - Caldera
  - CATOSL-1.1
  - CC-BY-1.0
  - CC-BY-2.0
  - CC-BY-2.5
  - CC-BY-2.5-AU
  - CC-BY-3.0
  - CC-BY-3.0-AT
  - CC-BY-3.0-DE
  - CC-BY-3.0-IGO
  - CC-BY-3.0-NL
  - CC-BY-3.0-US
  - CC-BY-4.0
  - CC-BY-NC-1.0
  - CC-BY-NC-2.0
  - CC-BY-NC-2.5
  - CC-BY-NC-3.0
  - CC-BY-NC-3.0-DE
  - CC-BY-NC-4.0
  - CC-BY-NC-ND-1.0
  - CC-BY-NC-ND-2.0
  - CC-BY-NC-ND-2.5
  - CC-BY-NC-ND-3.0
  - CC-BY-NC-ND-3.0-DE
  - CC-BY-NC-ND-3.0-IGO
  - CC-BY-NC-ND-4.0
  - CC-BY-NC-SA-1.0
  - CC-BY-NC-SA-2.0
  - CC-BY-NC-SA-2.0-DE
  - CC-BY-NC-SA-2.0-FR
  - CC-BY-NC-SA-2.0-UK
  - CC-BY-NC-SA-2.5
  - CC-BY-NC-SA-3.0
  - CC-BY-NC-SA-3.0-DE
  - CC-BY-NC-SA-3.0-IGO
  - CC-BY-NC-SA-4.0
  - CC-BY-ND-1.0
  - CC-BY-ND-2.0
  - CC-BY-ND-2.5
  - CC-BY-ND-3.0
  - CC-BY-ND-3.0-DE
  - CC-BY-ND-4.0
  - CC-BY-SA-1.0
  - CC-BY-SA-2.0
  - CC-BY-SA-2.0-UK
  - CC-BY-SA-2.1-JP
  - CC-BY-SA-2.5
  - CC-BY-SA-3.0
  - CC-BY-SA-3.0-AT
  - CC-BY-SA-3.0-DE
  - CC-BY-SA-3.0-IGO
  - CC-BY-SA-4.0
  - CC-PDDC
  - CC0-1.0
  - CDDL-1.0
  - CDDL-1.1
  - CDL-1.0
  - CDLA-Permissive-1.0
  - CDLA-Permissive-2.0
  - CDLA-Sharing-1.0
  - CECILL-1.0
  - CECILL-1.1
  - CECILL-2.0
  - CECILL-2.1
  - CECILL-B
  - CECILL-C
  - CERN-OHL-1.1
  - CERN-OHL-1.2
  - CERN-OHL-P-2.0
  - CERN-OHL-S-2.0
  - CERN-OHL-W-2.0
  - CFITSIO
  - checkmk
  - ClArtistic
  - Clips
  - CMU-Mach
  - CNRI-Jython
  - CNRI-Python
  - CNRI-Python-GPL-Compatible
  - COIL-1.0
  - Community-Spec-1.0
  - Condor-1.1
  - copyleft-next-0.3.0
  - copyleft-next-0.3.1
  - Cornell-Lossless-JPEG
  - CPAL-1.0
  - CPL-1.0
  - CPOL-1.02
  - Crossword
  - CrystalStacker
  - CUA-OPL-1.0
  - Cube
  - curl
  - D-FSL-1.0
  - diffmark
  - DL-DE-BY-2.0
  - DOC
  - Dotseqn
  - DRL-1.0
  - DSDP
  - dtoa
  - dvipdfm
  - ECL-1.0
  - ECL-2.0
  - EFL-1.0
  - EFL-2.0
  - eGenix
  - Elastic-2.0
  - Entessa
  - EPICS
  - EPL-1.0
  - EPL-2.0
  - ErlPL-1.1
  - etalab-2.0
  - EUDatagrid
  - EUPL-1.0
  - EUPL-1.1
  - EUPL-1.2
  - Eurosym
  - Fair
  - FDK-AAC
  - Frameworx-1.0
  - FreeBSD-DOC
  - FreeImage
  - FSFAP
  - FSFUL
  - FSFULLR
  - FSFULLRWD
  - FTL
  - GD
  - GFDL-1.1-invariants-only
  - GFDL-1.1-invariants-or-later
  - GFDL-1.1-no-invariants-only
  - GFDL-1.1-no-invariants-or-later
  - GFDL-1.1-only
  - GFDL-1.1-or-later
  - GFDL-1.2-invariants-only
  - GFDL-1.2-invariants-or-later
  - GFDL-1.2-no-invariants-only
  - GFDL-1.2-no-invariants-or-later
  - GFDL-1.2-only
  - GFDL-1.2-or-later
  - GFDL-1.3-invariants-only
  - GFDL-1.3-invariants-or-later
  - GFDL-1.3-no-invariants-only
  - GFDL-1.3-no-invariants-or-later
  - GFDL-1.3-only
  - GFDL-1.3-or-later
  - Giftware
  - GL2PS
  - Glide
  - Glulxe
  - GLWTPL
  - gnuplot
  - GPL-1.0-only
  - GPL-1.0-or-later
  - GPL-2.0-only
  - GPL-2.0-or-later
  - GPL-3.0-only
  - GPL-3.0-or-later
  - Graphics-Gems
  - gSOAP-1.3b
  - HaskellReport
  - Hippocratic-2.1
  - HP-1986
  - HPND
  - HPND-export-US
  - HPND-Markus-Kuhn
  - HPND-sell-variant
  - HPND-sell-variant-MIT-disclaimer
  - HTMLTIDY
  - IBM-pibs
  - ICU
  - IEC-Code-Components-EULA
  - IJG
  - IJG-short
  - ImageMagick
  - iMatix
  - Imlib2
  - Info-ZIP
  - Inner-Net-2.0
  - Intel
  - Intel-ACPI
  - Interbase-1.0
  - IPA
  - IPL-1.0
  - ISC
  - Jam
  - JasPer-2.0
  - JPL-image
  - JPNIC
  - JSON
  - Kazlib
  - Knuth-CTAN
  - LAL-1.2
  - LAL-1.3
  - Latex2e
  - Latex2e-translated-notice
  - Leptonica
  - LGPL-2.0-only
  - LGPL-2.0-or-later
  - LGPL-2.1-only
  - LGPL-2.1-or-later
  - LGPL-3.0-only
  - LGPL-3.0-or-later
  - LGPLLR
  - Libpng
  - libpng-2.0
  - libselinux-1.0
  - libtiff
  - libutil-David-Nugent
  - LiLiQ-P-1.1
  - LiLiQ-R-1.1
  - LiLiQ-Rplus-1.1
  - Linux-man-pages-1-para
  - Linux-man-pages-copyleft
  - Linux-man-pages-copyleft-2-para
  - Linux-man-pages-copyleft-var
  - Linux-OpenIB
  - LOOP
  - LPL-1.0
  - LPL-1.02
  - LPPL-1.0
  - LPPL-1.1
  - LPPL-1.2
  - LPPL-1.3a
  - LPPL-1.3c
  - LZMA-SDK-9.11-to-9.20
  - LZMA-SDK-9.22
  - MakeIndex
  - Martin-Birgmeier
  - metamail
  - Minpack
  - MirOS
  - MIT
  - MIT-0
  - MIT-advertising
  - MIT-CMU
  - MIT-enna
  - MIT-feh
  - MIT-Festival
  - MIT-Modern-Variant
  - MIT-open-group
  - MIT-Wu
  - MITNFA
  - Motosoto
  - mpi-permissive
  - mpich2
  - MPL-1.0
  - MPL-1.1
  - MPL-2.0
  - MPL-2.0-no-copyleft-exception
  - mplus
  - MS-LPL
  - MS-PL
  - MS-RL
  - MTLL
  - MulanPSL-1.0
  - MulanPSL-2.0
  - Multics
  - Mup
  - NAIST-2003
  - NASA-1.3
  - Naumen
  - NBPL-1.0
  - NCGL-UK-2.0
  - NCSA
  - Net-SNMP
  - NetCDF
  - Newsletr
  - NGPL
  - NICTA-1.0
  - NIST-PD
  - NIST-PD-fallback
  - NIST-Software
  - NLOD-1.0
  - NLOD-2.0
  - NLPL
  - Nokia
  - NOSL
  - Noweb
  - NPL-1.0
  - NPL-1.1
  - NPOSL-3.0
  - NRL
  - NTP
  - NTP-0
  - O-UDA-1.0
  - OCCT-PL
  - OCLC-2.0
  - ODbL-1.0
  - ODC-By-1.0
  - OFFIS
  - OFL-1.0
  - OFL-1.0-no-RFN
  - OFL-1.0-RFN
  - OFL-1.1
  - OFL-1.1-no-RFN
  - OFL-1.1-RFN
  - OGC-1.0
  - OGDL-Taiwan-1.0
  - OGL-Canada-2.0
  - OGL-UK-1.0
  - OGL-UK-2.0
  - OGL-UK-3.0
  - OGTSL
  - OLDAP-1.1
  - OLDAP-1.2
  - OLDAP-1.3
  - OLDAP-1.4
  - OLDAP-2.0
  - OLDAP-2.0.1
  - OLDAP-2.1
  - OLDAP-2.2
  - OLDAP-2.2.1
  - OLDAP-2.2.2
  - OLDAP-2.3
  - OLDAP-2.4
  - OLDAP-2.5
  - OLDAP-2.6
  - OLDAP-2.7
  - OLDAP-2.8
  - OLFL-1.3
  - OML
  - OpenPBS-2.3
  - OpenSSL
  - OPL-1.0
  - OPL-UK-3.0
  - OPUBL-1.0
  - OSET-PL-2.1
  - OSL-1.0
  - OSL-1.1
  - OSL-2.0
  - OSL-2.1
  - OSL-3.0
  - Parity-6.0.0
  - Parity-7.0.0
  - PDDL-1.0
  - PHP-3.0
  - PHP-3.01
  - Plexus
  - PolyForm-Noncommercial-1.0.0
  - PolyForm-Small-Business-1.0.0
  - PostgreSQL
  - PSF-2.0
  - psfrag
  - psutils
  - Python-2.0
  - Python-2.0.1
  - Qhull
  - QPL-1.0
  - QPL-1.0-INRIA-2004
  - Rdisc
  - RHeCos-1.1
  - RPL-1.1
  - RPL-1.5
  - RPSL-1.0
  - RSA-MD
  - RSCPL
  - Ruby
  - SAX-PD
  - Saxpath
  - SCEA
  - SchemeReport
  - Sendmail
  - Sendmail-8.23
  - SGI-B-1.0
  - SGI-B-1.1
  - SGI-B-2.0
  - SGP4
  - SHL-0.5
  - SHL-0.51
  - SimPL-2.0
  - SISSL
  - SISSL-1.2
  - Sleepycat
  - SMLNJ
  - SMPPL
  - SNIA
  - snprintf
  - Spencer-86
  - Spencer-94
  - Spencer-99
  - SPL-1.0
  - SSH-OpenSSH
  - SSH-short
  - SSPL-1.0
  - SugarCRM-1.1.3
  - SunPro
  - SWL
  - Symlinks
  - TAPR-OHL-1.0
  - TCL
  - TCP-wrappers
  - TermReadKey
  - TMate
  - TORQUE-1.1
  - TOSL
  - TPDL
  - TPL-1.0
  - TTWL
  - TU-Berlin-1.0
  - TU-Berlin-2.0
  - UCAR
  - UCL-1.0
  - Unicode-DFS-2015
  - Unicode-DFS-2016
  - Unicode-TOU
  - UnixCrypt
  - Unlicense
  - UPL-1.0
  - Vim
  - VOSTROM
  - VSL-1.0
  - W3C
  - W3C-19980720
  - W3C-20150513
  - w3m
  - Watcom-1.0
  - Widget-Workshop
  - Wsuipa
  - WTFPL
  - X11
  - X11-distribute-modifications-variant
  - Xdebug-1.03
  - Xerox
  - Xfig
  - XFree86-1.1
  - xinetd
  - xlock
  - Xnet
  - xpp
  - XSkat
  - YPL-1.0
  - YPL-1.1
  - Zed
  - Zend-2.0
  - Zimbra-1.3
  - Zimbra-1.4
  - Zlib
  - zlib-acknowledgement
  - ZPL-1.1
  - ZPL-2.0
  - ZPL-2.1

- Literal of
  - AGPL-1.0
  - AGPL-3.0
  - BSD-2-Clause-FreeBSD
  - BSD-2-Clause-NetBSD
  - bzip2-1.0.5
  - eCos-2.0
  - GFDL-1.1
  - GFDL-1.2
  - GFDL-1.3
  - GPL-1.0
  - GPL-1.0+
  - GPL-2.0
  - GPL-2.0+
  - GPL-2.0-with-autoconf-exception
  - GPL-2.0-with-bison-exception
  - GPL-2.0-with-classpath-exception
  - GPL-2.0-with-font-exception
  - GPL-2.0-with-GCC-exception
  - GPL-3.0
  - GPL-3.0+
  - GPL-3.0-with-autoconf-exception
  - GPL-3.0-with-GCC-exception
  - LGPL-2.0
  - LGPL-2.0+
  - LGPL-2.1
  - LGPL-2.1+
  - LGPL-3.0
  - LGPL-3.0+
  - Nunit
  - StandardML-NJ
  - wxWindows

- str
- None


</details>

## `links`<sub> Sequence[str]</sub> ≝ `()`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence[Maintainer]</sub> ≝ `()`
Maintainers of this resource.
If not specified `authors` are maintainers and at least some of them should specify their `github_user` name

<details><summary>Sequence[Maintainer]

</summary>


**Maintainer:**
### `maintainers.i.name`<sub> Optional[str]</sub> ≝ `None`
Full name



### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `maintainers.i.github_user`<sub> str</sub>
GitHub user name



### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[str (AfterValidator(validate_orcid_id))]

</details>

## `rdf_source`<sub> Union</sub> ≝ `None`
Resource description file (RDF) source; used to keep track of where an rdf.yaml was loaded from.
Do not set this field in a YAML file.


Union[Url (max_length=2083 allowed_schemes=['http', 'https']), RelativeFilePath, None]

## `source`<sub> Union</sub> ≝ `None`
URL or relative path to the source of the resource


Union[Url (max_length=2083 allowed_schemes=['http', 'https']), RelativeFilePath, None]

## `tags`<sub> Sequence[str]</sub> ≝ `()`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `version`<sub> Optional</sub> ≝ `None`
The version number of the resource. Its format must be a string in
`MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/).
Hyphens and plus signs are not allowed to be compatible with
https://packaging.pypa.io/en/stable/version.html.
The initial version should be '0.1.0'.
[*Example:*](#version) '0.1.0'


Optional[str (AfterValidator(validate_version))]

# Example values
### `authors.i.orcid`
0000-0001-2345-6789
### `badges.i.label`
Open in Colab
### `badges.i.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `badges.i.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `config`
{'bioimage_io': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `covers`
cover.png
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/README.md
- README.md

### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models/unet2d_nuclei_broad
### `license`
- MIT
- CC-BY-4.0
- BSD-2-Clause

### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.i.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `version`
0.1.0
