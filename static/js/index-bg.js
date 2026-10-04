document.addEventListener("DOMContentLoaded", () => {

    const canvas =
        document.getElementById("placementCanvas");

    if (!canvas) return;

    const ctx =
        canvas.getContext("2d", {
            alpha: true
        });

    let width = 0;
    let height = 0;
    let dpr = 1;


    /* =====================================================
       SETTINGS
       ===================================================== */

    const NODE_COUNT = 85;

    const CONNECTION_DISTANCE = 185;

    const MOUSE_DISTANCE = 280;

    const MOUSE_STRENGTH = 0.075;


    /* =====================================================
       MOUSE
       ===================================================== */

    const mouse = {

        x: -1000,
        y: -1000,

        targetX: -1000,
        targetY: -1000,

        active: false
    };


    /* =====================================================
       NODES
       ===================================================== */

    const nodes = [];


    function createNodes() {

        nodes.length = 0;

        const count =
            Math.min(
                NODE_COUNT,
                Math.max(
                    45,
                    Math.floor(
                        (width * height) / 14500
                    )
                )
            );


        for (
            let i = 0; i < count; i++
        ) {

            nodes.push({

                x: Math.random() *
                    width,

                y: Math.random() *
                    height,

                /* Faster movement */

                vx:
                    (
                        Math.random() - 0.5
                    ) * 0.34,

                vy:
                    (
                        Math.random() - 0.5
                    ) * 0.34,

                /* Slightly larger particles */

                radius: 1.25 +
                    Math.random() * 1.7,

                phase: Math.random() *
                    Math.PI *
                    2,

                pulseSpeed: 0.0010 +
                    Math.random() *
                    0.0009
            });
        }
    }


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
            Math.floor(
                width * dpr
            );

        canvas.height =
            Math.floor(
                height * dpr
            );


        canvas.style.width =
            `${width}px`;

        canvas.style.height =
            `${height}px`;


        ctx.setTransform(
            dpr,
            0,
            0,
            dpr,
            0,
            0
        );


        createNodes();
    }


    /* =====================================================
       MOUSE EVENTS
       ===================================================== */

    window.addEventListener(
        "pointermove",
        (event) => {

            mouse.targetX =
                event.clientX;

            mouse.targetY =
                event.clientY;

            mouse.active = true;

        }, {
            passive: true
        }
    );


    window.addEventListener(
        "pointerleave",
        () => {

            mouse.active = false;

            mouse.targetX = -1000;
            mouse.targetY = -1000;
        }
    );


    window.addEventListener(
        "blur",
        () => {

            mouse.active = false;

            mouse.targetX = -1000;
            mouse.targetY = -1000;
        }
    );


    /* =====================================================
       SMOOTH MOUSE
       ===================================================== */

    function updateMouse() {

        const ease = 0.075;


        mouse.x +=
            (
                mouse.targetX -
                mouse.x
            ) * ease;


        mouse.y +=
            (
                mouse.targetY -
                mouse.y
            ) * ease;
    }


    /* =====================================================
       UPDATE NODE
       ===================================================== */

    function updateNode(
        node,
        time
    ) {

        /* Faster base movement */

        node.x +=
            node.vx;

        node.y +=
            node.vy;


        /* =================================================
           EXTRA FLOATING MOTION
           ================================================= */

        node.x +=
            Math.sin(
                time *
                node.pulseSpeed +
                node.phase
            ) * 0.045;


        node.y +=
            Math.cos(
                time *
                node.pulseSpeed *
                0.8 +
                node.phase
            ) * 0.045;


        /* =================================================
           MOUSE INTERACTION
           ================================================= */

        if (
            mouse.active &&
            mouse.x > -500
        ) {

            const dx =
                node.x -
                mouse.x;

            const dy =
                node.y -
                mouse.y;


            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            if (
                distance <
                MOUSE_DISTANCE &&
                distance > 0
            ) {

                const influence =
                    1 -
                    distance /
                    MOUSE_DISTANCE;


                const force =
                    influence *
                    influence *
                    MOUSE_STRENGTH;


                node.vx +=
                    (-dx /
                        distance
                    ) *
                    force;


                node.vy +=
                    (-dy /
                        distance
                    ) *
                    force;
            }
        }


        /* =================================================
           CONTROL SPEED
           ================================================= */

        node.vx *= 0.998;
        node.vy *= 0.998;


        const maxSpeed =
            0.52;


        const speed =
            Math.sqrt(
                node.vx *
                node.vx +

                node.vy *
                node.vy
            );


        if (
            speed >
            maxSpeed
        ) {

            node.vx =
                (
                    node.vx /
                    speed
                ) *
                maxSpeed;


            node.vy =
                (
                    node.vy /
                    speed
                ) *
                maxSpeed;
        }


        /* =================================================
           WRAP AROUND SCREEN
           ================================================= */

        if (
            node.x < -20
        ) {

            node.x =
                width + 20;
        }


        if (
            node.x >
            width + 20
        ) {

            node.x = -20;
        }


        if (
            node.y < -20
        ) {

            node.y =
                height + 20;
        }


        if (
            node.y >
            height + 20
        ) {

            node.y = -20;
        }
    }


    /* =====================================================
       DRAW CONNECTIONS
       ===================================================== */

    function drawConnections() {

        for (
            let i = 0; i < nodes.length; i++
        ) {

            const a =
                nodes[i];


            for (
                let j = i + 1; j < nodes.length; j++
            ) {

                const b =
                    nodes[j];


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


                let opacity =
                    1 -
                    distance /
                    CONNECTION_DISTANCE;


                /* Brighter connections */

                opacity *= 0.115;


                ctx.beginPath();


                ctx.moveTo(
                    a.x,
                    a.y
                );


                ctx.lineTo(
                    b.x,
                    b.y
                );


                ctx.strokeStyle =
                    `rgba(
                        108,
                        114,
                        245,
                        ${opacity}
                    )`;


                ctx.lineWidth =
                    0.75;


                ctx.stroke();
            }
        }
    }


    /* =====================================================
       DRAW NODES
       ===================================================== */

    function drawNodes(time) {

        nodes.forEach(
            (node) => {

                const pulse =
                    (
                        Math.sin(
                            time *
                            node.pulseSpeed +
                            node.phase
                        ) + 1
                    ) * 0.5;


                const radius =
                    node.radius +
                    pulse * 0.7;


                /* =========================================
                   PARTICLE GLOW
                   ========================================= */

                const glow =
                    ctx.createRadialGradient(

                        node.x,
                        node.y,
                        0,

                        node.x,
                        node.y,
                        radius * 9
                    );


                glow.addColorStop(
                    0,
                    "rgba(160,165,255,0.30)"
                );


                glow.addColorStop(
                    0.20,
                    "rgba(135,140,255,0.18)"
                );


                glow.addColorStop(
                    0.45,
                    "rgba(99,102,241,0.075)"
                );


                glow.addColorStop(
                    1,
                    "rgba(99,102,241,0)"
                );


                ctx.fillStyle =
                    glow;


                ctx.beginPath();


                ctx.arc(
                    node.x,
                    node.y,
                    radius * 9,
                    0,
                    Math.PI * 2
                );


                ctx.fill();


                /* =========================================
                   BRIGHT PARTICLE CORE
                   ========================================= */

                ctx.beginPath();


                ctx.arc(
                    node.x,
                    node.y,
                    radius,
                    0,
                    Math.PI * 2
                );


                ctx.fillStyle =
                    "rgba(190,195,255,0.48)";


                ctx.fill();
            }
        );
    }


    /* =====================================================
       CURSOR NETWORK GLOW
       ===================================================== */

    function drawCursorGlow() {

        if (!mouse.active) return;


        const radius =
            205;


        const gradient =
            ctx.createRadialGradient(

                mouse.x,
                mouse.y,
                0,

                mouse.x,
                mouse.y,
                radius
            );


        gradient.addColorStop(
            0,
            "rgba(145,150,255,0.045)"
        );


        gradient.addColorStop(
            0.22,
            "rgba(110,115,245,0.025)"
        );


        gradient.addColorStop(
            0.50,
            "rgba(99,102,241,0.010)"
        );


        gradient.addColorStop(
            1,
            "rgba(99,102,241,0)"
        );


        ctx.fillStyle =
            gradient;


        ctx.beginPath();


        ctx.arc(
            mouse.x,
            mouse.y,
            radius,
            0,
            Math.PI * 2
        );


        ctx.fill();
    }


    /* =====================================================
       SOFT ATMOSPHERE
       ===================================================== */

    function drawAtmosphere(
        time
    ) {

        const positions = [

            {
                x: width * 0.18 +

                    Math.sin(
                        time *
                        0.00022
                    ) * 50,

                y: height * 0.20 +

                    Math.cos(
                        time *
                        0.00018
                    ) * 30,

                radius: 360,

                alpha: 0.023
            },


            {
                x: width * 0.78 +

                    Math.cos(
                        time *
                        0.00020
                    ) * 40,

                y: height * 0.30 +

                    Math.sin(
                        time *
                        0.00017
                    ) * 28,

                radius: 390,

                alpha: 0.020
            },


            {
                x: width * 0.50 +

                    Math.sin(
                        time *
                        0.00015
                    ) * 35,

                y: height * 0.76 +

                    Math.cos(
                        time *
                        0.00018
                    ) * 25,

                radius: 440,

                alpha: 0.014
            }
        ];


        positions.forEach(
            (light) => {

                const gradient =
                    ctx.createRadialGradient(

                        light.x,
                        light.y,
                        0,

                        light.x,
                        light.y,
                        light.radius
                    );


                gradient.addColorStop(
                    0,
                    `rgba(
                        86,
                        82,
                        220,
                        ${light.alpha}
                    )`
                );


                gradient.addColorStop(
                    0.40,
                    `rgba(
                        70,
                        70,
                        180,
                        ${light.alpha * 0.28}
                    )`
                );


                gradient.addColorStop(
                    1,
                    "rgba(0,0,0,0)"
                );


                ctx.fillStyle =
                    gradient;


                ctx.beginPath();


                ctx.arc(
                    light.x,
                    light.y,
                    light.radius,
                    0,
                    Math.PI * 2
                );


                ctx.fill();
            }
        );
    }


    /* =====================================================
       DARK VIGNETTE
       ===================================================== */

    function drawVignette() {

        const gradient =
            ctx.createRadialGradient(

                width * 0.5,
                height * 0.5,
                height * 0.12,

                width * 0.5,
                height * 0.5,
                Math.max(
                    width,
                    height
                ) * 0.78
            );


        gradient.addColorStop(
            0,
            "rgba(0,0,0,0)"
        );


        gradient.addColorStop(
            0.65,
            "rgba(0,0,0,0.025)"
        );


        gradient.addColorStop(
            1,
            "rgba(0,0,0,0.20)"
        );


        ctx.fillStyle =
            gradient;


        ctx.fillRect(
            0,
            0,
            width,
            height
        );
    }


    /* =====================================================
       ANIMATION
       ===================================================== */

    function animate(time) {

        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        /*
         * Dark base
         */

        ctx.fillStyle =
            "#050507";


        ctx.fillRect(
            0,
            0,
            width,
            height
        );


        updateMouse();


        drawAtmosphere(
            time
        );


        nodes.forEach(
            (node) => {

                updateNode(
                    node,
                    time
                );
            }
        );


        drawConnections();


        drawNodes(
            time
        );


        drawCursorGlow();


        drawVignette();


        requestAnimationFrame(
            animate
        );
    }


    /* =====================================================
       START
       ===================================================== */

    resize();


    window.addEventListener(
        "resize",
        resize
    );


    requestAnimationFrame(
        animate
    );

});