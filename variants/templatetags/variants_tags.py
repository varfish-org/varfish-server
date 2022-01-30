import sys

from django import template
from django.utils import formats
from django.utils.html import avoid_wrapping
import nltk

from django.conf import settings
from ..models import (
    Case,
    only_source_name as _models_only_source_name,
    _variant_scores_mutationtaster_rank_model,
)
from projectroles.app_settings import AppSettingAPI
from geneinfo.models import GeneIdToInheritance, Hpo, HpoName

modes_of_inheritance = dict(GeneIdToInheritance.MODES_OF_INHERITANCE)
register = template.Library()

nltk.data.path.append("misc/nltk_data")
stop_words = set(nltk.corpus.stopwords.words("english"))

# Row colors to use.
ROW_COLORS = {
    "pathogenic": "#dc354533",
    "uncertain": "#ffc10733",
    "benign": "#28a74533",
    "wip": "#6c757d33",
    "__invalid__": "#FF00FF",
}


@register.simple_tag
def get_login_page_text():
    return settings.VARFISH_LOGIN_PAGE_TEXT


@register.simple_tag
def get_row_bgcolor(rating):
    """Return color to use for row background for rating."""
    return ROW_COLORS.get(rating, ROW_COLORS["__invalid__"])


@register.simple_tag
def get_details_cases(project):
    """Return 5 most recent updated cases for the project details page."""
    return Case.objects.filter(project=project).order_by("-date_modified")[:5]


@register.filter
def acmg_classification(entry):
    """Return ACMG classification from entry, if any"""
    if entry.acmg_class_override:
        return entry.acmg_class_override
    elif entry.acmg_class_auto:
        return entry.acmg_class_auto
    else:
        return None


@register.filter
def acmg_classification2(entry):
    """Return ACMG classification from entry, if any"""
    if entry.class_override:
        return entry.class_override
    elif entry.class_auto:
        return entry.class_auto
    else:
        return None


@register.filter
def acmg_badge_class(entry):
    """Return ACMG classification from entry, if any"""
    val = acmg_classification(entry)
    if not val:
        return "badge badge-light text-muted"
    elif val > 3:
        return "badge badge-danger text-white"
    elif val == 3:
        return "badge badge-warning text-black"
    else:
        return "badge badge-success text-white"


@register.filter
def acmg_badge_class2(entry):
    """Return ACMG classification from entry, if any"""
    val = acmg_classification2(entry)
    if not val:
        return "badge badge-light text-muted"
    elif val > 3:
        return "badge badge-danger text-white"
    elif val == 3:
        return "badge badge-warning text-black"
    else:
        return "badge badge-success text-white"


@register.filter
def only_source_name(full_name):
    return _models_only_source_name(full_name)


#: Clinvar status to stars.
CLINVAR_STARS = {
    "practice guideline": 4,
    "reviewed by expert panel": 3,
    "criteria provided, multiple submitters, no conflicts": 2,
    "criteria provided, conflicting interpretations": 1,
    "criteria provided, single submitter": 1,
    "no assertion criteria provided": 0,
    "no assertion provided": 0,
}


@register.filter
def mutationtaster_rank(data):
    return _variant_scores_mutationtaster_rank_model(data)


@register.filter
def mutationtaster_scale_bayes(prob):
    return int(prob) / 1000


@register.filter
def status_stars(status):
    return CLINVAR_STARS.get(status, 0)


@register.filter
def status_importance(status):
    if CLINVAR_STARS.get(status):
        return list(CLINVAR_STARS.keys()).index(status)
    return len(CLINVAR_STARS)


#: Clinvar significance to colour.
COLOURS = {
    "pathogenic": "danger",
    "likely_pathogenic": "warning",
    "uncertain_significance": "info",
    "likely_benign": "secondary",
    "benign": "secondary",
}


#: Clinvar significance to text.
SIGNIFICANCE = {
    "pathogenic": "pathogenic",
    "likely_pathogenic": "likely patho.",
    "uncertain_significance": "uncertain sign.",
    "likely_benign": "likely benign",
    "benign": "benign",
}


