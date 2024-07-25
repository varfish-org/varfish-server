<template>
  <button type="button"><slot></slot></button>
</template>

<style scoped>
button {
  padding: 0 6px;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  &:hover {
    background: #e3e3e380;
  }

  &:not(:focus-visible) {
    outline: none;
  }
}
</style>
