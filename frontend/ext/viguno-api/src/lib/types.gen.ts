// This file is auto-generated by @hey-api/openapi-ts

/**
 * Struct for loading an HPO term from JSON.
 */
export type HpoTerm = {
    /**
     * The term ID.
     */
    term_id: string;
    /**
     * The term name (optional).
     */
    term_name?: (string) | null;
};

/**
 * Enum for representing the information content kind.
 *
 * We replicate what is in the `hpo` create so we can put them on the command line and use
 * them in HTTP queries more easily.
 */
export type IcBasedOn = 'gene' | 'omim';

/**
 * Specify how to perform query matches in the API calls.
 */
export type Match = 'exact' | 'prefix' | 'suffix' | 'contains';

/**
 * Parameters for `handle`.
 *
 * This allows to compute differences between
 *
 * - `terms` -- set of terms to use as query
 * - `gene_ids` -- set of ids for genes to use as "database", can be NCBI\
 * gene ID or HGNC gene ID.
 * - `gene_symbols` -- set of symbols for genes to use as
 * "database"
 */
export type Query = {
    /**
     * Set of terms to use as query.
     */
    terms: Array<(string)>;
    /**
     * The set of ids for genes to use as "database".
     */
    gene_ids?: Array<(string)> | null;
    /**
     * The set of symbols for genes to use as "database".
     */
    gene_symbols?: Array<(string)> | null;
};

/**
 * Request as sent together with the response.
 *
 * The difference is that the `lhs` and `rhs` fields are replaced by vecs.
 */
export type ResponseQuery = {
    /**
     * The one set of HPO terms to compute similarity for.
     */
    lhs: Array<(string)>;
    /**
     * The second set of HPO terms to compute similarity for.
     */
    rhs: Array<(string)>;
    ic_base?: IcBasedOn;
    similarity?: SimilarityMethod;
    combiner?: ScoreCombiner;
};

/**
 * Result container.
 */
export type Result = {
    version: Version;
    query: ResponseQuery;
    /**
     * The resulting records for the scored genes.
     */
    result: Array<ResultEntry>;
};

/**
 * Container for the result.
 */
export type Result_ = {
    version: Version;
    query: Query;
    /**
     * The resulting records for the scored genes.
     */
    result: Array<ResultEntry>;
};

/**
 * Result entry for `handle`.
 */
export type ResultEntry = {
    /**
     * The lhs entry.
     */
    lhs: string;
    /**
     * The rhs entry.
     */
    rhs: string;
    /**
     * The similarity score.
     */
    score: number;
};

/**
 * Representation of a gene.
 */
export type ResultGene = {
    /**
     * The HPO ID.
     */
    ncbi_gene_id: number;
    /**
     * The description.
     */
    gene_symbol: string;
    /**
     * The HGNC ID.
     */
    hgnc_id?: (string) | null;
};

/**
 * Representation of an HPO term.
 */
export type ResultHpoTerm = {
    /**
     * The HPO ID.
     */
    term_id: string;
    /**
     * The term name.
     */
    name: string;
};

/**
 * Representation of the standard combiners from HPO.
 *
 * We replicate what is in the `hpo` create so we can put them on the command line and use
 * them in HTTP queries more easily.
 */
export type ScoreCombiner = 'fun-sim-avg' | 'fun-sim-max' | 'bma';

/**
 * Enum for representing similarity method to use.
 *
 * We replicate what is in the `hpo` create so we can put them on the command line and use
 * them in HTTP queries more easily.
 */
export type SimilarityMethod = 'distance-gene' | 'graph-ic' | 'information-coefficient' | 'jc' | 'lin' | 'mutation' | 'relevance' | 'resnik';

/**
 * Detailed term scores.
 */
export type TermDetails = {
    term_query?: ((HpoTerm) | null);
    term_gene: HpoTerm;
    /**
     * The similarity score.
     */
    score: number;
};

/**
 * Version information that is returned by the HTTP server.
 */
export type Version = {
    /**
     * Version of the HPO.
     */
    hpo: string;
    /**
     * Version of the `viguno` package.
     */
    viguno: string;
};

export type HpoGenesData = {
    query?: {
        /**
         * The gene ID to search for.
         */
        gene_id?: (string) | null;
        /**
         * The gene symbol to search for.
         */
        gene_symbol?: (string) | null;
        /**
         * Whether to include HPO terms.
         */
        hpo_terms?: boolean;
        /**
         * The match mode.
         */
        match_?: ((Match) | null);
        /**
         * Maximal number of results to return.
         */
        max_results?: number;
    };
};

export type HpoGenesResponse = (Result);

export type HpoGenesError = unknown;

export type HpoOmimsData = {
    query?: {
        /**
         * Whether to include HPO terms.
         */
        hpo_terms?: boolean;
        /**
         * Whether case is insentivie, default is `false`.
         */
        ignore_case?: (boolean) | null;
        /**
         * The match mode, default is `Match::Exact`.
         */
        match_?: ((Match) | null);
        /**
         * Maximal number of results to return.
         */
        max_results?: number;
        /**
         * The disease name to search for.
         */
        name?: (string) | null;
        /**
         * The OMIM ID to search for.
         */
        omim_id?: (string) | null;
    };
};

export type HpoOmimsResponse = (Result);

export type HpoOmimsError = unknown;

export type HpoSimTermGeneData = {
    query: {
        /**
         * The set of ids for genes to use as "database".
         */
        gene_ids?: Array<(string)> | null;
        /**
         * The set of symbols for genes to use as "database".
         */
        gene_symbols?: Array<(string)> | null;
        /**
         * Set of terms to use as query.
         */
        terms: Array<(string)>;
    };
};

export type HpoSimTermGeneResponse = (Result);

export type HpoSimTermGeneError = unknown;

export type HpoSimTermTermData = {
    query: {
        /**
         * The score combiner.
         */
        combiner?: ScoreCombiner;
        /**
         * What should information content be based on.
         */
        ic_base?: IcBasedOn;
        /**
         * The one set of HPO terms to compute similarity for.
         */
        lhs: Array<(string)>;
        /**
         * The second set of HPO terms to compute similarity for.
         */
        rhs: Array<(string)>;
        /**
         * The similarity method to use.
         */
        similarity?: SimilarityMethod;
    };
};

export type HpoSimTermTermResponse = (Result);

export type HpoSimTermTermError = unknown;

export type HpoTermsData = {
    query?: {
        /**
         * Whether to include genes.
         */
        genes?: boolean;
        /**
         * Maximal number of results to return.
         */
        max_results?: number;
        /**
         * The term name to search for.
         */
        name?: (string) | null;
        /**
         * The term ID to search for.
         */
        term_id?: (string) | null;
    };
};

export type HpoTermsResponse = (Result);

export type HpoTermsError = unknown;