# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["SamtoolsLoadSamtoolsFlagstatTest::test_load 1"] = [
    "_state",
    "id",
    "sodar_uuid",
    "date_created",
    "date_modified",
    "caseqc_id",
    "sample",
    "qc_pass",
    "qc_fail",
]

snapshots["SamtoolsLoadSamtoolsFlagstatTest::test_load 2"] = {
    "qc_fail": GenericRepr(
        "SamtoolsFlagstatRecord(total=0, primary=0, secondary=0, supplementary=0, duplicates=0, duplicates_primary=0, mapped=0, mapped_primary=0, paired=0, fragment_first=0, fragment_last=0, properly_paired=0, with_itself_and_mate_mapped=0, singletons=0, with_mate_mapped_to_different_chr=0, with_mate_mapped_to_different_chr_mapq5=0)"
    ),
    "qc_pass": GenericRepr(
        "SamtoolsFlagstatRecord(total=885644887, primary=883629530, secondary=0, supplementary=2015357, duplicates=251067634, duplicates_primary=250647696, mapped=884708201, mapped_primary=882692844, paired=883629530, fragment_first=441814765, fragment_last=441814765, properly_paired=870504652, with_itself_and_mate_mapped=881815192, singletons=877652, with_mate_mapped_to_different_chr=7237436, with_mate_mapped_to_different_chr_mapq5=5217343)"
    ),
    "sample": "NA12878",
}

snapshots["SamtoolsLoadSamtoolsIdxstatsTest::test_load 1"] = [
    "_state",
    "id",
    "sodar_uuid",
    "date_created",
    "date_modified",
    "caseqc_id",
    "sample",
    "records",
]

