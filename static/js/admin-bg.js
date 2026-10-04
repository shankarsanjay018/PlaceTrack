/* =========================================================
   PLACETRACK ADMIN
   LIVE COMMAND CENTER BACKGROUND

   Unique admin visual:
   - Bright colorful particles
   - Data network
   - Moving data trails
   - Mouse magnetic interaction
   - Soft ambient light
   - No individual particle halos
========================================================= */

(() => {

    const canvas =
        document.getElementById("admin-bg");

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

        radius: 230
    };


    /* =====================================================
       SETTINGS
    ===================================================== */

    const DESKTOP_PARTICLES = 190;

    const MOBILE_PARTICLES = 105;

    const CONNECTION_DISTANCE = 150;

    const TRAIL_COUNT = 16;


    const particles = [];

    const trails = [];

    const lights = [];


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
       Large soft light only.
    ===================================================== */

    class AmbientLight {

        constructor(
            x,
            y,
            radius,
            color,
            opacity,
            moveX,
            moveY
        ) {

            this.baseX = x;

            this.baseY = y;

            this.x = x;

            this.y = y;

            this.radius = radius;

            this.color = color;

            this.opacity = opacity;

            this.moveX = moveX;

            this.moveY = moveY;

            this.phase =
                Math.random() *
                Math.PI * 2;

            this.speed =
                0.001 +
                Math.random() * 0.0015;
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
                    this.phase * 0.75
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
                    ${this.opacity}
                )`
            );


            gradient.addColorStop(
                0.35,
                `rgba(
                    ${c.r},
                    ${c.g},
                    ${c.b},
                    ${this.opacity * 0.45}
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
       PARTICLES
       BRIGHT COLOURFUL CORES
       NO INDIVIDUAL HALO
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
                0.35;

            this.vy =
                (Math.random() - 0.5) *
                0.35;


            this.size =
                Math.random() *
                1.6 +
                0.8;


            this.alpha =
                Math.random() *
                0.30 +
                0.70;


            this.phase =
                Math.random() *
                Math.PI * 2;


            this.phaseSpeed =
                Math.random() *
                0.012 +
                0.004;


            /* Admin colors */

            const colors = [

                /* Emerald */

                {
                    r: 52,
                    g: 211,
                    b: 153
                },


                /* Bright teal */

                {
                    r: 45,
                    g: 212,
                    b: 191
                },


                /* Violet */

                {
                    r: 167,
                    g: 139,
                    b: 250
                },


                /* Purple */

                {
                    r: 139,
                    g: 92,
                    b: 246
                },


                /* Amber */

                {
                    r: 251,
                    g: 191,
                    b: 36
                },


                /* Pink */

                {
                    r: 244,
                    g: 114,
                    b: 182
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


            /* Natural flow */

            this.vx +=
                Math.sin(
                    this.phase
                ) *
                0.0012;


            this.vy +=
                Math.cos(
                    this.phase * 0.8
                ) *
                0.0012;


            /* =================================================
               MOUSE MAGNETIC FIELD
            ================================================= */

            if (
                mouse.active
            ) {

                const dx =
                    mouse.x -
                    this.x;

                const dy =
                    mouse.y -
                    this.y;


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


                    /*
                       Slight attraction near the cursor
                       and stronger repulsion very close.
                    */

                    const direction =
                        distance < 85 ?
                        -1 :
                        1;


                    const angle =
                        Math.atan2(
                            dy,
                            dx
                        );


                    this.vx +=
                        Math.cos(angle) *
                        force *
                        0.018 *
                        direction;


                    this.vy +=
                        Math.sin(angle) *
                        force *
                        0.018 *
                        direction;

                }
            }


            /* Speed */

            const maxSpeed =
                0.72;


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


            /* Wrap */

            if (
                this.x < -15
            ) {

                this.x =
                    width + 15;

            }


            if (
                this.x >
                width + 15
            ) {

                this.x = -15;

            }


            if (
                this.y < -15
            ) {

                this.y =
                    height + 15;

            }


            if (
                this.y >
                height + 15
            ) {

                this.y = -15;

            }

        }


        draw() {

            const c =
                this.color;


            /*
               Bright solid particle.
               NO radial gradient.
            */

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
       DATA TRAILS
    ===================================================== */

    class DataTrail {

        constructor() {

            this.reset();
        }


        reset() {

            this.horizontal =
                Math.random() > 0.5;


            this.opacity =
                Math.random() *
                0.14 +
                0.04;


            this.speed =
                Math.random() *
                1.2 +
                0.45;


            this.length =
                Math.random() *
                80 +
                35;


            if (
                this.horizontal
            ) {

                this.x =
                    Math.random() *
                    width;

                this.y =
                    Math.random() *
                    height;

            } else {

                this.x =
                    Math.random() *
                    width;

                this.y =
                    Math.random() *
                    height;
            }


            const colors = [

                "52,211,153",

                "45,212,191",

                "167,139,250",

                "251,191,36",

                "244,114,182"
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

            if (
                this.horizontal
            ) {

                this.x +=
                    this.speed;


                if (
                    this.x >
                    width + this.length
                ) {

                    this.x = -this.length;

                    this.y =
                        Math.random() *
                        height;
                }

            } else {

                this.y +=
                    this.speed;


                if (
                    this.y >
                    height + this.length
                ) {

                    this.y = -this.length;

                    this.x =
                        Math.random() *
                        width;
                }
            }

        }


        draw() {

            ctx.save();

            ctx.globalAlpha =
                this.opacity;


            ctx.strokeStyle =
                `rgb(${this.color})`;


            ctx.lineWidth =
                1;


            ctx.beginPath();


            if (
                this.horizontal
            ) {

                ctx.moveTo(
                    this.x,
                    this.y
                );


                ctx.lineTo(
                    this.x +
                    this.length,
                    this.y
                );

            } else {

                ctx.moveTo(
                    this.x,
                    this.y
                );


                ctx.lineTo(
                    this.x,
                    this.y +
                    this.length
                );

            }


            ctx.stroke();


            ctx.restore();
        }

    }


    /* =====================================================
       CREATE LIGHTS
    ===================================================== */

    function createLights() {

        lights.length = 0;


        lights.push(
            new AmbientLight(
                width * 0.12,
                height * 0.16,
                370, {
                    r: 52,
                    g: 211,
                    b: 153
                },
                0.095,
                75,
                55
            )
        );


        lights.push(
            new AmbientLight(
                width * 0.50,
                height * 0.20,
                420, {
                    r: 45,
                    g: 212,
                    b: 191
                },
                0.075,
                90,
                60
            )
        );


        lights.push(
            new AmbientLight(
                width * 0.84,
                height * 0.34,
                350, {
                    r: 167,
                    g: 139,
                    b: 250
                },
                0.07,
                70,
                65
            )
        );


        lights.push(
            new AmbientLight(
                width * 0.44,
                height * 0.80,
                430, {
                    r: 139,
                    g: 92,
                    b: 246
                },
                0.065,
                80,
                60
            )
        );


        lights.push(
            new AmbientLight(
                width * 0.82,
                height * 0.83,
                320, {
                    r: 251,
                    g: 191,
                    b: 36
                },
                0.045,
                60,
                50
            )
        );
    }


    /* =====================================================
       CREATE PARTICLES
    ===================================================== */

    function createParticles() {

        particles.length = 0;


        const count =
            window.innerWidth <
            700 ?
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
       CREATE DATA TRAILS
    ===================================================== */

    function createTrails() {

        trails.length = 0;


        for (
            let i = 0; i < TRAIL_COUNT; i++
        ) {

            trails.push(
                new DataTrail()
            );
        }
    }


    /* =====================================================
       BASE
    ===================================================== */

    function drawBase() {

        ctx.fillStyle =
            "#05080a";


        ctx.fillRect(
            0,
            0,
            width,
            height
        );
    }


    /* =====================================================
       CONTROL GRID
    ===================================================== */

    function drawGrid() {

        const size =
            48;


        ctx.strokeStyle =
            "rgba(90,220,180,0.028)";


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
       NETWORK CONNECTIONS
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
                    0.07;


                /* Mouse activates nearby network */

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
                        mouse.radius *
                        1.35
                    ) {

                        const boost =
                            1 -
                            mouseDistance /
                            (
                                mouse.radius *
                                1.35
                            );


                        alpha +=
                            boost *
                            0.24;
                    }
                }


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
                    0.7;


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
       MOUSE FIELD
       No visible glowing dot.
    ===================================================== */

    function drawMouseField() {

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
            "rgba(45,212,191,0.13)"
        );


        gradient.addColorStop(
            0.28,
            "rgba(52,211,153,0.075)"
        );


        gradient.addColorStop(
            0.55,
            "rgba(139,92,246,0.035)"
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


        /* Cursor ring */

        ctx.beginPath();

        ctx.strokeStyle =
            "rgba(52,211,153,0.14)";

        ctx.lineWidth =
            1;

        ctx.arc(
            mouse.x,
            mouse.y,
            72,
            0,
            Math.PI * 2
        );

        ctx.stroke();
    }


    /* =====================================================
       ADMIN CORNER ACCENTS
    ===================================================== */

    function drawCornerAccents() {

        const size =
            45;


        ctx.strokeStyle =
            "rgba(52,211,153,0.09)";

        ctx.lineWidth =
            1;


        /* Top left */

        ctx.beginPath();

        ctx.moveTo(
            25,
            25 + size
        );

        ctx.lineTo(
            25,
            25
        );

        ctx.lineTo(
            25 + size,
            25
        );

        ctx.stroke();


        /* Top right */

        ctx.beginPath();

        ctx.moveTo(
            width - 25 - size,
            25
        );

        ctx.lineTo(
            width - 25,
            25
        );

        ctx.lineTo(
            width - 25,
            25 + size
        );

        ctx.stroke();


        /* Bottom left */

        ctx.beginPath();

        ctx.moveTo(
            25,
            height - 25 - size
        );

        ctx.lineTo(
            25,
            height - 25
        );

        ctx.lineTo(
            25 + size,
            height - 25
        );

        ctx.stroke();


        /* Bottom right */

        ctx.beginPath();

        ctx.moveTo(
            width - 25 - size,
            height - 25
        );

        ctx.lineTo(
            width - 25,
            height - 25
        );

        ctx.lineTo(
            width - 25,
            height - 25 - size
        );

        ctx.stroke();
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


        /* Ambient lights */

        for (
            const light
            of lights
        ) {

            light.update();

            light.draw();
        }


        drawGrid();


        /* Data streams */

        for (
            const trail
            of trails
        ) {

            trail.update();

            trail.draw();
        }


        /* Particles */

        for (
            const particle
            of particles
        ) {

            particle.update();
        }


        /* Network */

        drawConnections();


        /* Bright particle cores */

        for (
            const particle
            of particles
        ) {

            particle.draw();
        }


        drawCornerAccents();

        drawMouseField();


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

            createLights();

            createParticles();

            createTrails();
        }
    );


    /* =====================================================
       START
    ===================================================== */

    resize();

    createLights();

    createParticles();

    createTrails();

    animate();

})();