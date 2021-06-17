import hashlib
import uuid as uuid_object

from Crypto.PublicKey import RSA
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.urls import reverse
from projectroles.models import Project
from cryptographic_fields.fields import EncryptedTextField

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Consortium(models.Model):
    """Description of a consortium that the local or a remote site can be within."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    identifier = models.CharField(
        max_length=128,
        unique=True,
        null=False,
        blank=False,
        help_text="Identifier of consortium (e.g., in reverse DNS notation)",
    )
    title = models.CharField(
        max_length=128, null=False, blank=False, help_text="Title of the consortium"
    )
    description = models.TextField(
        null=True, blank=True, help_text="Optional description of the consortium"
    )

    ENABLED = "enabled"
    DISABLED = "disabled"
    STATE_CHOICES = (
        (ENABLED, ENABLED),
        (DISABLED, DISABLED),
    )
    state = models.CharField(max_length=100, choices=STATE_CHOICES, help_text="Consortium state.")

    projects = models.ManyToManyField(
        Project, through="ConsortiumAssignment", help_text="Projects assigned to consortium"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("beaconsite:consortium-detail", kwargs={"consortium": self.sodar_uuid})


def _insert_char_every_n_chars(string, char="\n", every=64):
    return char.join(string[i : i + every] for i in range(0, len(string), every))


class Site(models.Model):
    """Description of the local or a remote site."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    consortia = models.ManyToManyField(
        Consortium,
        related_name="sites",
        through="ConsortiumMember",
        help_text="Consortia that the site is a member of",
    )

    LOCAL = "local"
    REMOTE = "remote"
    ROLE_CHOICES = (
        (LOCAL, LOCAL),
        (REMOTE, REMOTE),
    )

    ENABLED = "enabled"
    DISABLED = "disabled"
    STATE_CHOICES = (
        (ENABLED, ENABLED),
        (DISABLED, DISABLED),
    )

    AES_128_CBC = "aes128-cbc"
    AES_192_CBC = "aes192-cbc"
    AES_256_CBC = "aes256-cbc"
    KEY_ALGOS_SYMMETRIC = (AES_128_CBC, AES_192_CBC, AES_256_CBC)
    RSA_SHA256 = "rsa-sha256"
    RSA_SHA512 = "rsa-sha512"
    ECDSA_SHA256 = "ecdsa-sha256"
    ECDSA_SHA512 = "ecdsa-sha512"
    KEY_ALGOS_ASYMMETRIC = (RSA_SHA256, RSA_SHA512, ECDSA_SHA256, ECDSA_SHA512)
    KEY_ALGO_CHOICES = (
        (RSA_SHA256, RSA_SHA256),
        (RSA_SHA512, RSA_SHA512),
        (ECDSA_SHA256, ECDSA_SHA256),
        (ECDSA_SHA512, ECDSA_SHA512),
    )

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, help_text="Site role.")

    state = models.CharField(max_length=100, choices=STATE_CHOICES, help_text="Site state.")

    identifier = models.CharField(
        max_length=128,
        unique=True,
        null=False,
        blank=False,
        help_text="Site name (in reverse DNS notation)",
    )
    title = models.CharField(max_length=128, null=False, blank=False, help_text="Title of the site")
    description = models.TextField(
        null=True, blank=True, help_text="Optional description of the site"
    )

    entrypoint_url = models.TextField(null=False, blank=False, help_text="Site base URL")

    key_algo = models.CharField(
        max_length=64, choices=KEY_ALGO_CHOICES, help_text="Key algorithm to use"
    )

    max_clock_skew = models.IntegerField(
        default=(5 * 60), help_text="Maximal age of request based on date header"
    )

    def is_key_algo_symmetric(self):
        return self.key_algo in self.KEY_ALGOS_SYMMETRIC

    private_key = EncryptedTextField(
        null=True, blank=True, help_text="(Private) key for (a)symmetric encryption."
    )
    public_key = models.TextField(
        null=True, blank=True, help_text="Public key for asymmetric encryption."
    )

    def get_all_projects(self):
        # TODO: speed this up with raw SQL query
        result = {}
        for consortium in self.consortia.all():
            for project in consortium.projects.all():
                if project.pk not in result:
                    result[project.pk] = project
        return result.values()

    def public_key_fingerprints(self):
        k = RSA.import_key(self.public_key)
        sha256digest = hashlib.sha256(k.exportKey("DER", pkcs=8)).hexdigest()
        sha1digest = hashlib.sha1(k.exportKey("DER", pkcs=8)).hexdigest()
        md5digest = hashlib.md5(k.exportKey("DER", pkcs=8)).hexdigest()
        return "\n".join(
            [
                "md5:%s" % _insert_char_every_n_chars(md5digest, ":", 2),
                "sha1:%s" % _insert_char_every_n_chars(sha1digest, ":", 2),
                "sha256:%s" % _insert_char_every_n_chars(sha256digest, ":", 2),
            ]
        )

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self.role == Site.LOCAL and self.state == Site.ENABLED:
            local_site_pks = [
                s.pk for s in Site.objects.filter(state=Site.ENABLED, role=Site.LOCAL)
            ]
            if local_site_pks and self.pk not in local_site_pks:
                raise ValidationError("There must be at most one active local site!")
        if (
            self.role == Site.LOCAL
            and self.key_algo not in Site.KEY_ALGOS_SYMMETRIC
            and not self.public_key
        ):
            raise ValidationError(
                "both public and private key are needed for local sites for RSA/ECDSA."
            )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("beaconsite:site-detail", kwargs={"site": self.sodar_uuid})


