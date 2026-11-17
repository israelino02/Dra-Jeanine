/* Dra. Jeanine Carneiro: comportamento do site.
   Sem dependências. Nada de dado de saúde vai para a camada de dados:
   só página, posição do botão e público (infantil/adulto/programa). */
(function () {
  "use strict";
  var dl = (window.dataLayer = window.dataLayer || []);
  var pagina = location.pathname;

  /* ---------- origem da campanha → mensagem do WhatsApp ----------
     Guarda utm_campaign/utm_source da primeira página da visita e acrescenta
     um código curto à mensagem, para a equipe registrar de onde veio o
     contato. Sobrevive a bloqueador e a recusa de cookies. */
  var origem = "";
  try {
    var q = new URLSearchParams(location.search);
    var camp = q.get("utm_campaign") || q.get("utm_source") || (q.get("gclid") ? "google" : "") || (q.get("fbclid") ? "meta" : "");
    if (camp) sessionStorage.setItem("jc_origem", camp.slice(0, 40));
    origem = sessionStorage.getItem("jc_origem") || "";
  } catch (e) {}
  if (origem) {
    document.querySelectorAll('a[href^="https://wa.me/"]').forEach(function (a) {
      try {
        var u = new URL(a.href);
        var t = u.searchParams.get("text") || "";
        u.searchParams.set("text", t + " [ref: " + origem + "]");
        a.href = u.toString();
      } catch (e) {}
    });
  }

  /* ---------- eventos ---------- */
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("a");
    if (!a) return;
    if (a.dataset.wa) {
      dl.push({ event: "whatsapp_click", pagina: pagina, posicao: a.dataset.wa, publico: a.dataset.publico || "" });
    } else if (a.dataset.maps) {
      dl.push({ event: "maps_click", pagina: pagina, posicao: a.dataset.maps });
    }
  });
  document.querySelectorAll(".faq details").forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (d.open) dl.push({ event: "faq_open", pagina: pagina, pergunta: d.querySelector("summary").textContent.slice(0, 90) });
    });
  });

  var io = "IntersectionObserver" in window;
  var calmo = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var proto = document.querySelector('[data-track="protocolo"]');
  if (proto && io) {
    var po = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { dl.push({ event: "scroll_protocolo", pagina: pagina }); po.disconnect(); }
    }, { threshold: 0.3 });
    po.observe(proto);
  }

  /* ---------- entrada suave (desliga com prefers-reduced-motion) ---------- */
  var els = document.querySelectorAll(".reveal");
  if (!io || calmo) {
    els.forEach(function (el) { el.classList.add("seen"); });
  } else {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("seen"); ro.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    els.forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 70 + "ms"; ro.observe(el); });
  }

  /* ---------- cabeçalho e menu ---------- */
  var head = document.querySelector(".site-header");
  var onScroll = function () { head && head.classList.toggle("scrolled", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    var fechar = function () { nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); btn.setAttribute("aria-label", "Abrir menu"); };
    btn.addEventListener("click", function () {
      var aberto = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", aberto ? "true" : "false");
      btn.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) fechar(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") fechar(); });
  }

  /* ---------- mapa do Google (LGPD) ----------
     O iframe do Google Maps grava cookies de terceiros. Por isso ele só
     carrega com clique em "Mostrar mapa" ou depois de a pessoa aceitar. */
  var carregarMapas = function () {
    document.querySelectorAll("[data-map]").forEach(function (m) {
      if (m.classList.contains("loaded")) return;
      var f = document.createElement("iframe");
      f.src = m.getAttribute("data-map");
      f.title = "Mapa do consultório no Google Maps";
      f.loading = "lazy";
      f.referrerPolicy = "no-referrer-when-downgrade";
      f.setAttribute("allowfullscreen", "");
      m.appendChild(f);
      m.classList.add("loaded");
      dl.push({ event: "mapa_aberto", pagina: pagina });
    });
  };
  document.addEventListener("click", function (e) {
    if (e.target.closest && e.target.closest("[data-map-load]")) carregarMapas();
  });

  /* ---------- botão flutuante de WhatsApp ----------
     Sempre visível. Enquanto o aviso de privacidade está aberto,
     sobe para não ficar por cima dele. */
  var fab = document.querySelector(".wa-fab");
  var ajustarFab = function () {
    if (!fab) return;
    var box = document.getElementById("cookie");
    var aberto = box && !box.hidden;
    fab.style.bottom = aberto ? "calc(" + (box.offsetHeight + 24) + "px + env(safe-area-inset-bottom))" : "";
  };
  window.addEventListener("resize", ajustarFab);

  /* ---------- abas por idade (teclado: setas, Home, End) ----------
     Sem JS, todos os painéis aparecem um embaixo do outro. */
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    var abrir = function (t, foco) {
      tabs.forEach(function (x) {
        var on = x === t;
        x.setAttribute("aria-selected", on ? "true" : "false");
        x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
      });
      if (foco) t.focus();
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { abrir(t); });
      t.addEventListener("keydown", function (e) {
        var n = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
        if (n === undefined) return;
        e.preventDefault();
        abrir(tabs[(n + tabs.length) % tabs.length], true);
      });
    });
    abrir(tabs[0]);
  });

  /* ---------- frases tocáveis ----------
     A mãe marca o que vive e recebe um retorno curto. Nada disso vai para a
     camada de dados nem sai do navegador (é informação de saúde). */
  document.querySelectorAll("[data-chips]").forEach(function (grupo) {
    var out = grupo.parentNode.querySelector("[data-chips-out]");
    var msg = out && out.querySelector("[data-chips-msg]");
    var chips = grupo.querySelectorAll(".chip");
    var atualizar = function () {
      var n = grupo.querySelectorAll('.chip[aria-pressed="true"]').length;
      if (!out) return;
      out.setAttribute("data-n", n);
      msg.innerHTML = n === 0
        ? "Toque nas frases que fazem parte da sua rotina."
        : n < 3
          ? "<b>" + n + "</b> de " + chips.length + ". Vale conversar com uma médica para entender o que está por trás."
          : "<b>" + n + "</b> de " + chips.length + ". Não é um diagnóstico, mas é motivo para uma avaliação cuidadosa.";
    };
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        c.setAttribute("aria-pressed", c.getAttribute("aria-pressed") === "true" ? "false" : "true");
        atualizar();
      });
    });
  });

  /* ---------- consentimento (LGPD) ---------- */
  var box = document.getElementById("cookie");
  var salvo = null;
  try { salvo = localStorage.getItem("jc_consent"); } catch (e) {}
  if (box && !salvo) box.hidden = false;
  if (salvo === "aceito") carregarMapas();
  ajustarFab();
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-consent],[data-cookie-prefs]");
    if (!b) return;
    if (b.hasAttribute("data-cookie-prefs")) { if (box) box.hidden = false; ajustarFab(); return; }
    var v = b.getAttribute("data-consent");
    try { localStorage.setItem("jc_consent", v); } catch (err) {}
    var g = v === "aceito" ? "granted" : "denied";
    if (typeof gtag === "function") {
      gtag("consent", "update", { ad_storage: g, analytics_storage: g, ad_user_data: g, ad_personalization: "denied" });
    }
    if (v === "aceito") { dl.push({ event: "consent_accept" }); carregarMapas(); }
    if (box) box.hidden = true;
    ajustarFab();
  });
})();
