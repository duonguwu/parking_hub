document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#page-root");
  const header = document.querySelector("[data-header]");
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const mobileMenu = document.querySelector("[data-mobile-menu]");
  const video = document.querySelector("#technology-video");
  const videoSource = video?.querySelector("source");
  const videoTitle = document.querySelector("#video-title");
  const videoDescription = document.querySelector("#demo-description");
  const reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const cleanupCallbacks = [];
  const observers = [];
  const trackedAnimations = [];

  if (!root) return;

  const listen = (target, eventName, handler, options) => {
    target?.addEventListener(eventName, handler, options);
    cleanupCallbacks.push(() => target?.removeEventListener(eventName, handler, options));
  };

  let scrollFrame = 0;
  const updateHeader = () => {
    header?.classList.toggle("is-scrolled", window.scrollY > 18);
    scrollFrame = 0;
  };
  const onScroll = () => {
    if (!scrollFrame) scrollFrame = window.requestAnimationFrame(updateHeader);
  };
  updateHeader();
  listen(window, "scroll", onScroll, { passive: true });

  const setMenuState = (open, animate = true) => {
    if (!menuToggle || !mobileMenu) return;
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Đóng menu" : "Mở menu");
    document.body.classList.toggle("menu-open", open);

    if (open) {
      mobileMenu.hidden = false;
      if (animate && window.gsap) {
        const tween = window.gsap.fromTo(
          mobileMenu.children,
          { autoAlpha: 0, y: 14 },
          { autoAlpha: 1, y: 0, duration: 0.32, stagger: 0.04, ease: "power2.out", overwrite: "auto" }
        );
        trackedAnimations.push(tween);
      }
      mobileMenu.querySelector("a")?.focus({ preventScroll: true });
      return;
    }

    if (animate && window.gsap && !mobileMenu.hidden) {
      const tween = window.gsap.to(mobileMenu.children, {
        autoAlpha: 0,
        y: -8,
        duration: 0.18,
        stagger: 0.02,
        ease: "power1.in",
        overwrite: "auto",
        onComplete: () => {
          mobileMenu.hidden = true;
          window.gsap.set(mobileMenu.children, { clearProps: "all" });
        }
      });
      trackedAnimations.push(tween);
    } else {
      mobileMenu.hidden = true;
    }
  };

  listen(menuToggle, "click", () => {
    setMenuState(menuToggle.getAttribute("aria-expanded") !== "true");
  });

  listen(mobileMenu, "click", (event) => {
    if (event.target.closest("a")) {
      setMenuState(false);
    }
  });

  listen(document, "keydown", (event) => {
    if (event.key === "Escape" && menuToggle?.getAttribute("aria-expanded") === "true") {
      setMenuState(false);
      menuToggle.focus();
    }
  });

  const getTargetScrollTop = (target) => {
    if (!target || target.id === "top") return 0;
    const headerHeight = header?.offsetHeight ?? 0;
    const targetRect = target.getBoundingClientRect();
    const targetTop = window.scrollY + targetRect.top;
    const availableHeight = Math.max(0, window.innerHeight - headerHeight);
    const canCenter = targetRect.height <= availableHeight;
    const offset = canCenter
      ? headerHeight + (availableHeight - targetRect.height) / 2
      : headerHeight + 16;
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    return Math.min(maxScroll, Math.max(0, targetTop - offset));
  };

  const focusTargetHeading = (target) => {
    const heading = target?.matches("h1, h2, h3")
      ? target
      : target?.querySelector("h1, h2, h3");
    if (!heading) return;
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
    listen(heading, "blur", () => heading.removeAttribute("tabindex"), { once: true });
  };

  const anchorLinks = Array.from(root.querySelectorAll('a[href^="#"]'));
  anchorLinks.forEach((link) => {
    listen(link, "click", (event) => {
      if (link.classList.contains("skip-link")) return;
      const targetId = link.getAttribute("href");
      if (!targetId || targetId === "#") return;
      const target = document.querySelector(targetId);
      if (!target) return;
      event.preventDefault();
      const top = getTargetScrollTop(target);
      window.scrollTo({
        top,
        behavior: reduceMotionQuery.matches ? "auto" : "smooth"
      });
      window.history.pushState(null, "", targetId);
      focusTargetHeading(target);
    });
  });

  if (window.location.hash) {
    const initialTarget = document.querySelector(window.location.hash);
    if (initialTarget) {
      window.requestAnimationFrame(() => {
        window.scrollTo({ top: getTargetScrollTop(initialTarget), behavior: "auto" });
      });
    }
  }

  const primaryNavLinks = Array.from(
    root.querySelectorAll('.desktop-nav a[href^="#"], .mobile-menu > a[href^="#"]')
  );
  const navSections = primaryNavLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter((section, index, sections) => section && sections.indexOf(section) === index);

  if ("IntersectionObserver" in window) {
    const navObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        primaryNavLinks.forEach((link) => {
          const current = link.getAttribute("href") === `#${visible.target.id}`;
          if (current) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      },
      { rootMargin: "-34% 0px -48%", threshold: [0, 0.1, 0.35] }
    );
    navSections.forEach((section) => navObserver.observe(section));
    observers.push(navObserver);
  }

  const videoTabs = window.gsap
    ? window.gsap.utils.toArray("[data-video]", root)
    : Array.from(root.querySelectorAll("[data-video]"));

  const selectVideo = (tab, moveFocus = false) => {
    if (!tab || !video || !videoSource) return;

    videoTabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute("aria-selected", String(selected));
      item.tabIndex = selected ? 0 : -1;
    });

    video.pause();
    videoSource.src = tab.dataset.video;
    video.poster = tab.dataset.poster;
    video.load();
    if (videoTitle) videoTitle.textContent = tab.dataset.title;
    if (videoDescription) videoDescription.textContent = tab.dataset.description;

    if (window.gsap && !reduceMotionQuery.matches) {
      const tween = window.gsap.fromTo(
        video.closest(".video-stage"),
        { autoAlpha: 0.55, scale: 0.985 },
        { autoAlpha: 1, scale: 1, duration: 0.3, ease: "power2.out", overwrite: "auto" }
      );
      trackedAnimations.push(tween);
    }

    if (moveFocus) tab.focus();
  };

  videoTabs.forEach((tab, index) => {
    tab.tabIndex = index === 0 ? 0 : -1;
    listen(tab, "click", () => selectVideo(tab));
    listen(tab, "keydown", (event) => {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
      event.preventDefault();
      const direction = event.key === "ArrowRight" ? 1 : -1;
      const nextIndex = window.gsap
        ? window.gsap.utils.wrap(0, videoTabs.length, index + direction)
        : (index + direction + videoTabs.length) % videoTabs.length;
      selectVideo(videoTabs[nextIndex], true);
    });
  });

  if (!window.gsap) return;

  const { gsap } = window;
  const pageContext = gsap.context(() => {
    gsap.defaults({ duration: 0.52, ease: "power2.out" });
  }, root);

  const media = gsap.matchMedia();
  media.add(
    {
      desktop: "(min-width: 1024px)",
      reduceMotion: "(prefers-reduced-motion: reduce)"
    },
    (context) => {
      const { desktop, reduceMotion } = context.conditions;
      const heroTargets = gsap.utils.toArray(
        ".hero-kicker, #hero-title, .hero-mantra, .hero-description, .hero-actions, .hero-values",
        root
      );
      const heroImage = root.querySelector(".hero-media img");

      if (reduceMotion) {
        gsap.set(heroTargets, { autoAlpha: 1, x: 0, y: 0, clearProps: "transform,visibility" });
        gsap.set(heroImage, { autoAlpha: 1, x: 0, y: 0, scale: 1, clearProps: "transform,visibility" });
        return;
      }

      const heroTimeline = gsap.timeline({
        defaults: { ease: "power3.out" }
      });
      heroTimeline
        .addLabel("heroIn", 0)
        .from(heroImage, {
          autoAlpha: 0,
          x: desktop ? 24 : 0,
          scale: 1.085,
          duration: 1.15,
          clearProps: "transform,visibility"
        }, "heroIn")
        .from(heroTargets, {
          autoAlpha: 0,
          y: 26,
          duration: 0.62,
          stagger: 0.07,
          clearProps: "transform,visibility"
        }, "heroIn+=0.18");
      trackedAnimations.push(heroTimeline);

      if (!desktop) return;

      const visual = root.querySelector(".hero");
      if (!visual || !heroImage) return;

      const clamp = gsap.utils.clamp(-7, 7);
      const mapX = gsap.utils.mapRange(0, 1, -6, 6);
      const mapY = gsap.utils.mapRange(0, 1, -4, 4);
      const moveX = gsap.quickTo(heroImage, "x", { duration: 0.65, ease: "power2.out" });
      const moveY = gsap.quickTo(heroImage, "y", { duration: 0.65, ease: "power2.out" });

      const onPointerMove = (event) => {
        const bounds = visual.getBoundingClientRect();
        const progressX = gsap.utils.normalize(bounds.left, bounds.right, event.clientX);
        const progressY = gsap.utils.normalize(bounds.top, bounds.bottom, event.clientY);
        const x = clamp(mapX(progressX));
        const y = clamp(mapY(progressY));
        moveX(x);
        moveY(y);
      };
      const onPointerLeave = () => {
        moveX(0);
        moveY(0);
      };

      visual.addEventListener("pointermove", onPointerMove, { passive: true });
      visual.addEventListener("pointerleave", onPointerLeave);
      return () => {
        visual.removeEventListener("pointermove", onPointerMove);
        visual.removeEventListener("pointerleave", onPointerLeave);
      };
    },
    root
  );

  const reduceMotion = reduceMotionQuery.matches;
  const revealGroups = gsap.utils.toArray(".reveal-group", root);

  if (reduceMotion || !("IntersectionObserver" in window)) {
    gsap.set(revealGroups, { autoAlpha: 1, y: 0 });
  } else {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const children = entry.target.children.length
            ? gsap.utils.toArray(entry.target.children)
            : [entry.target];
          const tween = gsap.fromTo(
            children,
            { autoAlpha: 0, y: 18 },
            {
              autoAlpha: 1,
              y: 0,
              duration: 0.46,
              stagger: { each: 0.045, from: "start" },
              ease: "power2.out",
              overwrite: "auto",
              clearProps: "transform,visibility"
            }
          );
          trackedAnimations.push(tween);
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -10%", threshold: 0.12 }
    );

    revealGroups.forEach((group) => revealObserver.observe(group));
    observers.push(revealObserver);
  }

  const cleanup = () => {
    if (scrollFrame) window.cancelAnimationFrame(scrollFrame);
    observers.forEach((observer) => observer.disconnect());
    trackedAnimations.forEach((animation) => animation?.kill());
    cleanupCallbacks.forEach((callback) => callback());
    media.revert();
    pageContext.revert();
  };

  window.addEventListener("pagehide", cleanup, { once: true });
});