snapshots["SamtoolsLoadSamtoolsIdxstatsTest::test_load 2"] = {
    "records": [
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='1', contig_len=249250621, mapped=66843086, unmapped=67438)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='2', contig_len=243199373, mapped=70403221, unmapped=70799)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='3', contig_len=198022430, mapped=57186383, unmapped=55741)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='4', contig_len=191154276, mapped=55140091, unmapped=53788)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='5', contig_len=180915260, mapped=52547273, unmapped=51508)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='6', contig_len=171115067, mapped=49433310, unmapped=48535)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='7', contig_len=159138663, mapped=45299238, unmapped=45930)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='8', contig_len=146364022, mapped=42400445, unmapped=41609)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='9', contig_len=141213431, mapped=35382960, unmapped=35779)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='10', contig_len=135534747, mapped=37890638, unmapped=38765)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='11', contig_len=135006516, mapped=38449213, unmapped=38359)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='12', contig_len=133851895, mapped=37923640, unmapped=37681)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='13', contig_len=115169878, mapped=27998172, unmapped=27816)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='14', contig_len=107349540, mapped=25835974, unmapped=25928)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='15', contig_len=102531392, mapped=23685081, unmapped=24045)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='16', contig_len=90354753, mapped=25549021, unmapped=25782)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='17', contig_len=81195210, mapped=22584163, unmapped=23483)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='18', contig_len=78077248, mapped=21966862, unmapped=22136)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='19', contig_len=59128983, mapped=15706370, unmapped=17467)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='20', contig_len=63025520, mapped=17342201, unmapped=18406)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='21', contig_len=48129895, mapped=10753653, unmapped=10960)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='22', contig_len=51304566, mapped=10072154, unmapped=10823)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='X', contig_len=155270560, mapped=43301862, unmapped=44182)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='Y', contig_len=59373566, mapped=190830, unmapped=787)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='MT', contig_len=16569, mapped=2322677, unmapped=3346)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000207.1', contig_len=4262, mapped=1446, unmapped=3)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000226.1', contig_len=15008, mapped=1178460, unmapped=340)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000229.1', contig_len=19913, mapped=10644, unmapped=9)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000231.1', contig_len=27386, mapped=14256, unmapped=11)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000210.1', contig_len=27682, mapped=4043, unmapped=8)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000239.1', contig_len=33824, mapped=25755, unmapped=25)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000235.1', contig_len=34474, mapped=16634, unmapped=12)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000201.1', contig_len=36148, mapped=5263, unmapped=6)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000247.1', contig_len=36422, mapped=13345, unmapped=16)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000245.1', contig_len=36651, mapped=18793, unmapped=15)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000197.1', contig_len=37175, mapped=5153, unmapped=14)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000203.1', contig_len=37498, mapped=7381, unmapped=8)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000246.1', contig_len=38154, mapped=6446, unmapped=5)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000249.1', contig_len=38502, mapped=5540, unmapped=7)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000196.1', contig_len=38914, mapped=5822, unmapped=2)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000248.1', contig_len=39786, mapped=5437, unmapped=7)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000244.1', contig_len=39929, mapped=11762, unmapped=14)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000238.1', contig_len=39939, mapped=5647, unmapped=4)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000202.1', contig_len=40103, mapped=9085, unmapped=18)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000234.1', contig_len=40531, mapped=22879, unmapped=19)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000232.1', contig_len=40652, mapped=22447, unmapped=29)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000206.1', contig_len=41001, mapped=5459, unmapped=5)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000240.1', contig_len=41933, mapped=12462, unmapped=18)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000236.1', contig_len=41934, mapped=5055, unmapped=8)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000241.1', contig_len=42152, mapped=28213, unmapped=26)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000243.1', contig_len=43341, mapped=18037, unmapped=30)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000242.1', contig_len=43523, mapped=6351, unmapped=11)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000230.1', contig_len=43691, mapped=8341, unmapped=4)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000237.1', contig_len=45867, mapped=42958, unmapped=71)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000233.1', contig_len=45941, mapped=9810, unmapped=5)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000204.1', contig_len=81310, mapped=19043, unmapped=19)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000198.1', contig_len=90085, mapped=35934, unmapped=21)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000208.1', contig_len=92689, mapped=101668, unmapped=47)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000191.1', contig_len=106433, mapped=16997, unmapped=14)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000227.1', contig_len=128374, mapped=25649, unmapped=38)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000228.1', contig_len=129120, mapped=59001, unmapped=71)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000214.1', contig_len=137718, mapped=193320, unmapped=185)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000221.1', contig_len=155397, mapped=95173, unmapped=83)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000209.1', contig_len=159169, mapped=27312, unmapped=26)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000218.1', contig_len=161147, mapped=141063, unmapped=142)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000220.1', contig_len=161802, mapped=2906260, unmapped=4786)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000213.1', contig_len=164239, mapped=19667, unmapped=23)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000211.1', contig_len=166566, mapped=51319, unmapped=54)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000199.1', contig_len=169874, mapped=438867, unmapped=141)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000217.1', contig_len=172149, mapped=66072, unmapped=92)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000216.1', contig_len=172294, mapped=93277, unmapped=67)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000215.1', contig_len=172545, mapped=22072, unmapped=22)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000205.1', contig_len=174588, mapped=164784, unmapped=138)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000219.1', contig_len=179198, mapped=67991, unmapped=81)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000224.1', contig_len=179693, mapped=235176, unmapped=185)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000223.1', contig_len=180455, mapped=24503, unmapped=45)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000195.1', contig_len=182896, mapped=205619, unmapped=167)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000212.1', contig_len=186858, mapped=46730, unmapped=61)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000222.1', contig_len=186861, mapped=28091, unmapped=24)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000200.1', contig_len=187035, mapped=24680, unmapped=22)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000193.1', contig_len=189789, mapped=113495, unmapped=95)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000194.1', contig_len=191469, mapped=76936, unmapped=73)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000225.1', contig_len=211173, mapped=148238, unmapped=188)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='GL000192.1', contig_len=547496, mapped=153379, unmapped=164)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='NC_007605', contig_len=171823, mapped=3803263, unmapped=5918)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='hs37d5', contig_len=35477943, mapped=37561180, unmapped=22817)"
        ),
        GenericRepr(
            "SamtoolsIdxstatsRecord(contig_name='*', contig_len=0, mapped=0, unmapped=59034)"
        ),
    ],
    "sample": "NA12878",
}
