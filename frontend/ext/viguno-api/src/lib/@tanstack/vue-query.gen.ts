// This file is auto-generated by @hey-api/openapi-ts

import type { Options } from '@hey-api/client-fetch';
import { queryOptions } from '@tanstack/vue-query';
import type { HpoGenesData, HpoOmimsData, HpoSimTermGeneData, HpoSimTermTermData, HpoTermsData } from '../types.gen';
import { client, hpoGenes, hpoOmims, hpoSimTermGene, hpoSimTermTerm, hpoTerms } from '../services.gen';

type QueryKey<TOptions extends Options> = [
    Pick<TOptions, 'baseUrl' | 'body' | 'headers' | 'path' | 'query'> & {
        _id: string;
        _infinite?: boolean;
    }
];

const createQueryKey = <TOptions extends Options>(id: string, options?: TOptions, infinite?: boolean): QueryKey<TOptions>[0] => {
    const params: QueryKey<TOptions>[0] = { _id: id, baseUrl: (options?.client ?? client).getConfig().baseUrl } as QueryKey<TOptions>[0];
    if (infinite) {
        params._infinite = infinite;
    }
    if (options?.body) {
        params.body = options.body;
    }
    if (options?.headers) {
        params.headers = options.headers;
    }
    if (options?.path) {
        params.path = options.path;
    }
    if (options?.query) {
        params.query = options.query;
    }
    return params;
};

export const hpoGenesQueryKey = (options?: Options<HpoGenesData>) => [
    createQueryKey('hpoGenes', options)
];

export const hpoGenesOptions = (options?: Options<HpoGenesData>) => {
    return queryOptions({
        queryFn: async ({ queryKey, signal }) => {
            const { data } = await hpoGenes({
                ...options,
                ...queryKey[0],
                signal,
                throwOnError: true
            });
            return data;
        },
        queryKey: hpoGenesQueryKey(options)
    });
};

export const hpoOmimsQueryKey = (options?: Options<HpoOmimsData>) => [
    createQueryKey('hpoOmims', options)
];

export const hpoOmimsOptions = (options?: Options<HpoOmimsData>) => {
    return queryOptions({
        queryFn: async ({ queryKey, signal }) => {
            const { data } = await hpoOmims({
                ...options,
                ...queryKey[0],
                signal,
                throwOnError: true
            });
            return data;
        },
        queryKey: hpoOmimsQueryKey(options)
    });
};

export const hpoSimTermGeneQueryKey = (options: Options<HpoSimTermGeneData>) => [
    createQueryKey('hpoSimTermGene', options)
];

export const hpoSimTermGeneOptions = (options: Options<HpoSimTermGeneData>) => {
    return queryOptions({
        queryFn: async ({ queryKey, signal }) => {
            const { data } = await hpoSimTermGene({
                ...options,
                ...queryKey[0],
                signal,
                throwOnError: true
            });
            return data;
        },
        queryKey: hpoSimTermGeneQueryKey(options)
    });
};

export const hpoSimTermTermQueryKey = (options: Options<HpoSimTermTermData>) => [
    createQueryKey('hpoSimTermTerm', options)
];

export const hpoSimTermTermOptions = (options: Options<HpoSimTermTermData>) => {
    return queryOptions({
        queryFn: async ({ queryKey, signal }) => {
            const { data } = await hpoSimTermTerm({
                ...options,
                ...queryKey[0],
                signal,
                throwOnError: true
            });
            return data;
        },
        queryKey: hpoSimTermTermQueryKey(options)
    });
};

export const hpoTermsQueryKey = (options?: Options<HpoTermsData>) => [
    createQueryKey('hpoTerms', options)
];

export const hpoTermsOptions = (options?: Options<HpoTermsData>) => {
    return queryOptions({
        queryFn: async ({ queryKey, signal }) => {
            const { data } = await hpoTerms({
                ...options,
                ...queryKey[0],
                signal,
                throwOnError: true
            });
            return data;
        },
        queryKey: hpoTermsQueryKey(options)
    });
};