class ConsortiumMember(models.Model):
    """Site membership within a consortium."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    consortium = models.ForeignKey(Consortium, on_delete=models.CASCADE)


class ConsortiumAssignment(models.Model):
    """Making a project available in a consortium."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    consortium = models.ForeignKey(Consortium, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Query(models.Model):
    """Store information about an outgoing or incoming query."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    src_site = models.ForeignKey(
        Site,
        related_name="src_queries",
        null=False,
        on_delete=models.CASCADE,
        help_text="Source of query",
    )
    dst_site = models.ForeignKey(
        Site,
        related_name="dst_queries",
        null=False,
        on_delete=models.CASCADE,
        help_text="Recipient of query",
    )

    GET = "GET"
    HTTP_METHOD_CHOICES = ((GET, GET),)

    http_url = models.TextField(null=False, help_text="URL of query")
    http_method = models.CharField(
        max_length=64, choices=HTTP_METHOD_CHOICES, help_text="HTTP method that was used"
    )
    http_header = models.TextField(null=False, help_text="HTTP request header content")
    http_body = models.TextField(null=True, blank=True, help_text="HTTP request body content")

    # TODO: maybe store stubs on source project/case/user

    src_project = models.ForeignKey(
        "projectroles.Project",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Origin project, if local source",
    )
    src_case = models.ForeignKey(
        "variants.Case",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Case that this query was performed for, if local source",
    )
    src_user_username = models.CharField(
        max_length=128, null=True, blank=True, help_text="User name from query source"
    )
    src_user_identifier = models.CharField(
        max_length=128, null=True, blank=True, help_text="User ID from query source"
    )
    src_user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User that triggered the query, if local source",
    )

    var_release = models.CharField(max_length=64, help_text="Query variant genome release")
    var_chrom = models.CharField(max_length=64, help_text="Query variant chromosome")
    var_start = models.IntegerField(help_text="Query variant 1-based start position")
    var_end = models.IntegerField(help_text="Query variant 1-based end position")
    var_reference = models.TextField(help_text="Query variant reference allele string")
    var_alternative = models.TextField(help_text="Query variant alternative allele tring")


class Response(models.Model):
    """Store information about a response."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )

    query = models.ForeignKey(
        Query, help_text="The query that this response is for", on_delete=models.CASCADE
    )
    http_header = models.TextField(null=False, help_text="HTTP request header content")
    http_body = models.TextField(null=True, blank=True, help_text="HTTP request body content")
