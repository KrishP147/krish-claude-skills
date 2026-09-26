/* Pure slash-input logic. Shared by the browser (window.SkillFilter) and
   node tests (CommonJS module.exports). No DOM access here. */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SkillFilter = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // A buffer is valid when empty, or when it is "/" + a prefix of some name.
  function isValid(buffer, names) {
    if (buffer === "") return true;
    if (buffer.charAt(0) !== "/") return false;
    var rest = buffer.slice(1);
    for (var i = 0; i < names.length; i++) {
      if (names[i].indexOf(rest) === 0) return true;
    }
    return false;
  }

  // Try to append typed text. Returns the new buffer, or null if rejected.
  function accept(buffer, text, names) {
    if (!text) return null;
    var next = buffer + text;
    return isValid(next, names) ? next : null;
  }

  // Names the buffer currently matches; exact match first, then A-Z.
  function matches(buffer, names) {
    if (buffer === "" || buffer.charAt(0) !== "/") return [];
    var rest = buffer.slice(1);
    var out = [];
    for (var i = 0; i < names.length; i++) {
      if (names[i].indexOf(rest) === 0) out.push(names[i]);
    }
    out.sort(function (a, b) {
      if (a === rest) return -1;
      if (b === rest) return 1;
      return a < b ? -1 : a > b ? 1 : 0;
    });
    return out;
  }

  function commonPrefix(list) {
    if (!list.length) return "";
    var p = list[0];
    for (var i = 1; i < list.length; i++) {
      var j = 0;
      while (j < p.length && j < list[i].length && p.charAt(j) === list[i].charAt(j)) j++;
      p = p.slice(0, j);
    }
    return p;
  }

  // Tab completion: the unique name, else the longest common prefix.
  // Returns the completed buffer, or null when it would not extend the
  // buffer (caller must then let Tab move focus normally).
  function complete(buffer, names) {
    var m = matches(buffer, names);
    if (!m.length) return null;
    var next = "/" + (m.length === 1 ? m[0] : commonPrefix(m));
    return next.length > buffer.length ? next : null;
  }

  // Enter: highlighted option if in range, else an exact name, else null.
  function resolve(buffer, names, highlighted) {
    var m = matches(buffer, names);
    if (typeof highlighted === "number" && highlighted >= 0 && highlighted < m.length) {
      return m[highlighted];
    }
    var rest = buffer.slice(1);
    return buffer.charAt(0) === "/" && names.indexOf(rest) !== -1 ? rest : null;
  }

  return {
    isValid: isValid,
    accept: accept,
    matches: matches,
    complete: complete,
    resolve: resolve,
    commonPrefix: commonPrefix
  };
});
