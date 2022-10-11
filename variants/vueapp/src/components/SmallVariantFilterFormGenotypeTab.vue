<template>
  <div style="overflow-y: auto !important; max-height: 400px">
    <div class="small font-italic p-2 bg-light">
      Use this form to fine-tune the genotype settings for each individual.
      Selecting "c/h index" (respectively "recess. index") for filtering for
      variants where the variant fulfills the comp. het. recessive criteria
      (respectively comp. het. or hom. recessive criteria). You can use the
      <span class="badge border" style="border-color: #6c757d !important"
        ><span
          class="iconify"
          data-icon="mdi:dip-switch"
          data-inline="false"
        ></span
      ></span>
      button to batch assign genotypes based on disease state.
    </div>
    <table
      class="table table-striped table-hover sodar-card-table compact-form-groups"
    >
      <thead>
        <tr>
          <th class="text-muted" style="width: 10px">#</th>
          <th class="col-2">Family</th>
          <th class="col-2">Individual</th>
          <th class="col-2">Trio Role</th>
          <th class="col-2">Father</th>
          <th class="col-2">Mother</th>
          <th class="col-1">Sex</th>
          <th class="col-1">Affected</th>
          <th class="col-1">
            <span
              data-toggle="tooltip"
              data-placement="left"
              data-html="true"
              title="<div class='text-left'><ul class='pl-3'><li><strong>any</strong>: don't apply genotype filter</li><li><strong>variant</strong>: allows genotypes <em>0/1</em> and <em>1/1</em></li><li><strong>non-variant</strong>: allows genotypes <em>0/0</em> and <em>./.</em></li><li><strong>non-reference</strong>: allows genotypes that are a variant or <em>./.</em></li><li><strong>index</strong>: activate comp het mode for this index patient.</li></ul></div>"
              >Genotype</span
            >
            &nbsp;
            <div class="dropdown d-inline" id="presets-genotype-dropdown">
              <button
                class="btn btn-sm btn-outline-secondary dropdown-toggle"
                type="button"
                id="presets-genotype-button"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
              >
                <span
                  class="iconify"
                  data-icon="mdi:dip-switch"
                  data-inline="false"
                ></span>
              </button>
              <div
                class="dropdown-menu"
                aria-labelledby="presets-genotype-button"
              >
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
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in store.case.pedigree" :key="index">
          <td>{{ index }}</td>
          <td>{{ store.case.name }}</td>
          <td>{{ $filters.displayName(item.name) }}</td>
          <td>{{ store.getRole(item.name) }}</td>
          <td>{{ $filters.displayName(item.name) }}</td>
          <td>{{ $filters.displayName(item.name) }}</td>
          <td>
            <i
              class="iconify"
              :data-icon="$filters.displaySexIcon(item.sex)"
            ></i>
          </td>
          <td>
            <i
              class="iconify"
              :class="$filters.displayAffectedColor(item.affected)"
              :data-icon="$filters.displayAffectedIcon(item.affected)"
            ></i>
          </td>
          <td class="text-right text-muted">
            <select
              v-model="store.querySettings.genotype[item.name]"
              :id="'id_' + item.name + '_gt'"
              :name="item.name + '_gt'"
            >
              <option value="any">any</option>
              <option value="ref">0/0</option>
              <option value="het">0/1</option>
              <option value="hom">1/1</option>
              <option value="non-hom">0/0 or 0/1</option>
              <option value="variant">variant</option>
              <option value="non-variant">non-variant</option>
              <option value="non-reference">non-reference</option>
              <option value="index">c/h index</option>
              <option value="recessive-index">recess. index</option>
            </select>
          </td>
        </tr>
        <!--              {% if item.has_gt_entries %}-->
        <!--                <td>-->
        <!--                  {% with x=form.get_genotype_field_names|keyvalue:item.patient|keyvalue:"gt" %}-->
        <!--                    {{ form|keyvalue:x }}-->
        <!--                    <em class="text-muted" style="display: none;" id="trio_role_{{ family }}_{{ x }}"></em>-->
        <!--                  {% endwith %}-->
        <!--                </td>-->
        <!--              {% else %}-->
        <!--                <td class="text-centered">-->
        <!--                  <em>no genotypes</em>-->
        <!--                </td>-->
        <!--              {% endif %}-->
      </tbody>
    </table>
  </div>

  <div
    class="row p-2 mt-2 border-top alert-info"
    style="display: none"
    id="compound_heterozygous_warning"
  >
    <div class="col pt-1">
      <i class="iconify pr-2" data-icon="fa-solid:users"></i>
      <strong>Compound heterozygous mode activated</strong>
    </div>
    <div class="col text-right">
      <!--      {% if query_type == "case" %}-->
      <!--        <div class="btn btn-sm btn-info" id="compound_heterozygous_disable">-->
      <!--          <span class="iconify" data-icon="mdi:close" data-inline="false"></span>-->
      <!--          Disable comp. het. mode-->
      <!--        </div>-->
      <!--      {% else %} {# query_type == "project" #}-->
      <!--        {# Technically, we could use the above code for the project filter as it can disable multiple indices. #}-->
      <!--        {# This is to prevent people from resetting all genotype comp het modes accidentally. #}-->
      <!--        <em>Please disable comp. het. mode in <strong>Genotype</strong> field for each family separately.</em>-->
      <!--      {% endif %}-->
    </div>
  </div>

  <div
    class="row p-2 mt-2 border-top alert-info"
    style="display: none"
    id="recessive_warning"
  >
    <div class="col pt-1">
      <i class="iconify pr-2" data-icon="fa-solid:users"></i>
      <strong>Recessive mode activated</strong>
    </div>
    <div class="col text-right">
      <!--      {% if query_type == "case" %}-->
      <!--        <div class="btn btn-sm btn-info" id="recessive_disable">-->
      <!--          <span class="iconify" data-icon="mdi:close" data-inline="false"></span>-->
      <!--          Disable recessive mode-->
      <!--        </div>-->
      <!--      {% else %} {# query_type == "project" #}-->
      <!--        {# Technically, we could use the above code for the project filter as it can disable multiple indices. #}-->
      <!--        {# This is to prevent people from resetting all genotype comp het modes accidentally. #}-->
      <!--        <em>Please disable recessive mode in <strong>Genotype</strong> field for each family separately.</em>-->
      <!--      {% endif %}-->
    </div>
  </div>
</template>

<script>
import { useFilterQueryStore } from '@variants/stores/filterQuery'

export default {
  setup() {
    const store = useFilterQueryStore()
    return { store }
  },
}
</script>
