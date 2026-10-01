/* Simone Menestrina — Ouija portfolio
   Shared script: mobile menu, active section, language links that keep the section,
   reveal on scroll and the Ouija board (planchette, idle wandering, "Ask the board"). */
(function () {
  "use strict";

  window.ouijaReady = true;

  var root = document.documentElement;
  root.classList.add("js");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || !("IntersectionObserver" in window)) root.classList.remove("motion");
  var motion = root.classList.contains("motion");

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  function setMenu(open) {
    if (!toggle || !nav) return;
    toggle.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setMenu(false);
        toggle.focus();
      }
    });

    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) {
      if (mq.matches) setMenu(false);
    });
  }

  /* ---------- Language links follow the current section ---------- */
  var langLinks = Array.prototype.slice.call(document.querySelectorAll(".lang-switch a[hreflang]"));
  langLinks.forEach(function (a) {
    a.setAttribute("data-base", a.getAttribute("href").split("#")[0]);
  });

  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".site-nav a[href^='#']"));

  function setCurrent(id) {
    langLinks.forEach(function (a) {
      a.setAttribute("href", a.getAttribute("data-base") + (id ? "#" + id : ""));
    });
    navLinks.forEach(function (a) {
      if (id && a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }

  var sections = Array.prototype.slice.call(document.querySelectorAll("main > section[id]"));

  if ("IntersectionObserver" in window && sections.length) {
    var sectionObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          setCurrent(id === "top" ? "" : id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) { sectionObserver.observe(s); });
  }

  if (location.hash) setCurrent(location.hash.slice(1));

  /* ---------- Reveal on scroll ---------- */
  if (motion) {
    var revealObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          revealObserver.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.08 }
    );
    document.querySelectorAll("[data-reveal]").forEach(function (el) {
      revealObserver.observe(el);
    });

    // Anything reached by keyboard is shown at once, even mid-animation.
    document.addEventListener("focusin", function (e) {
      var el = e.target.closest && e.target.closest("[data-reveal]");
      if (el) el.classList.add("is-in");
    });
  }

  /* ---------- The board: planchette + "Ask the board" FAQ ---------- */
  var boardEl = document.querySelector(".board");
  if (boardEl) initBoard(boardEl);

  function initBoard(board) {
    var svg = board.querySelector(".board-svg");
    var form = board.querySelector(".ask");
    var input = form && form.querySelector(".ask-input");
    var out = board.querySelector(".ask-answer");
    if (!svg) return;

    /* ----- Glyphs and lighting (shared by every mode) ----- */
    var glyphs = {};
    var list = [];
    Array.prototype.forEach.call(svg.querySelectorAll(".glyph"), function (g) {
      var o = { el: g, key: g.getAttribute("data-ch"), x: +g.getAttribute("data-x"), y: +g.getAttribute("data-y") };
      glyphs[o.key] = o;
      list.push(o);
    });

    var lit = [];           // letters lit by the current answer (or a re-spelling)
    var answerLit = false;  // an answer is on the board

    function light(g) { if (g && lit.indexOf(g) < 0) { g.el.classList.add("on"); lit.push(g); } }

    function clearLit() {
      lit.forEach(function (g) { g.el.classList.remove("on"); });
      lit = [];
    }

    // OUIJA stays lit except while an answer is on the board.
    function ouijaOff() { svg.classList.add("answering"); }
    function ouijaOn() { svg.classList.remove("answering"); }

    /* ----- FAQ: guided questions and keyword matching ----- */
    var faq = { topics: [], fallback: null };
    try { faq = JSON.parse(form.getAttribute("data-faq")) || faq; } catch (e) { /* keep defaults */ }

    function norm(s) {
      return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
        .replace(/[^a-z0-9]+/g, " ").trim();
    }

    // "web app*" -> / web app[a-z0-9]*(?= |$)/ on the normalised question
    function compile(keyword) {
      var parts = keyword.trim().split(/\s+/).map(function (w) {
        var star = /\*$/.test(w);
        return norm(w.replace(/\*$/, "")) + (star ? "[a-z0-9]*" : "");
      }).filter(Boolean);
      return new RegExp("(?:^| )" + parts.join(" ") + "(?= |$)");
    }

    var byId = {};
    faq.topics.forEach(function (topic) {
      topic.patterns = (topic.keywords || []).map(compile);
      byId[topic.id] = topic;
    });

    function match(question) {
      var q = norm(question);
      for (var i = 0; i < faq.topics.length; i++) {
        var topic = faq.topics[i];
        for (var j = 0; j < topic.patterns.length; j++) {
          if (topic.patterns[j].test(q)) return topic;
        }
      }
      return faq.fallback;
    }

    function showText(answer) {
      var prefix = document.createElement("span");
      prefix.className = "ask-prefix";
      prefix.textContent = form.getAttribute("data-prefix");
      var text = document.createElement("strong");
      text.textContent = answer.text;
      out.textContent = "";
      out.append(prefix, " ", text);
    }

    var asked = 0;
    var engine = null;      // set below when motion is allowed
    var idleTimer = 0;

    function respond(answer) {
      if (!answer) return;
      var n = ++asked;
      if (engine && engine.canAnimate()) {
        out.textContent = "";
        var shown = false;
        var reveal = function () { if (!shown && n === asked) { shown = true; showText(answer); } };
        engine.answer(answer.word).then(reveal);
        setTimeout(reveal, 8000);
        return;
      }
      // Still board: the answer's letters light up at once, text right away.
      clearLit();
      ouijaOff();
      answer.word.split("").forEach(function (ch) { light(glyphs[ch]); });
      answerLit = true;
      showText(answer);
      armIdle();
    }

    if (form && input && out) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (!input.value.trim()) {
          out.textContent = form.getAttribute("data-empty");
          input.focus();
          return;
        }
        respond(match(input.value));
      });

      Array.prototype.forEach.call(form.querySelectorAll(".ask-chip"), function (chip) {
        chip.addEventListener("click", function () {
          input.value = chip.textContent;
          respond(byId[chip.getAttribute("data-topic")]);
        });
      });
    }

    /* ----- Idle: after ~6 s without interaction the board goes back to OUIJA ----- */
    var IDLE_MS = 6000;
    var onIdle = function () {
      if (answerLit) { clearLit(); ouijaOn(); answerLit = false; }
    };

    function armIdle() {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(function () { onIdle(); }, IDLE_MS);
    }

    // Reduced motion (or no motion support): a still board, lights only.
    if (!motion) {
      ["pointermove", "pointerdown", "keydown", "wheel", "touchstart", "scroll"].forEach(function (type) {
        window.addEventListener(type, function () { if (answerLit) armIdle(); }, { passive: true });
      });
      return;
    }

    /* ----- Motion: the planchette ----- */
    var pl = svg.querySelector(".pl");
    var body = svg.querySelector(".pl-body");
    var lens = svg.querySelector(".pl-lens");
    var trail = Array.prototype.slice.call(svg.querySelectorAll(".pl-trail circle"));
    var REST = { x: +svg.getAttribute("data-rest-x"), y: +svg.getAttribute("data-rest-y") };
    var LENS = 1.2;
    var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

    var pos = { x: REST.x, y: REST.y };
    var vel = { x: 0, y: 0 };
    var target = { x: REST.x, y: REST.y };
    var stiffness = 12;     // spring strength: higher = snappier
    var tolerance = 1;      // how close counts as "arrived"
    var tilt = 0;
    var history = [];
    var arrivals = [];
    var raf = 0;
    var last = 0;

    // intro | rest | follow | wander | answer | respell
    var mode = "intro";
    var token = 0;          // bumped to cancel whatever sequence is running
    var onScreen = false;
    var introStarted = false;
    var introDone = false;
    var near = null;

    function active() { return onScreen && !document.hidden; }
    function busy() { return mode === "intro" || mode === "answer" || mode === "respell"; }

    function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

    function render() {
      pl.setAttribute("transform", "translate(" + pos.x.toFixed(2) + " " + pos.y.toFixed(2) + ")");
      body.setAttribute("transform", "rotate(" + tilt.toFixed(2) + ")");
      lens.setAttribute("transform", "scale(" + LENS + ") translate(" + (-pos.x).toFixed(2) + " " + (-pos.y).toFixed(2) + ")");
    }

    function flushArrivals() {
      var done = arrivals;
      arrivals = [];
      done.forEach(function (r) { r(); });
    }

    function kick() {
      if (!raf && active()) {
        last = 0;
        raf = requestAnimationFrame(frame);
      }
    }

    function setTarget(p, k, tol) {
      target = { x: p.x, y: p.y };
      stiffness = k;
      tolerance = tol || 1;
      flushArrivals();
      kick();
    }

    function moveTo(p, k, tol) {
      setTarget(p, k, tol);
      return new Promise(function (r) { arrivals.push(r); });
    }

    // Critically damped spring: eases in and out, no overshoot.
    function frame(now) {
      raf = 0;
      if (!active()) { last = 0; return; }
      var dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
      last = now;

      var w = Math.sqrt(stiffness);
      vel.x += (stiffness * (target.x - pos.x) - 2 * w * vel.x) * dt;
      vel.y += (stiffness * (target.y - pos.y) - 2 * w * vel.y) * dt;
      pos.x += vel.x * dt;
      pos.y += vel.y * dt;

      // Lean into the direction of travel.
      var lean = Math.max(-12, Math.min(12, vel.x / 40));
      tilt += (lean - tilt) * (1 - Math.exp(-8 * dt));

      var speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y);
      history.unshift({ x: pos.x, y: pos.y });
      if (history.length > 32) history.length = 32;
      var strength = Math.min(1, speed / 450);
      trail.forEach(function (dot, i) {
        var h = history[Math.min(history.length - 1, (i + 1) * 4)];
        dot.setAttribute("transform", "translate(" + h.x.toFixed(1) + " " + h.y.toFixed(1) + ")");
        dot.style.opacity = (strength * 0.45 * (1 - i / trail.length)).toFixed(3);
      });

      render();
      if (mode === "follow") updateNear();

      var dist = Math.sqrt((target.x - pos.x) * (target.x - pos.x) + (target.y - pos.y) * (target.y - pos.y));
      if (arrivals.length && dist < tolerance && speed < 40) flushArrivals();

      var settled = dist < 0.25 && speed < 0.5 && Math.abs(tilt) < 0.05;
      if (!settled || arrivals.length || mode === "follow") {
        raf = requestAnimationFrame(frame);
      } else {
        trail.forEach(function (dot) { dot.style.opacity = "0"; });
        last = 0;
      }
    }

    function setNear(g) {
      if (g === near) return;
      if (near) near.el.classList.remove("near");
      near = g;
      if (near) near.el.classList.add("near");
    }

    function updateNear() {
      var best = null;
      var bestD = Infinity;
      list.forEach(function (g) {
        var d = (g.x - pos.x) * (g.x - pos.x) + (g.y - pos.y) * (g.y - pos.y);
        if (d < bestD) { bestD = d; best = g; }
      });
      setNear(bestD < 34 * 34 ? best : null);
    }

    // Glide over each character in turn (letters and the 1-0 row); resolves false if interrupted.
    function spell(word, k, t) {
      var prev = null;
      return word.split("").reduce(function (p, ch) {
        return p.then(function (ok) {
          if (!ok || t !== token) return false;
          if (ch === " ") {
            prev = null;
            return moveTo(REST, k, 4).then(function () { return wait(220); }).then(function () { return t === token; });
          }
          var g = glyphs[ch];
          if (!g) return true;
          // Same character twice: a small hop off and back, like lifting the planchette.
          var hop = g === prev ? moveTo({ x: g.x, y: g.y + 28 }, k * 1.4, 5) : Promise.resolve();
          return hop.then(function () { return moveTo(g, k, 2); }).then(function () {
            if (t !== token) return false;
            light(g);
            prev = g;
            return wait(320).then(function () { return t === token; });
          });
        });
      }, Promise.resolve(true));
    }

    function toRest(k) {
      mode = "rest";
      setNear(null);
      setTarget(REST, k || 10, 1);
    }

    function stopWander(jump) {
      if (mode !== "wander") return;
      token++;
      if (jump) {
        // Off screen: no one is watching, just put it back.
        mode = "rest";
        pos = { x: REST.x, y: REST.y };
        vel = { x: 0, y: 0 };
        target = { x: REST.x, y: REST.y };
        tilt = 0;
        flushArrivals();
        render();
      } else {
        toRest(10);
      }
    }

    // Idle drifting: slow and silent, nothing lights up.
    function wander() {
      var t = ++token;
      mode = "wander";
      (function next() {
        if (t !== token) return;
        var p = { x: 150 + Math.random() * 460, y: 150 + Math.random() * 260 };
        moveTo(p, 4, 6).then(function () { return wait(500 + Math.random() * 1000); }).then(next);
      })();
    }

    // Spell O-U-I-J-A, then leave it lit. Used on first view and after an answer fades.
    function spellOuija(t, delay) {
      ouijaOff();
      clearLit();
      return wait(delay).then(function () { return spell("OUIJA", 55, t); }).then(function (ok) {
        if (t !== token) return false;
        ouijaOn();
        svg.classList.add("spelled");
        return wait(600).then(function () {
          if (t !== token) return false;
          clearLit();
          toRest(10);
          armIdle();
          return ok;
        });
      });
    }

    function intro() {
      introStarted = true;
      mode = "intro";
      var t = ++token;
      // The first time OUIJA is hidden by .motion:not(.spelled), not by .answering.
      ouijaOn();
      wait(400).then(function () { return spell("OUIJA", 60, t); }).then(function () {
        svg.classList.add("spelled");
        introDone = true;
        if (t !== token) return;
        return wait(600).then(function () {
          if (t !== token) return;
          clearLit();
          toRest(10);
          armIdle();
        });
      });
    }

    onIdle = function () {
      if (!introDone || mode !== "rest" || !active()) return;
      if (answerLit) {
        // The answer fades and the planchette writes OUIJA again.
        answerLit = false;
        mode = "respell";
        spellOuija(++token, 200);
      } else {
        wander();
      }
    };

    var baseArmIdle = armIdle;
    armIdle = function () {
      if (!introDone || !active()) { clearTimeout(idleTimer); return; }
      baseArmIdle();
    };

    engine = {
      canAnimate: active,
      answer: function (word) {
        var t = ++token;
        mode = "answer";
        clearTimeout(idleTimer);
        clearLit();
        setNear(null);
        ouijaOff();
        answerLit = true;
        if (!introDone) { svg.classList.add("spelled"); introDone = true; introStarted = true; }
        return spell(word, 60, t).then(function (ok) {
          if (!ok || t !== token) return false;
          mode = "rest";
          armIdle();
          return true;
        });
      }
    };

    /* Following the mouse (mouse only, never touch) */
    if (finePointer) {
      svg.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse" || !introDone || busy()) return;
        var m = svg.getScreenCTM();
        if (!m) return;
        var pt = svg.createSVGPoint();
        pt.x = e.clientX;
        pt.y = e.clientY;
        var p = pt.matrixTransform(m.inverse());
        if (mode !== "follow") {
          token++;
          mode = "follow";
        }
        setTarget(p, 110, 1);
      });

      svg.addEventListener("pointerleave", function () {
        if (mode !== "follow") return;
        toRest(9);
        armIdle();
      });
    }

    /* Any interaction ends the idle wandering and restarts the idle clock */
    function interact() {
      stopWander(false);
      if (!busy()) armIdle();
    }

    ["pointermove", "pointerdown", "keydown", "wheel", "touchstart", "scroll"].forEach(function (type) {
      window.addEventListener(type, interact, { passive: true });
    });

    /* Pause everything off screen or in a background tab */
    function sleep() {
      clearTimeout(idleTimer);
      stopWander(true);
    }

    new IntersectionObserver(function (entries) {
      var entry = entries[entries.length - 1];
      onScreen = entry.isIntersecting;
      if (!onScreen) { sleep(); return; }
      if (!introStarted && entry.intersectionRatio >= 0.25) {
        var fonts = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
        introStarted = true;
        fonts.then(intro);
      }
      kick();
      if (!busy()) armIdle();
    }, { threshold: [0, 0.25] }).observe(svg);

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) sleep();
      else { kick(); if (!busy()) armIdle(); }
    });
  }
})();
