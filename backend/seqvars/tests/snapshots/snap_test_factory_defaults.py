# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_exome_legacy 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': "Settings for short-read exome sequencing with relaxed quality presets.  These settings are aimed at 'legacy' WES sequencing where a target coverage of >=20x cannot be achieved for a considerable portion of the exome.",
    'label': 'short-read exome sequencing (legacy)',
    'rank': 3,
    'sodar_uuid': '41f60be0-7cef-4aa3-aaed-cf4a4599a084',
    'versions': [
        {
            'date_created': '2024-07-01T00:00:00Z',
            'date_modified': '2024-07-01T00:00:00Z',
            'predefinedquery_set': [
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '7e204ae3-0f53-40fb-a9ca-0d2797d938be',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'defaults',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 1,
                    'sodar_uuid': 'ea342c46-9fc3-46fb-80c1-3ed41a4d7cd8',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '7e204ae3-0f53-40fb-a9ca-0d2797d938be',
                    'genotype': {
                        'choice': 'de_novo'
                    },
                    'included_in_sop': False,
                    'label': 'de novo',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': '1d6608f7-02d3-4789-bbf8-322a12847494',
                    'rank': 2,
                    'sodar_uuid': '9e899ea8-5cbc-4afb-b686-bfc6936f107e',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '7e204ae3-0f53-40fb-a9ca-0d2797d938be',
                    'genotype': {
                        'choice': 'dominant'
                    },
                    'included_in_sop': False,
                    'label': 'dominant',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 3,
                    'sodar_uuid': '33531265-706a-466b-b476-0fd747426582',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'c9e201c1-a058-4cb8-a7ec-999359f1a611',
                    'genotype': {
                        'choice': 'homozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'homozygous recessive',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 4,
                    'sodar_uuid': '3e08cc52-f8ba-4342-854d-2a8d54507252',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'c9e201c1-a058-4cb8-a7ec-999359f1a611',
                    'genotype': {
                        'choice': 'compound_heterozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'compound heterozygous',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 5,
                    'sodar_uuid': 'f40bbc3d-84c3-4b5d-a0a7-d0b5a51cb882',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'c9e201c1-a058-4cb8-a7ec-999359f1a611',
                    'genotype': {
                        'choice': 'recessive'
                    },
                    'included_in_sop': False,
                    'label': 'recessive',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 6,
                    'sodar_uuid': '0714675c-7e68-43fa-b99e-70e1a9cbb433',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'c9e201c1-a058-4cb8-a7ec-999359f1a611',
                    'genotype': {
                        'choice': 'x_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'X recessive',
                    'locus': 'ef516257-e057-4c68-b2fd-a54c6303c86d',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 7,
                    'sodar_uuid': '98fcb9c1-05cf-4de9-bdfe-e571260ffb1d',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '2b0bd6c1-4d04-43b3-9178-7e4649d8beda',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': 'e565da21-cb89-49f7-8586-9e992290176e',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '35bd1a58-4b35-42ba-ac8c-f78b9f9565c0',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'ClinVar pathogenic',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': '110edc17-9ffb-4863-a62d-3f4c09274947',
                    'rank': 8,
                    'sodar_uuid': '7ac6f3ba-d824-4a03-833f-24a2f854909b',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': 'e565da21-cb89-49f7-8586-9e992290176e',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '7e204ae3-0f53-40fb-a9ca-0d2797d938be',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'mitochondrial',
                    'locus': '9ef59cf2-bb67-4969-a1ce-ffb5de1e716f',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3',
                    'rank': 9,
                    'sodar_uuid': '36e35e78-9c55-4fc2-acc3-2b791857767d',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                },
                {
                    'clinvar': '8b13d606-dbd0-4158-9fcf-0a28076cb2db',
                    'columns': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2',
                    'consequence': 'e565da21-cb89-49f7-8586-9e992290176e',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '35bd1a58-4b35-42ba-ac8c-f78b9f9565c0',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'whole genome',
                    'locus': '5b461bc0-407a-47c2-9217-39ea2c160877',
                    'phenotypeprio': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'quality': '110edc17-9ffb-4863-a62d-3f4c09274947',
                    'rank': 10,
                    'sodar_uuid': '1774622e-e4ee-4fee-9023-a0fec8fabc41',
                    'variantprio': '8deb93bd-7499-411a-9598-827324b80cdb'
                }
            ],
            'presetsset': {
                'date_created': '2024-07-01T00:00:00Z',
                'date_modified': '2024-07-01T00:00:00Z',
                'description': "Settings for short-read exome sequencing with relaxed quality presets.  These settings are aimed at 'legacy' WES sequencing where a target coverage of >=20x cannot be achieved for a considerable portion of the exome.",
                'label': 'short-read exome sequencing (legacy)',
                'rank': 3,
                'sodar_uuid': '41f60be0-7cef-4aa3-aaed-cf4a4599a084'
            },
            'querypresetsclinvar_set': [
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                    ],
                    'clinvar_presence_required': False,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': '8b13d606-dbd0-4158-9fcf-0a28076cb2db'
                },
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'sodar_uuid': 'c5888aed-8542-43ff-a15a-375da886b6a8'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP +conflicting',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'sodar_uuid': '2b0bd6c1-4d04-43b3-9178-7e4649d8beda'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic',
                        'uncertain_significance'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'ClinVar P/LP/VUS +conflicting',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 4,
                    'sodar_uuid': '478e2c06-9f45-4a49-8291-d9fa2ed08d07'
                }
            ],
            'querypresetscolumns_set': [
                {
                    'column_settings': [
                    ],
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'defaults',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': 'de09623d-f1df-4cea-a6b7-c6720cbd2ff2'
                }
            ],
            'querypresetsconsequence_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'any',
                    'max_distance_to_exon': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': 'e565da21-cb89-49f7-8586-9e992290176e',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'downstream_gene_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        'upstream_gene_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'null variant',
                    'max_distance_to_exon': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'sodar_uuid': 'fe19dbb5-3604-4542-a774-9d9fbca9e904',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'AA change + splicing',
                    'max_distance_to_exon': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'sodar_uuid': '6daacf24-b7a1-45ef-82bf-468ad91b8be9',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'all coding + deep intronic',
                    'max_distance_to_exon': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 4,
                    'sodar_uuid': '248ee65a-687b-4c7a-9ce8-2c7013300288',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'coding_sequence_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'whole transcript',
                    'max_distance_to_exon': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 5,
                    'sodar_uuid': '083c2879-ec46-4de3-8ea4-3d37b350c341',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                }
            ],
            'querypresetsfrequency_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 1,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant super strict',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': '4118a8cb-a4ac-4410-b3c3-3479cf6c7895'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 20,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 4,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant strict',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'sodar_uuid': '7e204ae3-0f53-40fb-a9ca-0d2797d938be'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 50,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 20,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': 0.15,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': 400,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant relaxed',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'sodar_uuid': '35acdddf-e969-43c4-9fa9-7fe2e8dc4e64'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.001,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 120,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.001,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 15,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive strict',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 4,
                    'sodar_uuid': 'c9e201c1-a058-4cb8-a7ec-999359f1a611'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1200,
                    'gnomad_exomes_homozygous': 20,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 150,
                    'gnomad_genomes_homozygous': 4,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive relaxed',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 5,
                    'sodar_uuid': 'b626ec8c-7ffd-4292-bfea-718f04537ef1'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': False,
                    'gnomad_exomes_frequency': None,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': None,
                    'gnomad_exomes_homozygous': None,
                    'gnomad_genomes_enabled': False,
                    'gnomad_genomes_frequency': None,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': None,
                    'gnomad_genomes_homozygous': None,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': None,
                    'inhouse_enabled': False,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'any',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 6,
                    'sodar_uuid': '35bd1a58-4b35-42ba-ac8c-f78b9f9565c0'
                }
            ],
            'querypresetslocus_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                    ],
                    'label': 'whole genome',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': '5b461bc0-407a-47c2-9217-39ea2c160877'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        },
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'nuclear chromosomes',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'sodar_uuid': '51ecae94-f671-4124-b9a6-3c39c66c7e86'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        }
                    ],
                    'label': 'autosomes',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'sodar_uuid': '056f89f8-16fe-4c7a-a951-40eb18004d45'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'gonosomes',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 4,
                    'sodar_uuid': 'c8acb3b0-5126-462c-9418-f039c04d4ade'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        }
                    ],
                    'label': 'X chromosome',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 5,
                    'sodar_uuid': 'ef516257-e057-4c68-b2fd-a54c6303c86d'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'Y chromosome',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 6,
                    'sodar_uuid': '8970646a-a924-4ed3-87d8-1695beecb78c'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'MT',
                            'range': None
                        }
                    ],
                    'label': 'MT genome',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 7,
                    'sodar_uuid': '9ef59cf2-bb67-4969-a1ce-ffb5de1e716f'
                }
            ],
            'querypresetsphenotypeprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'phenotype_prio_algorithm': 'exomiser.hiphive_human',
                    'phenotype_prio_enabled': False,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': '6149778e-d5df-4ca5-a299-e56a6a1c79ff',
                    'terms': [
                    ]
                }
            ],
            'querypresetsquality_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'super strict',
                    'max_ad': None,
                    'min_ab_het': 0.3,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 30,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'sodar_uuid': '1d6608f7-02d3-4789-bbf8-322a12847494'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'strict',
                    'max_ad': None,
                    'min_ab_het': 0.2,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 10,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'sodar_uuid': 'f4d26f48-1e22-410b-8ec2-d5ef48aa69a3'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'relaxed',
                    'max_ad': None,
                    'min_ab_het': 0.1,
                    'min_ad': 2,
                    'min_dp_het': 8,
                    'min_dp_hom': 4,
                    'min_gq': 10,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'sodar_uuid': 'a638caa5-be54-4a11-9afc-cd9f4fa0336c'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': False,
                    'label': 'any',
                    'max_ad': None,
                    'min_ab_het': None,
                    'min_ad': None,
                    'min_dp_het': None,
                    'min_dp_hom': None,
                    'min_gq': None,
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 4,
                    'sodar_uuid': '110edc17-9ffb-4863-a62d-3f4c09274947'
                }
            ],
            'querypresetsvariantprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 1,
                    'services': [
                    ],
                    'sodar_uuid': '8deb93bd-7499-411a-9598-827324b80cdb',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'CADD',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 2,
                    'services': [
                        {
                            'name': 'cadd',
                            'version': '1.6'
                        }
                    ],
                    'sodar_uuid': '0fd5b1ec-6269-4532-8f65-8323161c7b0c',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'MutationTaster',
                    'presetssetversion': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
                    'rank': 3,
                    'services': [
                        {
                            'name': 'mutationtaster',
                            'version': '2021'
                        }
                    ],
                    'sodar_uuid': 'e71a640f-9cc9-4f9d-83e1-82eee1ed1749',
                    'variant_prio_enabled': False
                }
            ],
            'signed_off_by': None,
            'sodar_uuid': '0587212a-56b7-4cfe-8d9d-ff9714f60b7a',
            'status': 'active',
            'version_major': 1,
            'version_minor': 0
        }
    ]
}

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_exome_modern 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': "Settings for short-read exome sequencing with strict quality presets.  These settings are aimed at 'modern' WES sequencing where a target coverage of >=20x can be achieved for >=99% of the exome.",
    'label': 'short-read exome sequencing (modern)',
    'rank': 2,
    'sodar_uuid': 'b39cfd4b-8abe-4d78-8520-10116895cea8',
    'versions': [
        {
            'date_created': '2024-07-01T00:00:00Z',
            'date_modified': '2024-07-01T00:00:00Z',
            'predefinedquery_set': [
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd82e3ed6-bcaf-4c20-b1d8-fbc7b6ad2d73',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'defaults',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 1,
                    'sodar_uuid': 'ffb91fd8-0f2c-4bfc-b779-e1eb9b527636',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd82e3ed6-bcaf-4c20-b1d8-fbc7b6ad2d73',
                    'genotype': {
                        'choice': 'de_novo'
                    },
                    'included_in_sop': False,
                    'label': 'de novo',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '39850d17-0772-4aea-8a21-229039a40dfe',
                    'rank': 2,
                    'sodar_uuid': 'ad05a008-0c48-4695-82be-277b6ee870af',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd82e3ed6-bcaf-4c20-b1d8-fbc7b6ad2d73',
                    'genotype': {
                        'choice': 'dominant'
                    },
                    'included_in_sop': False,
                    'label': 'dominant',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 3,
                    'sodar_uuid': '2486d632-1f5b-4a1a-b954-7b1e9f82af07',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '74211244-a16c-4327-b88b-78bdd49a72b4',
                    'genotype': {
                        'choice': 'homozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'homozygous recessive',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 4,
                    'sodar_uuid': 'bc333ff0-a477-41d4-aeb9-07252defcb3a',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '74211244-a16c-4327-b88b-78bdd49a72b4',
                    'genotype': {
                        'choice': 'compound_heterozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'compound heterozygous',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 5,
                    'sodar_uuid': 'a64108e7-9ea0-4917-8161-afd8d5e6ece5',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '74211244-a16c-4327-b88b-78bdd49a72b4',
                    'genotype': {
                        'choice': 'recessive'
                    },
                    'included_in_sop': False,
                    'label': 'recessive',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 6,
                    'sodar_uuid': '1024b6d5-a533-4e83-abc9-d0834b2fd3fb',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '74211244-a16c-4327-b88b-78bdd49a72b4',
                    'genotype': {
                        'choice': 'x_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'X recessive',
                    'locus': 'bf4302b2-4223-453b-a14a-79023047a452',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 7,
                    'sodar_uuid': '6f6c866b-01b9-49d2-930e-16c145a5027c',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '90401dcc-5b4f-4f2c-b1c4-1106fea2658c',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': 'c41edca6-67b1-4551-974b-975360e09044',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'fe56b1e5-74a0-4625-bbc3-6d973bb70669',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'ClinVar pathogenic',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': 'a24eb80d-b189-4370-8d90-437bfd4f6854',
                    'rank': 8,
                    'sodar_uuid': '86113d33-b030-491d-adab-5aaf461f1f40',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': 'c41edca6-67b1-4551-974b-975360e09044',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd82e3ed6-bcaf-4c20-b1d8-fbc7b6ad2d73',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'mitochondrial',
                    'locus': 'ae0b60fd-d113-4b9a-b5e8-04cfac78b489',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': '19a56746-0241-45e4-9195-9d9d1ddccf2d',
                    'rank': 9,
                    'sodar_uuid': 'dba947cb-3150-4e85-ada0-9b93a060af85',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                },
                {
                    'clinvar': '9a949347-c0e2-4124-947d-605303bc1158',
                    'columns': '394aa1da-d68a-4f2d-9cc2-5c505712caa6',
                    'consequence': 'c41edca6-67b1-4551-974b-975360e09044',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'fe56b1e5-74a0-4625-bbc3-6d973bb70669',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'whole genome',
                    'locus': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b',
                    'phenotypeprio': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'quality': 'a24eb80d-b189-4370-8d90-437bfd4f6854',
                    'rank': 10,
                    'sodar_uuid': '0f8f7bdb-d4a7-463b-baa2-ac82d733291e',
                    'variantprio': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282'
                }
            ],
            'presetsset': {
                'date_created': '2024-07-01T00:00:00Z',
                'date_modified': '2024-07-01T00:00:00Z',
                'description': "Settings for short-read exome sequencing with strict quality presets.  These settings are aimed at 'modern' WES sequencing where a target coverage of >=20x can be achieved for >=99% of the exome.",
                'label': 'short-read exome sequencing (modern)',
                'rank': 2,
                'sodar_uuid': 'b39cfd4b-8abe-4d78-8520-10116895cea8'
            },
            'querypresetsclinvar_set': [
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                    ],
                    'clinvar_presence_required': False,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': '9a949347-c0e2-4124-947d-605303bc1158'
                },
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'sodar_uuid': '481ffa49-8b0f-441e-8e55-e385a5940e13'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP +conflicting',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'sodar_uuid': '90401dcc-5b4f-4f2c-b1c4-1106fea2658c'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic',
                        'uncertain_significance'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'ClinVar P/LP/VUS +conflicting',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 4,
                    'sodar_uuid': '5c66c458-1c8c-457b-a78f-5a8532f4bdb0'
                }
            ],
            'querypresetscolumns_set': [
                {
                    'column_settings': [
                    ],
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'defaults',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': '394aa1da-d68a-4f2d-9cc2-5c505712caa6'
                }
            ],
            'querypresetsconsequence_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'any',
                    'max_distance_to_exon': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': 'c41edca6-67b1-4551-974b-975360e09044',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'downstream_gene_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        'upstream_gene_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'null variant',
                    'max_distance_to_exon': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'sodar_uuid': '5bb88633-537c-4792-ab87-55c5b0f9aafc',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'AA change + splicing',
                    'max_distance_to_exon': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'sodar_uuid': '4860f7d0-d76e-4b6f-96bc-f77c12d465da',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'all coding + deep intronic',
                    'max_distance_to_exon': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 4,
                    'sodar_uuid': '82d1d170-1cac-4d0b-a8b7-65989e022098',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'coding_sequence_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'whole transcript',
                    'max_distance_to_exon': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 5,
                    'sodar_uuid': '451ed237-1839-42d2-96af-b86411efe3fd',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                }
            ],
            'querypresetsfrequency_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 1,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant super strict',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': 'bd15349c-09af-4530-b5b9-80156fb59ea3'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 20,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 4,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant strict',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'sodar_uuid': 'd82e3ed6-bcaf-4c20-b1d8-fbc7b6ad2d73'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 50,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 20,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': 0.15,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': 400,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant relaxed',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'sodar_uuid': '5e9879ff-5422-47bb-8fbe-5628a7483d73'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.001,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 120,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.001,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 15,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive strict',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 4,
                    'sodar_uuid': '74211244-a16c-4327-b88b-78bdd49a72b4'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1200,
                    'gnomad_exomes_homozygous': 20,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 150,
                    'gnomad_genomes_homozygous': 4,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive relaxed',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 5,
                    'sodar_uuid': '268cdc62-8a60-4252-8d4d-6762970882be'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': False,
                    'gnomad_exomes_frequency': None,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': None,
                    'gnomad_exomes_homozygous': None,
                    'gnomad_genomes_enabled': False,
                    'gnomad_genomes_frequency': None,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': None,
                    'gnomad_genomes_homozygous': None,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': None,
                    'inhouse_enabled': False,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'any',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 6,
                    'sodar_uuid': 'fe56b1e5-74a0-4625-bbc3-6d973bb70669'
                }
            ],
            'querypresetslocus_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                    ],
                    'label': 'whole genome',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': 'f1702cde-1b93-4513-90bf-eb96f57bfe7b'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        },
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'nuclear chromosomes',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'sodar_uuid': '4a2a3e41-f835-4314-9263-3d6da014c5d4'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        }
                    ],
                    'label': 'autosomes',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'sodar_uuid': '18873255-62c8-44c1-9834-7f9608f5fa74'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'gonosomes',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 4,
                    'sodar_uuid': '30c9e507-eab9-4480-b9e2-1d297a2f15f0'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        }
                    ],
                    'label': 'X chromosome',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 5,
                    'sodar_uuid': 'bf4302b2-4223-453b-a14a-79023047a452'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'Y chromosome',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 6,
                    'sodar_uuid': '0b1f331b-0c98-4e86-86cc-ac693f7a9c53'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'MT',
                            'range': None
                        }
                    ],
                    'label': 'MT genome',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 7,
                    'sodar_uuid': 'ae0b60fd-d113-4b9a-b5e8-04cfac78b489'
                }
            ],
            'querypresetsphenotypeprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'phenotype_prio_algorithm': 'exomiser.hiphive_human',
                    'phenotype_prio_enabled': False,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': 'feb9a31c-af0a-46c8-bc93-5110cb477e85',
                    'terms': [
                    ]
                }
            ],
            'querypresetsquality_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'super strict',
                    'max_ad': None,
                    'min_ab_het': 0.3,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 30,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'sodar_uuid': '39850d17-0772-4aea-8a21-229039a40dfe'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'strict',
                    'max_ad': None,
                    'min_ab_het': 0.2,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 10,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'sodar_uuid': '19a56746-0241-45e4-9195-9d9d1ddccf2d'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'relaxed',
                    'max_ad': None,
                    'min_ab_het': 0.1,
                    'min_ad': 2,
                    'min_dp_het': 8,
                    'min_dp_hom': 4,
                    'min_gq': 10,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'sodar_uuid': 'b0567812-8382-456e-8642-35eb281cdb93'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': False,
                    'label': 'any',
                    'max_ad': None,
                    'min_ab_het': None,
                    'min_ad': None,
                    'min_dp_het': None,
                    'min_dp_hom': None,
                    'min_gq': None,
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 4,
                    'sodar_uuid': 'a24eb80d-b189-4370-8d90-437bfd4f6854'
                }
            ],
            'querypresetsvariantprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 1,
                    'services': [
                    ],
                    'sodar_uuid': 'f92d470b-d1d2-484c-9dc2-b5d1588d6282',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'CADD',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 2,
                    'services': [
                        {
                            'name': 'cadd',
                            'version': '1.6'
                        }
                    ],
                    'sodar_uuid': '47290348-0b2a-43a0-bcd4-48ced6e3facf',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'MutationTaster',
                    'presetssetversion': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
                    'rank': 3,
                    'services': [
                        {
                            'name': 'mutationtaster',
                            'version': '2021'
                        }
                    ],
                    'sodar_uuid': 'e2164371-3920-4108-8260-d2cc2842cc58',
                    'variant_prio_enabled': False
                }
            ],
            'signed_off_by': None,
            'sodar_uuid': '612b6cd5-2d39-45ab-9ddd-2106dcae6e9f',
            'status': 'active',
            'version_major': 1,
            'version_minor': 0
        }
    ]
}

