// source.config.ts
import { defineConfig, defineDocs } from "fumadocs-mdx/config";
import { remarkMdxMermaid } from "fumadocs-core/mdx-plugins";
var { docs, meta } = defineDocs({
  dir: "src/content/docs"
});
var source_config_default = defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkMdxMermaid]
  }
});
export {
  source_config_default as default,
  docs,
  meta
};
