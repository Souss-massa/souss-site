// Souss — multi-page interactions: nav, reveals, filters, contact form
(function () {
  "use strict";

  // Mobile navigation
  var toggle = document.getElementById("navToggle");
  var links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Active nav link for current page
  var page = document.body.getAttribute("data-page");
  if (page) {
    document.querySelectorAll('.nav-links a[data-nav="' + page + '"]').forEach(function (a) {
      a.classList.add("active");
    });
  }

  // Reveal on scroll
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("visible"); });
  }

  // Personality filter chips (personnalites.html)
  var filterBar = document.getElementById("filterBar");
  if (filterBar) {
    var chips = filterBar.querySelectorAll(".chip");
    var people = function () { return document.querySelectorAll("#people .person"); };
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.classList.remove("active"); });
        chip.classList.add("active");
        var f = chip.getAttribute("data-filter");
        people().forEach(function (p) {
          var cats = (p.getAttribute("data-cat") || "").split(/\s+/);
          var show = f === "all" || cats.indexOf(f) !== -1;
          p.classList.toggle("hidden", !show);
          if (show) p.classList.add("visible");
        });
      });
    });
  }

  // Contact form (client-side demo validation)
  var form = document.getElementById("contactForm");
  if (form) {
    var status = document.getElementById("formStatus");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.elements.name;
      var email = form.elements.email;
      var msg = form.elements.message;
      var ok = true;
      [name, email, msg].forEach(function (f) { f.classList.remove("invalid"); });
      if (!name.value.trim()) { name.classList.add("invalid"); ok = false; }
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim())) { email.classList.add("invalid"); ok = false; }
      if (!msg.value.trim()) { msg.classList.add("invalid"); ok = false; }
      if (!ok) {
        status.textContent = "Merci de remplir tous les champs (e-mail valide requis).";
        status.className = "form-status err";
        return;
      }
      status.textContent = "Merci " + name.value.trim() + " ! Votre message a bien été pris en compte (démo locale).";
      status.className = "form-status ok";
      form.reset();
    });
  }

  // Community contributions from content/personnalites.json (merged PRs)
  var peopleHost = document.getElementById("people");
  if (peopleHost) {
    fetch("content/personnalites.json")
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (list) {
        if (!Array.isArray(list) || !list.length) return;
        list.forEach(function (p) {
          var art = document.createElement("article");
          art.className = "person reveal visible";
          art.id = p.id || "";
          art.setAttribute("data-cat", (p.cats || []).join(" "));
          var photo = '<div class="person-photo' + (p.image ? " has-img" : "") + '">';
          if (p.image && p.image.src) {
            photo += '<img src="' + p.image.src + '" alt="' + (p.image.alt || p.name) + '" loading="lazy">';
          }
          photo += '<span class="person-initials">' + (p.initials || "") + "</span>";
          if (p.image && p.image.credit) {
            photo += '<span class="photo-credit">' + p.image.credit + "</span>";
          }
          photo += "</div>";
          var works = p.works ? '<p class="person-works"><strong>Œuvres marquantes :</strong> ' + p.works + "</p>" : "";
          art.innerHTML =
            photo +
            '<div class="person-body">' +
            "<h3>" + p.name + ' <span class="person-tag">' + p.tag + ' · contribution</span></h3>' +
            '<p class="person-meta">' + p.meta + "</p>" +
            "<p>" + p.bio + "</p>" + works +
            "</div>";
          peopleHost.appendChild(art);
        });
      })
      .catch(function () { /* no contributions file: fine */ });
  }
})();