snapshots['CreatePresetsSetTest::test_create_presetsset_short_read_genome 1'] = {
    'date_created': '2024-07-01T00:00:00Z',
    'date_modified': '2024-07-01T00:00:00Z',
    'description': 'Settings for short-read genome sequencing with strict quality presets.  These settings are aimed at WGS sequencing with at least 30x coverage.',
    'label': 'short-read genome sequencing',
    'rank': 1,
    'sodar_uuid': 'c33f4584-b23b-41d8-893c-d01609de8895',
    'versions': [
        {
            'date_created': '2024-07-01T00:00:00Z',
            'date_modified': '2024-07-01T00:00:00Z',
            'predefinedquery_set': [
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd8448135-1816-4a59-8fa0-448eade3702d',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'defaults',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 1,
                    'sodar_uuid': 'bb2a90cd-aa30-410a-9f9e-95261613064f',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd8448135-1816-4a59-8fa0-448eade3702d',
                    'genotype': {
                        'choice': 'de_novo'
                    },
                    'included_in_sop': False,
                    'label': 'de novo',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '18a61865-cafe-4acf-b2cc-dfa7abf10ac2',
                    'rank': 2,
                    'sodar_uuid': '4eb9d5a9-ceb6-4bfe-92f7-992b277364cf',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd8448135-1816-4a59-8fa0-448eade3702d',
                    'genotype': {
                        'choice': 'dominant'
                    },
                    'included_in_sop': False,
                    'label': 'dominant',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 3,
                    'sodar_uuid': '6cbc093c-8902-41e8-b0a8-4cd01be38ac1',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '5486d496-54ce-4017-b930-7855e61f2da4',
                    'genotype': {
                        'choice': 'homozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'homozygous recessive',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 4,
                    'sodar_uuid': '2585702d-09b8-4a4c-964e-e498716d78b2',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '5486d496-54ce-4017-b930-7855e61f2da4',
                    'genotype': {
                        'choice': 'compound_heterozygous_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'compound heterozygous',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 5,
                    'sodar_uuid': 'ca9c2af1-e74d-4213-9b12-d40d00a51da6',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '5486d496-54ce-4017-b930-7855e61f2da4',
                    'genotype': {
                        'choice': 'recessive'
                    },
                    'included_in_sop': False,
                    'label': 'recessive',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 6,
                    'sodar_uuid': '2043c517-1fd3-4c9b-93fd-c924fa02f585',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '5486d496-54ce-4017-b930-7855e61f2da4',
                    'genotype': {
                        'choice': 'x_recessive'
                    },
                    'included_in_sop': False,
                    'label': 'X recessive',
                    'locus': '4678b59a-4bd1-40b4-aa6d-06f0d6cf23c0',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 7,
                    'sodar_uuid': 'c5dccb54-fd3b-47a7-845d-845dbc0e2336',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': '791aa55f-0a95-44a7-af1a-311eb715e9a1',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': 'f362b708-c15c-41bf-a2f2-34308c072307',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '1484cf3f-d92e-4a26-a057-b0de2ab49ae1',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'ClinVar pathogenic',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': 'f275418c-da2f-466e-9fdf-e1685f53f26c',
                    'rank': 8,
                    'sodar_uuid': 'c7d7cd13-e291-4a49-925b-9e35e7609ea3',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': 'f362b708-c15c-41bf-a2f2-34308c072307',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': 'd8448135-1816-4a59-8fa0-448eade3702d',
                    'genotype': {
                        'choice': 'affected_carriers'
                    },
                    'included_in_sop': False,
                    'label': 'mitochondrial',
                    'locus': 'd0469667-db0e-4e65-bcfc-bc361a60e033',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': '9be6a8ea-7f8e-44c2-994b-7a5674043590',
                    'rank': 9,
                    'sodar_uuid': '8847a774-b79f-48f5-9e58-b604566fa460',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                },
                {
                    'clinvar': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd',
                    'columns': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b',
                    'consequence': 'f362b708-c15c-41bf-a2f2-34308c072307',
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'frequency': '1484cf3f-d92e-4a26-a057-b0de2ab49ae1',
                    'genotype': {
                        'choice': 'any'
                    },
                    'included_in_sop': False,
                    'label': 'whole genome',
                    'locus': 'fa6b594e-98e3-4528-a308-b85bc5b58496',
                    'phenotypeprio': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'quality': 'f275418c-da2f-466e-9fdf-e1685f53f26c',
                    'rank': 10,
                    'sodar_uuid': 'c115bff5-eff5-4a26-824c-e83f7f8439ca',
                    'variantprio': 'ba711a18-5e38-49ff-84a3-f94497668966'
                }
            ],
            'presetsset': {
                'date_created': '2024-07-01T00:00:00Z',
                'date_modified': '2024-07-01T00:00:00Z',
                'description': 'Settings for short-read genome sequencing with strict quality presets.  These settings are aimed at WGS sequencing with at least 30x coverage.',
                'label': 'short-read genome sequencing',
                'rank': 1,
                'sodar_uuid': 'c33f4584-b23b-41d8-893c-d01609de8895'
            },
            'querypresetsclinvar_set': [
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                    ],
                    'clinvar_presence_required': False,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'e63ce18b-7eb3-4bc1-8c08-97ce1d0159fd'
                },
                {
                    'allow_conflicting_interpretations': False,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'sodar_uuid': '5c8ffa6e-f489-408b-ba83-f02ac7753887'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'Clinvar P/LP +conflicting',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'sodar_uuid': '791aa55f-0a95-44a7-af1a-311eb715e9a1'
                },
                {
                    'allow_conflicting_interpretations': True,
                    'clinvar_germline_aggregate_description': [
                        'pathogenic',
                        'likely_pathogenic',
                        'uncertain_significance'
                    ],
                    'clinvar_presence_required': True,
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'ClinVar P/LP/VUS +conflicting',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 4,
                    'sodar_uuid': 'c60e43ae-9a13-44ff-aa38-7a4ef7702500'
                }
            ],
            'querypresetscolumns_set': [
                {
                    'column_settings': [
                    ],
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'defaults',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'a51c6d2a-208d-47e3-9bad-d3cc1569f64b'
                }
            ],
            'querypresetsconsequence_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'any',
                    'max_distance_to_exon': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'f362b708-c15c-41bf-a2f2-34308c072307',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'downstream_gene_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        'upstream_gene_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'null variant',
                    'max_distance_to_exon': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'sodar_uuid': '0ec69d37-2d1a-49ea-a4d8-f3636f1f16f1',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'AA change + splicing',
                    'max_distance_to_exon': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'sodar_uuid': '1fe2a062-d1f9-4ffa-9b78-4c44d9d2f5ed',
                    'transcript_types': [
                        'coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'all coding + deep intronic',
                    'max_distance_to_exon': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 4,
                    'sodar_uuid': '291e1aa6-1882-4eed-a749-ac5860383fa0',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'coding_sequence_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'whole transcript',
                    'max_distance_to_exon': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 5,
                    'sodar_uuid': '20f2c360-7ef8-4d5b-95a2-5c02832ea288',
                    'transcript_types': [
                        'coding',
                        'non_coding'
                    ],
                    'variant_consequences': [
                        'frameshift_variant',
                        'rare_amino_acid_variant',
                        'splice_acceptor_variant',
                        'splice_donor_variant',
                        'start_lost',
                        'stop_gained',
                        'stop_lost',
                        '3_prime_UTR_truncation',
                        '5_prime_UTR_truncation',
                        'conservative_inframe_deletion',
                        'conservative_inframe_insertion',
                        'disruptive_inframe_deletion',
                        'disruptive_inframe_insertion',
                        'missense_variant',
                        'splice_region_variant',
                        'initiator_codon_variant',
                        'start_retained',
                        'stop_retained_variant',
                        'synonymous_variant',
                        'intron_variant',
                        'non_coding_transcript_exon_variant',
                        'non_coding_transcript_intron_variant',
                        '5_prime_UTR_variant',
                        'coding_sequence_variant',
                        '3_prime_UTR_variant-exon_variant',
                        '5_prime_UTR_variant-exon_variant',
                        '3_prime_UTR_variant-intron_variant',
                        '5_prime_UTR_variant-intron_variant'
                    ],
                    'variant_types': [
                        'snv',
                        'indel',
                        'mnv',
                        'complex_substitution'
                    ]
                }
            ],
            'querypresetsfrequency_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 1,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant super strict',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'a6561be6-eecb-4547-a76b-b9c89599bc3d'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.002,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 20,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.002,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 4,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant strict',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'sodar_uuid': 'd8448135-1816-4a59-8fa0-448eade3702d'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 50,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 20,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': 0.15,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': 400,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'dominant relaxed',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'sodar_uuid': 'a5ab4237-c971-4e97-b519-8c349f6c6415'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.001,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 120,
                    'gnomad_exomes_homozygous': 0,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.001,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 15,
                    'gnomad_genomes_homozygous': 0,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive strict',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 4,
                    'sodar_uuid': '5486d496-54ce-4017-b930-7855e61f2da4'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': True,
                    'gnomad_exomes_frequency': 0.01,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': 1200,
                    'gnomad_exomes_homozygous': 20,
                    'gnomad_genomes_enabled': True,
                    'gnomad_genomes_frequency': 0.01,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': 150,
                    'gnomad_genomes_homozygous': 4,
                    'helixmtdb_enabled': True,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': 20,
                    'inhouse_enabled': True,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'recessive relaxed',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 5,
                    'sodar_uuid': '70547e0b-b37e-4754-aa03-203287656d8e'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gnomad_exomes_enabled': False,
                    'gnomad_exomes_frequency': None,
                    'gnomad_exomes_hemizygous': None,
                    'gnomad_exomes_heterozygous': None,
                    'gnomad_exomes_homozygous': None,
                    'gnomad_genomes_enabled': False,
                    'gnomad_genomes_frequency': None,
                    'gnomad_genomes_hemizygous': None,
                    'gnomad_genomes_heterozygous': None,
                    'gnomad_genomes_homozygous': None,
                    'helixmtdb_enabled': False,
                    'helixmtdb_frequency': None,
                    'helixmtdb_heteroplasmic': None,
                    'helixmtdb_homoplasmic': None,
                    'inhouse_carriers': None,
                    'inhouse_enabled': False,
                    'inhouse_hemizygous': None,
                    'inhouse_heterozygous': None,
                    'inhouse_homozygous': None,
                    'label': 'any',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 6,
                    'sodar_uuid': '1484cf3f-d92e-4a26-a057-b0de2ab49ae1'
                }
            ],
            'querypresetslocus_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                    ],
                    'label': 'whole genome',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'fa6b594e-98e3-4528-a308-b85bc5b58496'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        },
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'nuclear chromosomes',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'sodar_uuid': '2e8d0bb3-933d-4d81-859d-990181b584eb'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': '1',
                            'range': None
                        },
                        {
                            'chromosome': '2',
                            'range': None
                        },
                        {
                            'chromosome': '3',
                            'range': None
                        },
                        {
                            'chromosome': '4',
                            'range': None
                        },
                        {
                            'chromosome': '5',
                            'range': None
                        },
                        {
                            'chromosome': '6',
                            'range': None
                        },
                        {
                            'chromosome': '7',
                            'range': None
                        },
                        {
                            'chromosome': '8',
                            'range': None
                        },
                        {
                            'chromosome': '9',
                            'range': None
                        },
                        {
                            'chromosome': '10',
                            'range': None
                        },
                        {
                            'chromosome': '11',
                            'range': None
                        },
                        {
                            'chromosome': '12',
                            'range': None
                        },
                        {
                            'chromosome': '13',
                            'range': None
                        },
                        {
                            'chromosome': '14',
                            'range': None
                        },
                        {
                            'chromosome': '15',
                            'range': None
                        },
                        {
                            'chromosome': '16',
                            'range': None
                        },
                        {
                            'chromosome': '17',
                            'range': None
                        },
                        {
                            'chromosome': '18',
                            'range': None
                        },
                        {
                            'chromosome': '19',
                            'range': None
                        },
                        {
                            'chromosome': '20',
                            'range': None
                        },
                        {
                            'chromosome': '21',
                            'range': None
                        },
                        {
                            'chromosome': '22',
                            'range': None
                        }
                    ],
                    'label': 'autosomes',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'sodar_uuid': '944ae60b-0c86-410e-9043-9bde607e2b46'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        },
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'gonosomes',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 4,
                    'sodar_uuid': '0fb87e07-f120-486b-afc6-499d0fab80c5'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'X',
                            'range': None
                        }
                    ],
                    'label': 'X chromosome',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 5,
                    'sodar_uuid': '4678b59a-4bd1-40b4-aa6d-06f0d6cf23c0'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'Y',
                            'range': None
                        }
                    ],
                    'label': 'Y chromosome',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 6,
                    'sodar_uuid': '9f9f243f-85b2-4ac3-93b9-3773e38544f3'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'gene_panels': [
                    ],
                    'genes': [
                    ],
                    'genome_regions': [
                        {
                            'chromosome': 'MT',
                            'range': None
                        }
                    ],
                    'label': 'MT genome',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 7,
                    'sodar_uuid': 'd0469667-db0e-4e65-bcfc-bc361a60e033'
                }
            ],
            'querypresetsphenotypeprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'phenotype_prio_algorithm': 'exomiser.hiphive_human',
                    'phenotype_prio_enabled': False,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': 'e05adc18-0cd3-4c52-91cd-827dc7e6c971',
                    'terms': [
                    ]
                }
            ],
            'querypresetsquality_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'super strict',
                    'max_ad': None,
                    'min_ab_het': 0.3,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 30,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'sodar_uuid': '18a61865-cafe-4acf-b2cc-dfa7abf10ac2'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'strict',
                    'max_ad': None,
                    'min_ab_het': 0.2,
                    'min_ad': 3,
                    'min_dp_het': 10,
                    'min_dp_hom': 5,
                    'min_gq': 10,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'sodar_uuid': '9be6a8ea-7f8e-44c2-994b-7a5674043590'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': True,
                    'label': 'relaxed',
                    'max_ad': None,
                    'min_ab_het': 0.1,
                    'min_ad': 2,
                    'min_dp_het': 8,
                    'min_dp_hom': 4,
                    'min_gq': 10,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'sodar_uuid': '939d61dc-6eb1-48e2-839a-a6b004e77af5'
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'filter_active': False,
                    'label': 'any',
                    'max_ad': None,
                    'min_ab_het': None,
                    'min_ad': None,
                    'min_dp_het': None,
                    'min_dp_hom': None,
                    'min_gq': None,
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 4,
                    'sodar_uuid': 'f275418c-da2f-466e-9fdf-e1685f53f26c'
                }
            ],
            'querypresetsvariantprio_set': [
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'disabled',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 1,
                    'services': [
                    ],
                    'sodar_uuid': 'ba711a18-5e38-49ff-84a3-f94497668966',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'CADD',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 2,
                    'services': [
                        {
                            'name': 'cadd',
                            'version': '1.6'
                        }
                    ],
                    'sodar_uuid': '120287d6-9abf-49b8-ac00-72c72f9e383b',
                    'variant_prio_enabled': False
                },
                {
                    'date_created': '2024-07-01T00:00:00Z',
                    'date_modified': '2024-07-01T00:00:00Z',
                    'description': None,
                    'label': 'MutationTaster',
                    'presetssetversion': '5eb04521-7668-4387-b59b-a79924d8cea5',
                    'rank': 3,
                    'services': [
                        {
                            'name': 'mutationtaster',
                            'version': '2021'
                        }
                    ],
                    'sodar_uuid': 'a9a3d623-8d4d-44f9-be4c-06d4f81bd0ee',
                    'variant_prio_enabled': False
                }
            ],
            'signed_off_by': None,
            'sodar_uuid': '5eb04521-7668-4387-b59b-a79924d8cea5',
            'status': 'active',
            'version_major': 1,
            'version_minor': 0
        }
    ]
}