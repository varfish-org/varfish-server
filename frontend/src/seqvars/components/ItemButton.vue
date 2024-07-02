<template>
  <button type="button"><slot></slot></button>
</template>

<style scoped>
button {
  width: auto;
  height: 100%;
  aspect-ratio: 1/1;
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