@register.filter
def significance_text(sig):
    return SIGNIFICANCE.get(sig, "undefined")


@register.filter
def significance_color(sig):
    return COLOURS.get(sig, "secondary")


@register.filter
def significance_importance(sig):
    if SIGNIFICANCE.get(sig):
        return list(SIGNIFICANCE.keys()).index(sig)
    return len(SIGNIFICANCE)


@register.filter
def smallvar_description(entry):
    """Return small variant description from query result"""
    keys = (
        "release",
        "chromosome",
        "start",
        "end",
        "bin",
        "reference",
        "alternative",
        "ensembl_gene_id",
    )
    if isinstance(entry, dict):
        return "-".join(map(str, (entry[key] for key in keys)))
    else:
        return "-".join(map(str, (getattr(entry, key) for key in keys)))


#: Mapping of small variant flag value to font awesome icon.
FLAG_VALUE_TO_FA = {
    "positive": "fa-solid:exclamation-circle",
    "uncertain": "fa-solid:question",
    "negative": "fa-solid:minus-circle",
    "empty": "fa-solid:times",
}


@register.filter
def flag_value_to_fa(value):
    return FLAG_VALUE_TO_FA.get(value, "fa-solid:times")


#: Mapping of small variant flag value to Bootstrap color class.
FLAG_VALUE_TO_COLOR = {
    "positive": "text-danger",
    "uncertain": "text-warning",
    "negative": "text-success",
    "empty": "text-secondary",
}


@register.filter
def flag_value_to_color(value):
    return FLAG_VALUE_TO_COLOR.get(value, "")


CASE_STATUS_TO_COLOR = {
    "initial": "secondary",
    "active": "info",
    "closed-solved": "success",
    "closed-uncertain": "warning",
    "closed-unsolved": "danger",
}


@register.filter
def case_status_to_color(value):
    return CASE_STATUS_TO_COLOR.get(value, "")


CASE_STATUS_TO_ICON = {
    "initial": "fa-solid:asterisk",
    "active": "fa-solid:filter",
    "closed-solved": "fa-solid:check",
    "closed-uncertain": "fa-solid:question",
    "closed-unsolved": "fa-solid:times",
}


@register.filter
def case_status_to_icon(value):
    return CASE_STATUS_TO_ICON.get(value, "")


CASE_STATUS_TO_CLASS = {
    "initial": "text-secondary",
    "active": "text-info",
    "closed-solved": "text-success",
    "closed-uncertain": "text-warning",
    "closed-unsolved": "text-danger",
}


@register.filter
def case_status_to_class(value):
    return "%s text-%s" % (CASE_STATUS_TO_CLASS.get(value, ""), case_status_to_color(value))


CASE_STATUS_TO_ORDER = {
    "initial": 0,
    "active": 4,
    "closed-solved": 3,
    "closed-unsolved": 1,
    "closed-uncertain": 2,
}


@register.filter
def case_status_to_order(value):
    return CASE_STATUS_TO_ORDER.get(value, -1000)


@register.filter
def flag_class(row):
    """Return CSS class to used based on the flag of ``row``.

    Report "wip" class if a flag is set for {visual, validation, phenotype_match}.
    If the summary flag has been set, use this value instead.
    """
    if row.flag_summary and row.flag_summary != "empty":
        return row.flag_summary  # short-circuit
    # Except bookmark flag as it is set automatically if not actively disabled by user.
    bool_flags = (
        "candidate",
        "doesnt_segregate",
        "final_causative",
        "for_validation",
        "no_disease_association",
        "segregates",
    )
    flags = ("visual", "validation", "phenotype_match", "molecular")
    for flag in flags:
        flag_name = "flag_%s" % flag
        flag_value = getattr(row, flag_name)
        if flag_value and flag_value != "empty":
            return "wip"
    for flag in bool_flags:
        flag_name = "flag_%s" % flag
        if getattr(row, flag_name):
            return "wip"
    return "empty"


