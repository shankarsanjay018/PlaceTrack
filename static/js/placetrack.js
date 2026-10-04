document.addEventListener("DOMContentLoaded", () => {

    // Slide content into the page when it opens
    const main = document.querySelector(".pt-main");

    if (main) {
        main.classList.add("page-enter");

        const sections = main.children;

        Array.from(sections).forEach((section, index) => {
            section.style.animationDelay = `${index * 0.08}s`;
            section.classList.add("section-slide");
        });
    }


    // Slide page out before navigating
    const navigationLinks = document.querySelectorAll(".pt-nav a");

    navigationLinks.forEach(link => {

        link.addEventListener("click", function(event) {

            const href = this.getAttribute("href");

            // Ignore links that don't navigate to another page
            if (!href || href.startsWith("#")) {
                return;
            }

            event.preventDefault();

            const main = document.querySelector(".pt-main");

            if (main) {

                main.classList.remove("page-enter");
                main.classList.add("page-exit");

                setTimeout(() => {
                    window.location.href = href;
                }, 250);

            } else {
                window.location.href = href;
            }

        });

    });

});