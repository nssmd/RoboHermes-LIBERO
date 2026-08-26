import path from "node:path";
import {Config} from "@remotion/cli/config";

Config.setPublicDir(
  path.resolve(process.cwd(), "../src/robohermes_libero/static"),
);
Config.setOverwriteOutput(true);
