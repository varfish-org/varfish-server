from rest_framework import serializers


class GeneInfoSerializer(serializers.Serializer):
    """Serializer that serializes ``Hgnc`` to gene information"""

    hgnc_id = serializers.CharField(max_length=16)
    symbol = serializers.CharField(max_length=16)
    ensembl_gene_id = serializers.CharField(max_length=32)
    entrez_id = serializers.CharField(max_length=16)
