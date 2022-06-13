import random
import typing

import attrs
from bgjobs.models import BackgroundJob
from test_plus.test import TestCase

from svs import bg_db
from django.contrib.auth import get_user_model

#: The User model to use.
from svs.models import BuildBackgroundSvSetJob, BackgroundSvSet, BackgroundSv

User = get_user_model()

from svs.tests.factories import StructuralVariantFactory


class TestSvTypes(TestCase):
    def testSmokeTest(self):
        self.assertIn("DEL", bg_db.SV_TYPES)


class TestClusterAlgoParams(TestCase):
    def testConstructionDefaultValues(self):
        params = bg_db.ClusterAlgoParams()
        self.assertEqual(
            str(params),
            "ClusterAlgoParams(seed=42, cluster_max_size=500, cluster_size_sample_to=100, "
            "min_jaccard_overlap=0.7, bnd_slack=50)",
        )


class TestFileNamSafe(TestCase):
    def testSimple(self):
        self.assertEqual(bg_db._file_name_safe("This is a string /"), "This_is_a_string__")


class TestPairedEndOrientation(TestCase):
    def testValues(self):
        self.assertEqual(bg_db.PairedEndOrientation.FIVE_TO_THREE.value, "5to3")
        self.assertEqual(bg_db.PairedEndOrientation.THREE_TO_FIVE.value, "3to5")
        self.assertEqual(bg_db.PairedEndOrientation.THREE_TO_THREE.value, "3to3")
        self.assertEqual(bg_db.PairedEndOrientation.FIVE_TO_FIVE.value, "5to5")


class TestSvRecord(TestCase):
    def setUp(self):
        self.maxDiff = None

    def testConstruction(self):
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=123,
            chrom2="7",
            end=456,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
            counts=bg_db.GenotypeCounts(src_count=1, carriers=1, carriers_het=1),
        )
        self.assertEqual(
            str(record),
            "SvRecord(release='GRCh37', sv_type='DEL', chrom='7', pos=123, chrom2='7', "
            "end=456, orientation=<PairedEndOrientation.THREE_TO_FIVE: '3to5'>, "
            "counts=GenotypeCounts(src_count=1, carriers=1, carriers_het=1, carriers_hom=0, carriers_hemi=0))",
        )

    def testJaccardIndex(self):
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=1001,
            chrom2="7",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        with self.assertRaises(ValueError):
            record.jaccard_index(attrs.evolve(record, release="GRCh38"))
        with self.assertRaises(ValueError):
            record.jaccard_index(attrs.evolve(record, sv_type="DUP"))
        self.assertAlmostEqual(
            record.jaccard_index(attrs.evolve(record, chrom="8", chrom2="8")), 0.0
        )
        self.assertAlmostEqual(record.jaccard_index(record), 1.0, delta=1e-7)
        self.assertAlmostEqual(
            record.jaccard_index(attrs.evolve(record, pos=501, end=1500)), 0.333, delta=0.001
        )

    def testIsCompatibleDel(self):
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=1001,
            chrom2="7",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_good = attrs.evolve(record, pos=2000, end=2001)
        record_bad = attrs.evolve(record, pos=2001, end=2001)
        self.assertTrue(record.is_compatible(record_good, bnd_slack=50))
        self.assertFalse(record.is_compatible(record_bad, bnd_slack=50))

    def testIsCompatibleBnd(self):
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="BND",
            chrom="7",
            pos=1000,
            chrom2="9",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_good_1 = attrs.evolve(record, pos=1000, end=2050)
        record_good_2 = attrs.evolve(record, pos=1050, end=2050)
        record_bad_1 = attrs.evolve(record, orientation=bg_db.PairedEndOrientation.THREE_TO_THREE)
        record_bad_2 = attrs.evolve(record, pos=1052)
        record_bad_3 = attrs.evolve(record, end=2052)
        self.assertTrue(record.is_compatible(record_good_1, bnd_slack=50))
        self.assertTrue(record.is_compatible(record_good_2, bnd_slack=50))
        self.assertFalse(record.is_compatible(record_bad_1, bnd_slack=50))
        self.assertFalse(record.is_compatible(record_bad_2, bnd_slack=50))
        self.assertFalse(record.is_compatible(record_bad_3, bnd_slack=50))