@register.simple_tag
def ambiguous_frequency_warning(row, exac, thousandg, gnomad_exomes, gnomad_genomes, inhouse):
    tables = {
        "exac": exac,
        "thousand_genomes": thousandg,
        "gnomad_exomes": gnomad_exomes,
        "gnomad_genomes": gnomad_genomes,
        "inhouse": inhouse,
    }
    ambiguous_tables = []

    if all(tables.values()) or not any(tables.values()):
        return ambiguous_tables

    for table, activated in tables.items():
        if not activated:
            if table == "inhouse":
                hom_field = "inhouse_hom_alt"
            else:
                hom_field = "{}_homozygous".format(table)
            hom_failed = getattr(row, hom_field, 0) > 50
            freq_failed = getattr(row, "{}_frequency".format(table), 0) > 0.1
            if freq_failed or hom_failed:
                ambiguous_tables.append(table)

    return ambiguous_tables


@register.simple_tag
def chrx_het_hom_ratio(case, sample):
    """Return het./hom. ratio of ``sample`` in ``case``."""
    return case.chrx_het_hom_ratio(sample)


@register.filter
def from_bamstats(stats, value):
    """Return percentage that a part represents of a total."""
    if value == "mean target coverage":
        return stats.get("summary", {}).get("mean coverage")
    elif value == "total target size":
        return stats.get("summary", {}).get("total target size")
    elif value == "total reads":
        return stats["bamstats"]["sequences"] // 2
    elif value == "percent duplicates":
        if stats["bamstats"]["sequences"]:
            return 100.0 * stats["bamstats"]["reads duplicated"] / stats["bamstats"]["sequences"]
        else:
            return 0.0
    else:
        return "INVALID"


@register.filter(is_safe=True)
def asint(value):
    try:
        return int(value)
    except ValueError:
        return -1


@register.filter(is_safe=True)
def bpformat(bp):
    """
    Format the value like a 'human-readable' file size (i.e. 13 Kbp, 4.1 Mbp,
    102 bp, etc.).
    """
    try:
        bp = int(bp)
    except (TypeError, ValueError, UnicodeDecodeError):
        return avoid_wrapping("0 bp")

    def bp_number_format(value):
        return formats.number_format(round(value, 1), 1)

    kbp = 1 << 10
    mbp = 1 << 20
    gbp = 1 << 30
    tbp = 1 << 40
    pbp = 1 << 50

    negative = bp < 0
    if negative:
        bp = -bp  # Allow formatting of negative numbers.

    if bp < kbp:
        value = "%(size)d byte" % {"size": bp}
    elif bp < mbp:
        value = "%s Kbp" % bp_number_format(bp / kbp)
    elif bp < gbp:
        value = "%s Mbp" % bp_number_format(bp / mbp)
    elif bp < tbp:
        value = "%s Gbp" % bp_number_format(bp / gbp)
    elif bp < pbp:
        value = "%s Tbp" % bp_number_format(bp / tbp)
    else:
        value = "%s Pbp" % bp_number_format(bp / bp)

    if negative:
        value = "-%s" % value
    return avoid_wrapping(value)


# TODO: move to sodar-core
@register.simple_tag
def get_user_setting(user, app_name, setting_name):
    """Return user setting."""
    if settings.KIOSK_MODE:
        return
    setting_api = AppSettingAPI()
    return setting_api.get_app_setting(app_name, setting_name, user=user)


@register.filter
def allelic_balance(gt):
    """Return allelic balance from genotype value."""
    if not gt.get("dp"):
        return 0.0
    else:
        return gt.get("ad") / gt.get("dp")


@register.filter
def mode_of_inheritance_description(mode_of_inheritance):
    """Return description for mode of inheritance"""
    return modes_of_inheritance.get(mode_of_inheritance, "No description available.")


@register.filter
def listsort(l):
    return sorted(l)


@register.filter
def get_symbol(record):
    return record.symbol or record.gene_symbol or None


