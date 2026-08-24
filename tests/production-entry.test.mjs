import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import test from "node:test";

test("the production build loads the React application bundle", async () => {
  const build = spawnSync("npm", ["run", "build"], {
    cwd: process.cwd(),
    encoding: "utf8",
  });

  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);

  const html = await readFile("dist/index.html", "utf8");
  const assets = await readdir("dist/assets");
  const javascriptAssets = assets.filter((asset) => asset.endsWith(".js"));

  assert.ok(
    javascriptAssets.length > 0,
    "expected Vite to emit the React JavaScript bundle",
  );
  assert.match(
    html,
    /<script[^>]+src="\/assets\/[^\"]+\.js"[^>]*><\/script>/,
    "expected the built page to load the emitted React bundle",
  );
});
