<script setup>
import { ref } from 'vue'

import CollapsibleGroup from './CollapsibleGroup.vue'
import InheritanceModeControls from './InheritanceModeControls.vue'
import Item from './Item.vue'

const checked = ref(new Set())
</script>

<template>
  <div style="height: 100vh; display: flex" class="bg-bg">
    <div style="width: 100%; max-width: 350px; height: 100%; overflow-y: auto">
      <div
        class="text-ui-control-text"
        style="
          padding: 6px;
          font-weight: bold;
          color: white !important;
          background: #1e3064;
        "
      >
        NA12878
      </div>
      <div
        style="
          border-right: 1px solid #e9e9e9;
          height: 100%;
          display: flex;
          flex-direction: column;
          gap: 16px;
        "
      >
        <CollapsibleGroup title="Results">
          <div style="width: 100%; display: flex; flex-direction: column">
            <Item>flagged variants</Item>
            <Item selected>de novo</Item>
          </div>
        </CollapsibleGroup>

        <CollapsibleGroup title="Presets">
          <div style="width: 100%; display: flex; flex-direction: column">
            <Item>de novo</Item>
            <Item>dominant</Item>
            <Item>known curable</Item>
          </div>
        </CollapsibleGroup>

        <CollapsibleGroup title="Genotype">
          <div
            style="
              width: 100%;
              display: flex;
              flex-direction: column;
              gap: 16px;
            "
          >
            <div style="width: 100%; display: flex; flex-direction: column">
              <Item>de novo</Item>
              <Item>dominant</Item>
              <Item>affected caries</Item>
              <Item>any mode</Item>
            </div>

            <div
              class="bg-inactive-ui-element"
              style="margin: 4px 0; width: 100%; height: 1px"
            ></div>

            <div
              v-for="item in ['index II', 'father I', 'mother I', 'sibling']"
              :key="item"
              style="
                display: flex;
                flex-direction: row;
                align-items: start;
                gap: 12px;
              "
            >
              <input :id="item" type="checkbox" style="margin-top: 6px" />
              <div style="display: flex; flex-direction: column; gap: 4px">
                <label :for="item">{{ item }}</label>
                <InheritanceModeControls v-model="checked" />
              </div>
            </div>
          </div>
        </CollapsibleGroup>
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