@register.filter
def get_pubmed_linkout(record, hpoterms):
    symbol = record.symbol or record.gene_symbol
    terms = " OR ".join(
        [
            "(%s)"
            % " AND ".join(
                word
                for word in map(lambda x: x.lower(), nltk.tokenize.word_tokenize(title))
                if word not in stop_words
            )
            for _, title in hpoterms.items()
        ]
    )
    return "{} AND ({})".format(symbol, terms)


@register.filter
def add_omim_information(term):
    info = {}
    for record in Hpo.objects.filter(database_id=term).values("hpo_id"):
        hpo_name = HpoName.objects.filter(hpo_id=record["hpo_id"])
        if hpo_name.exists():
            info[record["hpo_id"]] = hpo_name.first().name
        else:
            info[record["hpo_id"]] = "unknown HPO term"
    return info


@register.filter
def check_mt_position_homopolymer(pos):
    return (
        (pos >= 66 and pos <= 71)
        or (pos >= 300 and pos <= 316)
        or (pos >= 513 and pos <= 525)
        or (pos >= 3106 and pos <= 3107)
        or (pos >= 12418 and pos <= 12425)
        or (pos >= 16182 and pos <= 16194)
    )


@register.filter
def sex_errors(item, disable_pedigree_sex_check):
    return item.sex_errors(disable_pedigree_sex_check=disable_pedigree_sex_check)


@register.simple_tag
def get_is_testing():
    """Return whether we are in testing mode."""
    return sys.argv[1:2] == ["test"]


@register.simple_tag
def get_term_description(term):
    """Return HPO, Orphanet, or OMIM description."""
    if term.startswith("HP:"):
        terms = HpoName.objects.filter(hpo_id=term)
        if terms:
            return terms.first().name
        else:
            return None
    else:
        for record in Hpo.objects.filter(database_id=term).order_by("-name"):
            return record.name
        else:
            return None


#: Links from browser name and genome release to base URLs.
LINKOUT_URLS = {
    ("ucsc", "GRCh37"): "https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg19",
    ("ucsc", "GRCh38"): "https://genome-euro.ucsc.edu/cgi-bin/hgTracks?db=hg38",
    ("ensembl", "GRCh37"): "https://grch37.ensembl.org/Homo_sapiens/Location/View?",
    ("ensembl", "GRCh38"): "https://ensembl.org/Homo_sapiens/Location/View?",
    ("dgv", "GRCh37"): "http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg19/",
    ("dgv", "GRCh38"): "http://dgv.tcag.ca/gb2/gbrowse/dgv2_hg38/",
    ("gnomad", "GRCh37"): "http://gnomad.broadinstitute.org/region",
    ("gnomad", "GRCh38"): "http://gnomad.broadinstitute.org/region",
    ("umd", "GRCh37"): "http://umd-predictor.eu/webservice.php?",
    ("varsome", "GRCh37"): "https://varsome.com/variant/hg19/chr",
    ("varsome", "GRCh38"): "https://varsome.com/variant/hg38/",
    ("variant_validator", "GRCh37"): True,  # no URL, via javascript
    ("variant_validator", "GRCh38"): True,  # no URL, via javascript
}


@register.simple_tag
def linkout_available_for(database, release):
    """Return whether the linkout to the given database is available for the given release."""
    return bool(LINKOUT_URLS.get((database, release), False))


@register.simple_tag
def linkout_base_url(database, release):
    """Return linkout base URL."""
    return LINKOUT_URLS.get((database, release), None)


@register.simple_tag
def gnomad_release(release):
    return {"GRCh37": "gnomad_r2_1", "GRCh38": "gnomad_r3"}.get(release, None)


@register.simple_tag
def same_release(cases):
    """Return whether an iterable of cases has the same genome release."""
    return len({case.release for case in cases}) == 1


@register.simple_tag
def entry_chr(entry):
    """Return chromosome value for the result entry.

    Adds ``chr`` prefix as required.
    """
    if not entry.chromosome.startswith("chr"):
        return "chr" + entry.chromosome
    else:
        return entry.chromosome
