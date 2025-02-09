import chokidar from "fs";
import { addDynamicExports } from "./add-dynamic-exports";

const watcher = chokidar.watch("app/**/page.{tsx,ts}", {
  ignored: /(^|[\/\\])\../,
  persistent: true,
});

watcher.on("add", (path) => {
  console.log(`New page detected: ${path}`);
  addDynamicExports(path);
});