class TestSvClusterWithDel(TestCase):
    def setUp(self):
        self.params = bg_db.ClusterAlgoParams(cluster_max_size=5, cluster_size_sample_to=3)
        self.rng = random.Random(self.params.seed)
        self.maxDiff = None

    def testConstruction(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        self.maxDiff = None
        self.assertEqual(
            str(cluster),
            "SvCluster(params=ClusterAlgoParams(seed=42, cluster_max_size=5, cluster_size_sample_to=3, "
            "min_jaccard_overlap=0.7, bnd_slack=50), mean=None, records=[], "
            "counts=GenotypeCounts(src_count=0, carriers=0, carriers_het=0, carriers_hom=0, carriers_hemi=0))",
        )

    def testAugmentOnce(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=1001,
            chrom2="7",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
            counts=bg_db.GenotypeCounts(src_count=1, carriers=1, carriers_het=1),
        )
        cluster.augment(record)
        self.assertEqual(
            str(cluster.mean),
            "SvRecord(release='GRCh37', sv_type='DEL', chrom='7', pos=1001, "
            "chrom2='7', end=2000, orientation=<PairedEndOrientation.THREE_TO_FIVE: '3to5'>, "
            "counts=GenotypeCounts(src_count=1, carriers=1, carriers_het=1, carriers_hom=0, carriers_hemi=0))",
        )
        self.assertEqual(len(cluster.records), 1)

    def testAugmentTwice(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=1001,
            chrom2="7",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
            counts=bg_db.GenotypeCounts(src_count=1, carriers=1, carriers_het=1),
        )
        cluster.augment(record)
        cluster.augment(attrs.evolve(record, pos=1501, end=2500))
        self.assertEqual(
            str(cluster.mean),
            "SvRecord(release='GRCh37', sv_type='DEL', chrom='7', pos=1251, "
            "chrom2='7', end=2250, orientation=<PairedEndOrientation.THREE_TO_FIVE: '3to5'>, "
            "counts=GenotypeCounts(src_count=1, carriers=1, carriers_het=1, carriers_hom=0, carriers_hemi=0))",
        )
        self.assertEqual(
            cluster.counts, bg_db.GenotypeCounts(src_count=2, carriers=2, carriers_het=2)
        )
        self.assertEqual(len(cluster.records), 2)


class TestSvClusterWithBnd(TestCase):
    def setUp(self):
        self.params = bg_db.ClusterAlgoParams(cluster_max_size=5, cluster_size_sample_to=3)
        self.rng = random.Random(self.params.seed)
        self.maxDiff = None

    def testAugmentTwiceCompatible(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="BND",
            chrom="7",
            pos=1001,
            chrom2="9",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
            counts=bg_db.GenotypeCounts(src_count=1, carriers=1, carriers_het=1),
        )
        cluster.augment(record)
        cluster.augment(attrs.evolve(record, pos=record.pos + 50, end=record.end + 50))
        self.assertEqual(
            str(cluster.mean),
            "SvRecord(release='GRCh37', sv_type='BND', chrom='7', pos=1026, "
            "chrom2='9', end=2025, orientation=<PairedEndOrientation.THREE_TO_FIVE: '3to5'>, "
            "counts=GenotypeCounts(src_count=1, carriers=1, carriers_het=1, carriers_hom=0, carriers_hemi=0))",
        )
        self.assertEqual(len(cluster.records), 2)
        self.assertEqual(
            str(cluster.counts),
            "GenotypeCounts(src_count=2, carriers=2, carriers_het=2, carriers_hom=0, carriers_hemi=0)",
        )

    def testAugmentTwinceIncompatible(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="BND",
            chrom="7",
            pos=1001,
            chrom2="9",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_THREE,
        )
        cluster.augment(record)
        with self.assertRaises(ValueError):
            cluster.augment(attrs.evolve(record, pos=record.pos + 51, end=record.end + 51))
        self.assertEqual(len(cluster.records), 1)


class TestClusterSvAlgorithm(TestCase):
    def setUp(self):
        self.maxDiff = None

    def testConstruction(self):
        _algo = bg_db.ClusterSvAlgorithm(bg_db.ClusterAlgoParams())

    def _run_clustering(
        self, by_chrom: typing.Dict[str, typing.List[bg_db.SvRecord]]
    ) -> typing.Dict[str, typing.List[bg_db.SvCluster]]:
        result = {}
        algo = bg_db.ClusterSvAlgorithm(bg_db.ClusterAlgoParams())
        for chrom, chrom_records in by_chrom.items():
            with algo.on_chrom(chrom):
                for record in chrom_records:
                    algo.push(record)
                result[chrom] = list(map(bg_db.SvCluster.normalized, algo.cluster()))
        return algo, result

    def testWithNoVariant(self):
        records = {}
        _algo, clusters = self._run_clustering(records)
        self.assertEqual(clusters, {})

    def testWithSingleChromSingleVar(self):
        record_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1000,
            chrom2="chr1",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        records = {
            "chr1": [record_1],
        }
        algo, clusters = self._run_clustering(records)
        expected = {
            "chr1": [
                bg_db.SvCluster(
                    params=algo.params, rng=algo.rng, mean=record_1, records=[record_1],
                )
            ]
        }
        self.assertEqual(clusters, expected)

    def testWithSingleChromMultipleVariants(self):
        record_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1000,
            chrom2="chr1",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_2 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1500,
            chrom2="chr1",
            end=2500,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        mean_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1250,
            chrom2="chr1",
            end=2250,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        records = {"chr1": [record_1, record_2,]}
        algo, clusters = self._run_clustering(records)
        expected = {
            "chr1": [
                bg_db.SvCluster(
                    params=algo.params, rng=algo.rng, mean=mean_1, records=[record_1, record_2]
                )
            ],
        }
        self.assertEqual(clusters, expected)

    def testWithTwoChromsSingleVar(self):
        record_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1000,
            chrom2="chr1",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_2 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr2",
            pos=1000,
            chrom2="chr2",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        records = {
            "chr1": [record_1,],
            "chr2": [record_2,],
        }
        algo, clusters = self._run_clustering(records)
        expected = {
            "chr1": [
                bg_db.SvCluster(params=algo.params, rng=algo.rng, mean=record_1, records=[record_1])
            ],
            "chr2": [
                bg_db.SvCluster(params=algo.params, rng=algo.rng, mean=record_2, records=[record_2])
            ],
        }
        self.assertEqual(clusters, expected)

    def testWithTwoChromsMultipleVariants(self):
        record_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1000,
            chrom2="chr1",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_2 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1500,
            chrom2="chr1",
            end=2500,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_3 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr2",
            pos=1000,
            chrom2="chr2",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_4 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr2",
            pos=1500,
            chrom2="chr2",
            end=2500,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        mean_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr1",
            pos=1250,
            chrom2="chr1",
            end=2250,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        mean_2 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="chr2",
            pos=1250,
            chrom2="chr2",
            end=2250,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        records = {
            "chr1": [record_1, record_2,],
            "chr2": [record_3, record_4,],
        }
        algo, clusters = self._run_clustering(records)
        expected = {
            "chr1": [
                bg_db.SvCluster(
                    params=algo.params, rng=algo.rng, mean=mean_1, records=[record_1, record_2]
                )
            ],
            "chr2": [
                bg_db.SvCluster(
                    params=algo.params, rng=algo.rng, mean=mean_2, records=[record_3, record_4]
                )
            ],
        }
        self.assertEqual(clusters, expected)

    def testWithBreakend(self):
        record_1 = bg_db.SvRecord(
            release="GRCh37",
            sv_type="BND",
            chrom="chr1",
            pos=1000,
            chrom2="chr2",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        record_2 = attrs.evolve(
            record_1, pos=1001, orientation=bg_db.PairedEndOrientation.THREE_TO_THREE,
        )
        record_3 = attrs.evolve(record_1, end=record_1.end + 1)
        mean_1 = attrs.evolve(record_1, end=record_1.end + 1)
        mean_2 = record_2
        records = {"chr1": [record_1, record_2, record_3]}
        algo, clusters = self._run_clustering(records)
        expected = {
            "chr1": [
                bg_db.SvCluster(
                    params=algo.params, rng=algo.rng, mean=mean_1, records=[record_1, record_3]
                ),
                bg_db.SvCluster(params=algo.params, rng=algo.rng, mean=mean_2, records=[record_2]),
            ],
        }
        self.assertEqual(clusters, expected)


class TestModelToAttrs(TestCase):
    def testWithDel(self):
        sv_model = StructuralVariantFactory(chromosome="3", chromosome_no=3, start=1000, end=2000,)
        sv_record = bg_db.sv_model_to_attrs(sv_model)
        self.maxDiff = None
        expected = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="3",
            pos=1000,
            chrom2="3",
            end=2000,
            orientation="3to5",
            counts=bg_db.GenotypeCounts(
                src_count=1, carriers=1, carriers_het=1, carriers_hom=0, carriers_hemi=0
            ),
        )
        self.assertEqual(expected, sv_record)


class TestSvClusterToModelArgs(TestCase):
    def setUp(self):
        self.params = bg_db.ClusterAlgoParams(cluster_max_size=5, cluster_size_sample_to=3)
        self.rng = random.Random(self.params.seed)
        self.maxDiff = None

    def testWithDel(self):
        cluster = bg_db.SvCluster(params=self.params, rng=self.rng)
        record = bg_db.SvRecord(
            release="GRCh37",
            sv_type="DEL",
            chrom="7",
            pos=1001,
            chrom2="7",
            end=2000,
            orientation=bg_db.PairedEndOrientation.THREE_TO_FIVE,
        )
        cluster.augment(record)
        expected = {
            "bin": 585,
            "carriers": 0,
            "carriers_hemi": 0,
            "carriers_het": 0,
            "carriers_hom": 0,
            "chromosome": "7",
            "chromosome2": "7",
            "chromosome_no": 7,
            "chromosome_no2": 7,
            "end": 2000,
            "pe_orientation": "3to5",
            "release": "GRCh37",
            "src_count": 0,
            "start": 1001,
            "sv_type": "DEL",
        }
        self.assertEqual(expected, bg_db.sv_cluster_to_model_args(cluster))


class TestBuildBgSvSet(TestCase):
    def setUp(self):
        super().setUp()
        self.root_user = User.objects.create(username="root", is_superuser=True)
        self.bg_job = BackgroundJob.objects.create(
            name="job name",
            project=None,
            job_type="variants.export_file_bg_job",
            user=self.root_user,
        )
        self.build_sv_set_bg_job = BuildBackgroundSvSetJob.objects.create(bg_job=self.bg_job,)

    def testWithNoRecords(self):
        self.assertEqual(BackgroundSvSet.objects.count(), 0)
        self.assertEqual(BackgroundSv.objects.count(), 0)
        bg_db.build_bg_sv_set(self.build_sv_set_bg_job)
        self.assertEqual(BackgroundSvSet.objects.count(), 1)
        self.assertEqual(BackgroundSv.objects.count(), 0)

    def testWithTwoChromsSingleRecords(self):
        _vars = [
            StructuralVariantFactory(chromosome="1", chromosome_no=1, start=10_000, end=20_000),
            StructuralVariantFactory(chromosome="2", chromosome_no=2, start=10_000, end=20_000),
        ]
        self.assertEqual(BackgroundSvSet.objects.count(), 0)
        self.assertEqual(BackgroundSv.objects.count(), 0)
        bg_db.build_bg_sv_set(self.build_sv_set_bg_job)
        self.assertEqual(BackgroundSvSet.objects.count(), 1)
        self.assertEqual(BackgroundSv.objects.count(), 2)

    def testWithTwoChromsTwoRecordsEach(self):
        _vars = [
            StructuralVariantFactory(chromosome="1", chromosome_no=1, start=10_000, end=20_000),
            StructuralVariantFactory(chromosome="2", chromosome_no=2, start=10_000, end=20_000),
            StructuralVariantFactory(chromosome="1", chromosome_no=1, start=10_001, end=20_001),
            StructuralVariantFactory(chromosome="2", chromosome_no=2, start=10_001, end=20_001),
        ]
        self.assertEqual(BackgroundSvSet.objects.count(), 0)
        self.assertEqual(BackgroundSv.objects.count(), 0)
        bg_db.build_bg_sv_set(self.build_sv_set_bg_job)
        self.assertEqual(BackgroundSvSet.objects.count(), 1)
        self.assertEqual(BackgroundSv.objects.count(), 2)
