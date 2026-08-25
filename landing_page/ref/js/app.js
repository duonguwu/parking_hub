/* =====================================================
   DPSG Talkshow — GSAP motion
   ===================================================== */

// Guard: if the GSAP CDN failed to load, make sure nothing stays hidden.
if (typeof gsap === "undefined") {
    document.documentElement.classList.remove("gsap-ready");
    console.warn("GSAP failed to load — animations skipped, content shown.");
} else {
    run();
}

function run() {
    gsap.registerPlugin(ScrollTrigger);

    /* ---- Nav & Floating Action Scroll Handler ---- */
    const nav = document.querySelector(".nav");
    const backToTop = document.querySelector(".float-btn--top");
    
    if (nav || backToTop) {
        if (nav) nav.classList.add("nav--top");

        ScrollTrigger.create({
            start: "top top",
            onUpdate: (self) => {
                const scrolled = self.scroll();
                
                if (nav) {
                    if (scrolled > 30) {
                        nav.classList.remove("nav--top");
                    } else {
                        nav.classList.add("nav--top");
                    }
                }

                if (backToTop) {
                    if (scrolled > 300) {
                        backToTop.classList.add("is-visible");
                    } else {
                        backToTop.classList.remove("is-visible");
                    }
                }
            }
        });
    }

    const mm = gsap.matchMedia();

    mm.add(
        {
            motion: "(prefers-reduced-motion: no-preference)",
            reduce: "(prefers-reduced-motion: reduce)",
        },
        (ctx) => {
            const { reduce } = ctx.conditions;

            // If reduced motion, just show everything and bail.
            if (reduce) {
                gsap.set(".reveal", { opacity: 1, y: 0 });
                gsap.set("[data-hero='line'], [data-hero='kicker'], [data-hero='block']", { opacity: 1, y: 0 });
                gsap.set(".timeline-track .progress", { scaleY: 1 });
                gsap.set(".tl-dot", { scale: 1 });
                document.querySelectorAll(".count").forEach((el) => {
                    el.textContent = el.dataset.to;
                });
                return;
            }

            gsap.defaults({ ease: "power3.out", duration: 0.9 });

            /* ---- HERO load timeline ---- */
            const heroTl = gsap.timeline({ delay: 0.15 });

            heroTl
                .from("[data-hero='photo']", { autoAlpha: 0, scale: 1.08, xPercent: 6, duration: 1.4, ease: "power3.out" })
                .from("[data-hero='kicker']", { y: 14, opacity: 0, duration: 0.6, stagger: 0.1 }, 0.25)
                .from(
                    "[data-hero='line']",
                    { yPercent: 115, duration: 1, stagger: 0.12, ease: "power4.out" },
                    "-=0.35"
                )
                .add(() => {
                    // Draw the light-blue underline behind "giảng đường" (CSS transition)
                    document.querySelector(".hero-headline .mark-word")?.classList.add("is-drawn");
                }, "-=0.35")
                .from(
                    "[data-hero='block']",
                    { y: 24, opacity: 0, duration: 0.8, stagger: 0.12 },
                    "-=0.5"
                );

            /* ---- Generic reveals (exclude speaker cards; they batch separately) ---- */
            gsap.utils.toArray(".reveal:not(.sp-card)").forEach((el) => {
                gsap.fromTo(
                    el,
                    { y: 30, opacity: 0 },
                    {
                        y: 0,
                        opacity: 1,
                        duration: 0.9,
                        scrollTrigger: {
                            trigger: el,
                            start: "top 88%",
                            toggleActions: "play none none none",
                        },
                    }
                );
            });

            /* ---- Speaker cards: staggered batch reveal ---- */
            gsap.set(".sp-card", { opacity: 0, y: 40 });
            ScrollTrigger.batch(".sp-card", {
                start: "top 90%",
                onEnter: (batch) =>
                    gsap.to(batch, {
                        y: 0,
                        opacity: 1,
                        duration: 0.7,
                        stagger: 0.08,
                        overwrite: true,
                    }),
            });

            /* ---- Stat count-up ---- */
            gsap.utils.toArray(".count").forEach((el) => {
                const target = parseFloat(el.dataset.to);
                const obj = { val: 0 };
                ScrollTrigger.create({
                    trigger: el,
                    start: "top 85%",
                    once: true,
                    onEnter: () => {
                        gsap.to(obj, {
                            val: target,
                            duration: 1.4,
                            ease: "power2.out",
                            onUpdate: () => {
                                el.textContent = Math.round(obj.val);
                            },
                        });
                    },
                });
            });

            /* ---- Timeline: draw progress line + pop dots on scroll ---- */
            gsap.to(".timeline-track .progress", {
                scaleY: 1,
                ease: "none",
                scrollTrigger: {
                    trigger: ".timeline-wrap",
                    start: "top 70%",
                    end: "bottom 80%",
                    scrub: 0.6,
                },
            });

            gsap.utils.toArray(".tl-dot").forEach((dot) => {
                gsap.to(dot, {
                    scale: 1,
                    duration: 0.4,
                    ease: "back.out(2)",
                    scrollTrigger: {
                        trigger: dot,
                        start: "top 80%",
                        toggleActions: "play none none none",
                    },
                });
            });

            /* ---- Subtle parallax on the hero photo as you scroll ---- */
            gsap.to("[data-hero='photo'] img", {
                yPercent: 10,
                ease: "none",
                scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true },
            });

            /* ---- Failsafe: never leave above-the-fold content hidden ---- */
            gsap.delayedCall(3.5, () => {
                gsap.set("[data-hero='photo'], [data-hero='line'], [data-hero='kicker'], [data-hero='block']", {
                    clearProps: "transform,opacity,visibility",
                });
            });

            return () => { };
        }
    );

    // FAQ Accordion
    const faqItems = document.querySelectorAll(".faq-item");
    faqItems.forEach((item) => {
        const trigger = item.querySelector(".faq-trigger");
        const answer = item.querySelector(".faq-answer");
        
        trigger.addEventListener("click", () => {
            const isExpanded = trigger.getAttribute("aria-expanded") === "true";
            
            // Close all other FAQ items
            faqItems.forEach((otherItem) => {
                if (otherItem !== item) {
                    const otherTrigger = otherItem.querySelector(".faq-trigger");
                    const otherAnswer = otherItem.querySelector(".faq-answer");
                    otherTrigger.setAttribute("aria-expanded", "false");
                    otherAnswer.style.height = "0px";
                }
            });
            
            if (isExpanded) {
                trigger.setAttribute("aria-expanded", "false");
                answer.style.height = "0px";
            } else {
                trigger.setAttribute("aria-expanded", "true");
                answer.style.height = `${answer.scrollHeight}px`;
            }
        });
    });

    // Floating back-to-top button click handler
    if (backToTop) {
        backToTop.addEventListener("click", (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    /* ---- Google Form Modal (time-gated) ---- */
    const formModal = document.getElementById("formModal");
    const formModalClose = document.getElementById("formModalClose");
    const openBtns = document.querySelectorAll("[data-open-form]");
    const formCountdown = document.getElementById("formCountdown");
    const formContent = document.getElementById("formContent");
    const formIframe = document.getElementById("formIframe");

    // Form opens at 19:55 Vietnam time (UTC+7) on June 25, 2026
    // Using UTC: 19:55 UTC+7 = 12:55 UTC
    const FORM_OPEN_TIME = new Date("2026-06-25T12:55:00Z").getTime();
    const FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc-Uixf8MKZEsKEjq1Dobg5cY3imFBf-iexWxIfdETOTFRXVQ/viewform?embedded=true";

    function isFormOpen() {
        return Date.now() >= FORM_OPEN_TIME;
    }

    function updateCountdown() {
        const now = Date.now();
        const diff = FORM_OPEN_TIME - now;

        if (diff <= 0) {
            // Time's up — switch to form view
            switchToForm();
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const secs = Math.floor((diff % (1000 * 60)) / 1000);

        const pad = (n) => String(n).padStart(2, "0");
        document.getElementById("cdDays").textContent = pad(days);
        document.getElementById("cdHours").textContent = pad(hours);
        document.getElementById("cdMins").textContent = pad(mins);
        document.getElementById("cdSecs").textContent = pad(secs);
    }

    function switchToForm() {
        if (formCountdown) formCountdown.style.display = "none";
        if (formContent) formContent.style.display = "flex";
        if (formIframe && !formIframe.src) {
            formIframe.src = FORM_URL;
        }
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
        }
    }

    // Initialize: check if form is already open
    let countdownInterval = null;
    if (isFormOpen()) {
        switchToForm();
    } else {
        updateCountdown();
        countdownInterval = setInterval(updateCountdown, 1000);
    }

    function openFormModal(e) {
        if (e) e.preventDefault();
        formModal.classList.add("is-open");
        document.body.classList.add("modal-open");

        // Load iframe on first open (only if form is open)
        if (isFormOpen() && formIframe && !formIframe.src) {
            formIframe.src = FORM_URL;
        }
    }

    function closeFormModal() {
        formModal.classList.remove("is-open");
        document.body.classList.remove("modal-open");
    }

    openBtns.forEach((btn) => btn.addEventListener("click", openFormModal));

    if (formModalClose) {
        formModalClose.addEventListener("click", closeFormModal);
    }

    // Close on backdrop click
    if (formModal) {
        formModal.addEventListener("click", (e) => {
            if (e.target === formModal) closeFormModal();
        });
    }

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && formModal.classList.contains("is-open")) {
            closeFormModal();
        }
    });
}
