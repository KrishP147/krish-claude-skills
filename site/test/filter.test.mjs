// Dependency-free: node --test site/test/filter.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const F = require("../src/filter.js");

const NAMES = ["pair", "planner", "progress-report", "grilling", "grill-me", "grill-docs", "handoff", "handoff-auto", "next"];

test("first key must be '/'", () => {
  assert.equal(F.accept("", "x", NAMES), null);
  assert.equal(F.accept("", "p", NAMES), null);
  assert.equal(F.accept("", " ", NAMES), null);
  assert.equal(F.accept("", "/", NAMES), "/");
});

test("only keys keeping a name prefix are accepted", () => {
  assert.equal(F.accept("/", "p", NAMES), "/p");
  assert.equal(F.accept("/p", "a", NAMES), "/pa");
  assert.equal(F.accept("/pa", "x", NAMES), null);
  assert.equal(F.accept("/", "z", NAMES), null);
  assert.equal(F.accept("/pair", "s", NAMES), null);
  assert.equal(F.accept("/pa", "", NAMES), null);
});

test("isValid gates whole values (IME / paste rollback)", () => {
  assert.equal(F.isValid("", NAMES), true);
  assert.equal(F.isValid("/", NAMES), true);
  assert.equal(F.isValid("/pai", NAMES), true);
  assert.equal(F.isValid("x", NAMES), false);
  assert.equal(F.isValid("pair", NAMES), false);
  assert.equal(F.isValid("/pairx", NAMES), false);
  assert.equal(F.isValid("//", NAMES), false);
});

test("'/pa' filters to pair", () => {
  assert.deepEqual(F.matches("/pa", NAMES), ["pair"]);
  assert.deepEqual(F.matches("/p", NAMES), ["pair", "planner", "progress-report"]);
  assert.deepEqual(F.matches("", NAMES), []);
  assert.equal(F.matches("/", NAMES).length, NAMES.length);
});

test("exact match sorts first", () => {
  assert.deepEqual(F.matches("/handoff", NAMES), ["handoff", "handoff-auto"]);
});

test("tab completes unique name, else longest common prefix, else null", () => {
  assert.equal(F.complete("/pa", NAMES), "/pair");
  assert.equal(F.complete("/gr", NAMES), "/grill");
  assert.equal(F.complete("/grill", NAMES), null);
  assert.equal(F.complete("/pair", NAMES), null);
  assert.equal(F.complete("", NAMES), null);
  assert.equal(F.complete("/n", NAMES), "/next");
});

test("enter resolution", () => {
  assert.equal(F.resolve("/pa", NAMES, 0), "pair");
  assert.equal(F.resolve("/pair", NAMES, -1), "pair");
  assert.equal(F.resolve("/p", NAMES, 1), "planner");
  assert.equal(F.resolve("/p", NAMES, -1), null);
  assert.equal(F.resolve("/handoff", NAMES, 0), "handoff");
  assert.equal(F.resolve("/handoff", NAMES, 1), "handoff-auto");
  assert.equal(F.resolve("", NAMES, 0), null);
  assert.equal(F.resolve("/p", NAMES, 99), null);
});

test("commonPrefix", () => {
  assert.equal(F.commonPrefix([]), "");
  assert.equal(F.commonPrefix(["abc"]), "abc");
  assert.equal(F.commonPrefix(["grill-me", "grilling"]), "grill");
});
