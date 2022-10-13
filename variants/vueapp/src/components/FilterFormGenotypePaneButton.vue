<script setup></script>

<template>
  <div class="dropdown d-inline" id="presets-genotype-dropdown">
    <button
      class="btn btn-sm btn-outline-secondary dropdown-toggle"
      type="button"
      id="presets-genotype-button"
      data-toggle="dropdown"
      aria-haspopup="true"
      aria-expanded="false"
    >
      <i-mdi-tools />
    </button>
    <div class="dropdown-menu" aria-labelledby="presets-genotype-button">
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:any"
        >Unaffected: any</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:ref"
        >Unaffected: 0/0</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:het"
        >Unaffected: 0/1</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:non-hom"
        >Unaffected: 0/0 or 0/1</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:non-variant"
        >Unaffected: non-variant</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="unaffected:non-reference"
        >Unaffected: non-reference</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:any"
        >Affected: any</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:het"
        >Affected: 0/1</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:hom"
        >Affected: 1/1</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:non-hom"
        >Affected: 0/0 or 0/1</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:variant"
        >Affected: variant</a
      >
      <a
        class="dropdown-item load-genotype"
        href="#"
        data-preset-name="affected:non-reference"
        >Affected: non-reference</a
      >
    </div>
  </div>
</template>
