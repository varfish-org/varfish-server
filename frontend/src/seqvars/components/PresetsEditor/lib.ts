// Source: https://dev.to/razi91/using-v-model-with-custom-setters-4hni

import { computed, ref, Ref } from "vue";

export type ProxySetters<T extends object> = Partial<{
  [K in keyof T]: (target: T, value: T[K]) => Partial<T> | Promise<Partial<T>>
}>;

export function toProxy<T extends object>(opt: {
  target: Ref<T>;
  setters: ProxySetters<T>;
}) {
  // <(string & {})> -- a trick for "any string, but still suggest the keys"
  const currentlySetting = ref<keyof T | (string & {})>();

  function setFields(toSet: Partial<T>) {
    opt.target.value = {
      ...opt.target.value,
      ...toSet,
    };
  }

  const proxy = computed({
    get() {
      return new Proxy(opt.target.value, {
        get(target: T, key: string) {
          return target[key as keyof T];
        },
        set(target: T, key: string, value: any) {
          if (currentlySetting.value) return false;
          const setterFn = opt.setters[key as keyof T];
          if (setterFn) {
            currentlySetting.value = key;
            const toSet = setterFn(target, value);
            if (toSet instanceof Promise) {
              toSet
                .then(setFields)
                .finally(() => (currentlySetting.value = undefined));
            } else {
              setFields(toSet);
              currentlySetting.value = undefined;
            }
          } else {
            opt.target.value[key as keyof T] = value;
          }
          return true;
        },
      });
    },
    set(v) {
      opt.target.value = v;
    },
  });

  return {
    proxy,
    currentlySetting,
    isProcessing: computed(() => currentlySetting.value != undefined),
  };
}
