/* =========================================================
   PLACETRACK
   BRIGHT COLORFUL INTERACTIVE PARTICLE BACKGROUND

   ✔ Bright colorful particles
   ✔ No halo/glow around individual particles
   ✔ Many particles
   ✔ Mouse interaction
   ✔ Soft ambient background light
   ✔ Purple / pink / violet / magenta theme
========================================================= */

(() => {

    const canvas =
        document.getElementById("placement-bg");

    if (!canvas) {
        return;
    }

    const ctx =
        canvas.getContext("2d");

    let width = 0;
    let height = 0;

    let dpr =
        Math.min(
            window.devicePixelRatio || 1,
            2
        );


    /* =====================================================
       MOUSE
    ===================================================== */

    const mouse = {

        x: -1000,

        y: -1000,

        active: false,

        radius: 220
    };


    /* =====================================================
       SETTINGS
    ===================================================== */

    const DESKTOP_PARTICLES = 230;

    const MOBILE_PARTICLES = 125;

    const CONNECTION_DISTANCE = 135;


    const particles = [];

    const lightSources = [];


    /* =====================================================
       RESIZE
    ===================================================== */

    function resize() {

        dpr =
            Math.min(
                window.devicePixelRatio || 1,
                2
            );

        width =
            window.innerWidth;

        height =
            window.innerHeight;


        canvas.width =
            width * dpr;

        canvas.height =
            height * dpr;


        canvas.style.width =
            width + "px";

        canvas.style.height =
            height + "px";


        ctx.setTransform(
            dpr,
            0,
            0,
            dpr,
            0,
            0
        );
    }


    /* =====================================================
       AMBIENT LIGHT
       Large soft lights only.
       No visible dot.
    ===================================================== */

    class LightSource {

        constructor(
            x,
            y,
            radius,
            color,
            intensity,
            moveX,
            moveY
        ) {

            this.baseX = x;

            this.baseY = y;

            this.x = x;

            this.y = y;

            this.radius = radius;

            this.color = color;

            this.intensity =
                intensity;

            this.moveX =
                moveX;

            this.moveY =
                moveY;

            this.phase =
                Math.random() *
                Math.PI *
                2;

            this.speed =
                0.0015 +
                Math.random() *
                0.0015;
        }


        update() {

            this.phase +=
                this.speed;


            this.x =
                this.baseX +
                Math.sin(
                    this.phase
                ) *
                this.moveX;


            this.y =
                this.baseY +
                Math.cos(
                    this.phase * 0.8
                ) *
                this.moveY;
        }


        draw() {

            const c =
                this.color;


            const gradient =
                ctx.createRadialGradient(
                    this.x,
                    this.y,
                    0,
                    this.x,
                    this.y,
                    this.radius
                );


            gradient.addColorStop(
                0,
                `rgba(
                    ${c.r},
                    ${c.g},
                    ${c.b},
                    ${this.intensity}
                )`
            );


            gradient.addColorStop(
                0.35,
                `rgba(
                    ${c.r},
                    ${c.g},
                    ${c.b},
                    ${this.intensity * 0.45}
                )`
            );


            gradient.addColorStop(
                1,
                `rgba(
                    ${c.r},
                    ${c.g},
                    ${c.b},
                    0
                )`
            );


            ctx.beginPath();

            ctx.fillStyle =
                gradient;

            ctx.arc(
                this.x,
                this.y,
                this.radius,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }
    }


    /* =====================================================
       PARTICLE
       BRIGHT + COLORFUL
       NO INDIVIDUAL GLOW
    ===================================================== */

    class Particle {

        constructor() {

            this.x =
                Math.random() *
                width;

            this.y =
                Math.random() *
                height;


            this.vx =
                (Math.random() - 0.5) *
                0.28;

            this.vy =
                (Math.random() - 0.5) *
                0.28;


            /* Slightly larger */

            this.size =
                Math.random() *
                1.7 +
                0.8;


            /* BRIGHT */

            this.alpha =
                Math.random() *
                0.35 +
                0.65;


            this.phase =
                Math.random() *
                Math.PI *
                2;


            this.phaseSpeed =
                Math.random() *
                0.012 +
                0.004;


            /* =================================================
               VIBRANT COLORS
            ================================================= */

            const colors = [

                /* Purple */

                {
                    r: 139,
                    g: 92,
                    b: 246
                },


                /* Bright Violet */

                {
                    r: 167,
                    g: 139,
                    b: 250
                },


                /* Magenta */

                {
                    r: 217,
                    g: 70,
                    b: 239
                },


                /* Pink */

                {
                    r: 244,
                    g: 114,
                    b: 182
                },


                /* Hot Pink */

                {
                    r: 236,
                    g: 72,
                    b: 153
                },


                /* Lavender */

                {
                    r: 196,
                    g: 181,
                    b: 253
                },


                /* Warm accent */

                {
                    r: 251,
                    g: 146,
                    b: 60
                }

            ];


            this.color =
                colors[
                    Math.floor(
                        Math.random() *
                        colors.length
                    )
                ];
        }


        update() {

            this.phase +=
                this.phaseSpeed;


            /* Natural movement */

            this.vx +=
                Math.sin(
                    this.phase
                ) *
                0.001;

            this.vy +=
                Math.cos(
                    this.phase * 0.8
                ) *
                0.001;


            /* =================================================
               MOUSE PUSH
            ================================================= */

            if (mouse.active) {

                const dx =
                    this.x -
                    mouse.x;

                const dy =
                    this.y -
                    mouse.y;


                const distance =
                    Math.sqrt(
                        dx * dx +
                        dy * dy
                    );


                if (
                    distance <
                    mouse.radius
                ) {

                    const force =
                        1 -
                        distance /
                        mouse.radius;


                    const angle =
                        Math.atan2(
                            dy,
                            dx
                        );


                    this.vx +=
                        Math.cos(angle) *
                        force *
                        0.025;


                    this.vy +=
                        Math.sin(angle) *
                        force *
                        0.025;

                }

            }


            /* =================================================
               SPEED
            ================================================= */

            const maxSpeed =
                0.65;


            this.vx =
                Math.max(-maxSpeed,
                    Math.min(
                        maxSpeed,
                        this.vx
                    )
                );


            this.vy =
                Math.max(-maxSpeed,
                    Math.min(
                        maxSpeed,
                        this.vy
                    )
                );


            this.x +=
                this.vx;

            this.y +=
                this.vy;


            /* =================================================
               WRAP
            ================================================= */

            if (
                this.x < -10
            ) {

                this.x =
                    width + 10;

            }


            if (
                this.x >
                width + 10
            ) {

                this.x = -10;

            }


            if (
                this.y < -10
            ) {

                this.y =
                    height + 10;

            }


            if (
                this.y >
                height + 10
            ) {

                this.y = -10;

            }

        }


        draw() {

            const c =
                this.color;


            /* =================================================
               IMPORTANT:
               NO RADIAL GRADIENT HERE.
               PARTICLE ITSELF IS BRIGHT.
            ================================================= */

            ctx.beginPath();


            ctx.fillStyle =
                `rgba(
                    ${c.r},
                    ${c.g},
                    ${c.b},
                    ${this.alpha}
                )`;


            ctx.arc(
                this.x,
                this.y,
                this.size,
                0,
                Math.PI * 2
            );


            ctx.fill();
        }
    }


    /* =====================================================
       LIGHT SOURCES
    ===================================================== */

    function createLightSources() {

        lightSources.length = 0;


        /* Top left purple */

        lightSources.push(
            new LightSource(
                width * 0.15,
                height * 0.16,
                390, {
                    r: 124,
                    g: 58,
                    b: 237
                },
                0.11,
                80,
                55
            )
        );


        /* Top middle magenta */

        lightSources.push(
            new LightSource(
                width * 0.48,
                height * 0.19,
                430, {
                    r: 217,
                    g: 70,
                    b: 239
                },
                0.085,
                90,
                50
            )
        );


        /* Right pink */

        lightSources.push(
            new LightSource(
                width * 0.83,
                height * 0.38,
                360, {
                    r: 236,
                    g: 72,
                    b: 153
                },
                0.075,
                70,
                65
            )
        );


        /* Bottom purple */

        lightSources.push(
            new LightSource(
                width * 0.43,
                height * 0.82,
                440, {
                    r: 139,
                    g: 92,
                    b: 246
                },
                0.075,
                80,
                60
            )
        );


        /* Bottom right magenta */

        lightSources.push(
            new LightSource(
                width * 0.82,
                height * 0.83,
                330, {
                    r: 192,
                    g: 38,
                    b: 211
                },
                0.065,
                65,
                60
            )
        );
    }


    /* =====================================================
       CREATE PARTICLES
    ===================================================== */

    function createParticles() {

        particles.length = 0;


        const count =
            window.innerWidth < 700 ?
            MOBILE_PARTICLES :
            DESKTOP_PARTICLES;


        for (
            let i = 0; i < count; i++
        ) {

            particles.push(
                new Particle()
            );
        }
    }


    /* =====================================================
       BASE
    ===================================================== */

    function drawBase() {

        ctx.fillStyle =
            "#07060d";


        ctx.fillRect(
            0,
            0,
            width,
            height
        );
    }


    /* =====================================================
       GRID
    ===================================================== */

    function drawGrid() {

        const size =
            44;


        ctx.strokeStyle =
            "rgba(177,130,240,0.028)";


        ctx.lineWidth =
            1;


        ctx.beginPath();


        for (
            let x = 0; x <= width; x += size
        ) {

            ctx.moveTo(
                x,
                0
            );

            ctx.lineTo(
                x,
                height
            );
        }


        for (
            let y = 0; y <= height; y += size
        ) {

            ctx.moveTo(
                0,
                y
            );

            ctx.lineTo(
                width,
                y
            );
        }


        ctx.stroke();
    }


    /* =====================================================
       CONNECTIONS
    ===================================================== */

    function drawConnections() {

        for (
            let i = 0; i < particles.length; i++
        ) {

            const a =
                particles[i];


            for (
                let j = i + 1; j < particles.length; j++
            ) {

                const b =
                    particles[j];


                const dx =
                    a.x -
                    b.x;


                const dy =
                    a.y -
                    b.y;


                const distance =
                    Math.sqrt(
                        dx * dx +
                        dy * dy
                    );


                if (
                    distance >
                    CONNECTION_DISTANCE
                ) {

                    continue;
                }


                let alpha =
                    (
                        1 -
                        distance /
                        CONNECTION_DISTANCE
                    ) *
                    0.09;


                /* Mouse interaction */

                if (
                    mouse.active
                ) {

                    const midX =
                        (
                            a.x +
                            b.x
                        ) / 2;


                    const midY =
                        (
                            a.y +
                            b.y
                        ) / 2;


                    const mdx =
                        midX -
                        mouse.x;


                    const mdy =
                        midY -
                        mouse.y;


                    const mouseDistance =
                        Math.sqrt(
                            mdx * mdx +
                            mdy * mdy
                        );


                    if (
                        mouseDistance <
                        mouse.radius * 1.4
                    ) {

                        const boost =
                            1 -
                            mouseDistance /
                            (mouse.radius * 1.4);


                        alpha +=
                            boost * 0.22;

                    }

                }


                /* Blend the two particle colors */

                const r =
                    Math.round(
                        (
                            a.color.r +
                            b.color.r
                        ) / 2
                    );


                const g =
                    Math.round(
                        (
                            a.color.g +
                            b.color.g
                        ) / 2
                    );


                const blue =
                    Math.round(
                        (
                            a.color.b +
                            b.color.b
                        ) / 2
                    );


                ctx.beginPath();


                ctx.strokeStyle =
                    `rgba(
                        ${r},
                        ${g},
                        ${blue},
                        ${alpha}
                    )`;


                ctx.lineWidth =
                    0.75;


                ctx.moveTo(
                    a.x,
                    a.y
                );


                ctx.lineTo(
                    b.x,
                    b.y
                );


                ctx.stroke();

            }

        }
    }


    /* =====================================================
       MOUSE LIGHT
       No visible cursor dot.
    ===================================================== */

    function drawMouseLight() {

        if (!mouse.active) {

            return;
        }


        const gradient =
            ctx.createRadialGradient(
                mouse.x,
                mouse.y,
                0,
                mouse.x,
                mouse.y,
                mouse.radius
            );


        gradient.addColorStop(
            0,
            "rgba(236,72,153,0.16)"
        );


        gradient.addColorStop(
            0.25,
            "rgba(217,70,239,0.09)"
        );


        gradient.addColorStop(
            0.55,
            "rgba(139,92,246,0.04)"
        );


        gradient.addColorStop(
            1,
            "rgba(139,92,246,0)"
        );


        ctx.beginPath();


        ctx.fillStyle =
            gradient;


        ctx.arc(
            mouse.x,
            mouse.y,
            mouse.radius,
            0,
            Math.PI * 2
        );


        ctx.fill();
    }


    /* =====================================================
       ANIMATION
    ===================================================== */

    function animate() {

        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        drawBase();


        /* Ambient light */

        for (
            const source
            of lightSources
        ) {

            source.update();

            source.draw();

        }


        drawGrid();


        /* Update particles */

        for (
            const particle
            of particles
        ) {

            particle.update();

        }


        /* Connections */

        drawConnections();


        /* Bright particles */

        for (
            const particle
            of particles
        ) {

            particle.draw();

        }


        /* Mouse light */

        drawMouseLight();


        requestAnimationFrame(
            animate
        );
    }


    /* =====================================================
       MOUSE EVENTS
    ===================================================== */

    window.addEventListener(
        "mousemove",
        (event) => {

            mouse.x =
                event.clientX;

            mouse.y =
                event.clientY;

            mouse.active =
                true;

        }, {
            passive: true
        }
    );


    window.addEventListener(
        "mouseleave",
        () => {

            mouse.active =
                false;

        }
    );


    /* =====================================================
       TOUCH
    ===================================================== */

    window.addEventListener(
        "touchmove",
        (event) => {

            if (!event.touches ||
                !event.touches.length
            ) {

                return;
            }


            mouse.x =
                event.touches[0].clientX;

            mouse.y =
                event.touches[0].clientY;

            mouse.active =
                true;

        }, {
            passive: true
        }
    );


    window.addEventListener(
        "touchend",
        () => {

            mouse.active =
                false;

        }
    );


    /* =====================================================
       RESIZE
    ===================================================== */

    window.addEventListener(
        "resize",
        () => {

            resize();

            createLightSources();

            createParticles();

        }
    );


    /* =====================================================
       START
    ===================================================== */

    resize();

    createLightSources();

    createParticles();

    animate();

})();