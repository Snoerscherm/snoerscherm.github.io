/* Snoer & Scherm: menu's, plakbalk, bereikbaarheid, vinkjes en het snoer tussen de stappen.
   Alles werkt ook zonder dit script; het voegt alleen gemak en beweging toe. */
(function () {
  "use strict";

  var html = document.documentElement;
  var kop = document.querySelector(".site-kop");

  /* Mobiel menu */
  var menuknop = document.querySelector(".menuknop");
  var mobielmenu = document.getElementById("mobielmenu");

  function zetMenu(open) {
    if (!menuknop || !mobielmenu) return;
    html.classList.toggle("menu-open", open);
    menuknop.setAttribute("aria-expanded", String(open));
    menuknop.setAttribute("aria-label", open ? "Menu sluiten" : "Menu openen");
    if (open) {
      mobielmenu.removeAttribute("inert");
    } else {
      mobielmenu.setAttribute("inert", "");
    }
  }

  if (menuknop && mobielmenu) {
    mobielmenu.setAttribute("inert", "");
    menuknop.addEventListener("click", function () {
      zetMenu(menuknop.getAttribute("aria-expanded") !== "true");
    });
    mobielmenu.addEventListener("click", function (e) {
      if (e.target.closest("a")) zetMenu(false);
    });
    window.matchMedia("(min-width: 62rem)").addEventListener("change", function (e) {
      if (e.matches) zetMenu(false);
    });
  }

  /* Uitklapmenu Diensten (klik en toetsenbord; hover regelt de CSS) */
  var menus = document.querySelectorAll(".heeft-menu");
  menus.forEach(function (item) {
    var knop = item.querySelector("button");
    if (!knop) return;
    knop.addEventListener("click", function () {
      var open = !item.classList.contains("is-open");
      menus.forEach(function (m) {
        m.classList.remove("is-open");
        m.querySelector("button").setAttribute("aria-expanded", "false");
      });
      item.classList.toggle("is-open", open);
      knop.setAttribute("aria-expanded", String(open));
    });
  });

  document.addEventListener("click", function (e) {
    menus.forEach(function (m) {
      if (!m.contains(e.target)) {
        m.classList.remove("is-open");
        m.querySelector("button").setAttribute("aria-expanded", "false");
      }
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (html.classList.contains("menu-open")) {
      zetMenu(false);
      menuknop.focus();
    }
    menus.forEach(function (m) {
      if (m.classList.contains("is-open") || m.contains(document.activeElement)) {
        m.classList.remove("is-open");
        var knop = m.querySelector("button");
        knop.setAttribute("aria-expanded", "false");
        knop.focus();
      }
    });
  });

  /* Bereikbaarheid: open van 10.00 tot 22.00 uur (Nederlandse tijd) */
  var status = document.querySelector("[data-status]");
  if (status) {
    try {
      var uur = Number(
        new Intl.DateTimeFormat("nl-NL", { timeZone: "Europe/Amsterdam", hour: "numeric", hourCycle: "h23" }).format(new Date())
      );
      var open = uur >= 10 && uur < 22;
      status.classList.add(open ? "is-open" : "is-dicht");
      status.querySelector(".status__tekst").textContent = open
        ? "Nu bereikbaar, tot 22.00 uur"
        : "Vanaf 10.00 uur weer bereikbaar. Een appje sturen kan altijd.";
    } catch (e) {
      /* oude browser: de vaste tekst blijft staan */
    }
  }

  if (!("IntersectionObserver" in window)) {
    document.querySelectorAll(".stappen, .afspraken").forEach(function (s) {
      s.classList.add("is-zichtbaar");
    });
    return;
  }

  /* Schaduw onder de kopbalk zodra er gescrold is */
  var randje = document.createElement("div");
  randje.setAttribute("aria-hidden", "true");
  randje.style.cssText = "position:absolute;top:0;left:0;width:1px;height:8px;pointer-events:none";
  document.body.prepend(randje);
  new IntersectionObserver(function (items) {
    if (kop) kop.classList.toggle("is-gescrold", !items[0].isIntersecting);
  }).observe(randje);

  /* Snoer tussen de stappen trekt zich uit, vinkjes tikken aan: één keer, zodra het in beeld komt */
  var stapObs = new IntersectionObserver(
    function (items) {
      items.forEach(function (it) {
        if (it.isIntersecting) {
          it.target.classList.add("is-zichtbaar");
          stapObs.unobserve(it.target);
        }
      });
    },
    { threshold: 0.35 }
  );
  document.querySelectorAll(".stappen, .afspraken").forEach(function (s) {
    stapObs.observe(s);
  });

  /* Plakbalk met App en Bel: zichtbaar na de paginakop, weg bij de oproep onderaan */
  var plakbalk = document.querySelector(".plakbalk");
  var boven = document.querySelector(".hero, .paginakop");
  var onder = document.querySelector(".oproep");
  if (plakbalk && boven) {
    var bovenInBeeld = true;
    var onderInBeeld = false;
    var werkBij = function () {
      var zien = !bovenInBeeld && !onderInBeeld;
      plakbalk.classList.toggle("is-zichtbaar", zien);
      if (zien) {
        plakbalk.removeAttribute("inert");
      } else {
        plakbalk.setAttribute("inert", "");
      }
    };
    new IntersectionObserver(function (items) {
      bovenInBeeld = items[0].isIntersecting;
      werkBij();
    }).observe(boven);
    if (onder) {
      new IntersectionObserver(function (items) {
        onderInBeeld = items[0].isIntersecting;
        werkBij();
      }).observe(onder);
    }
  }
})();
