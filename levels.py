# ================= PLATFORM TYPES =================
PLATFORM_STATIC = "static"
PLATFORM_MOVING = "moving"
PLATFORM_FALLING = "falling"
PLATFORM_DEADLY = "deadly"

# ================= HELPERS =================
def platform(x, y, w, h, p_type=PLATFORM_STATIC, **options):
    return (x, y, w, h, p_type, options)

def coin(x, y, value=1):
    # y سالب = ارتفاع فوق الأرض
    return {"x": x, "y": y, "value": value}

# ================= LEVELS =================
levels = [

    # ================= LEVEL 1 =================
    {
        "name": "Level 1",
        "world_width": 3500,
        "spawn": (100, 0),
        "goal": 3200,

        "platforms": [
            platform(300, -120, 200, 20),
            platform(700, -170, 200, 20),
            platform(1100, -200, 200, 20),
            platform(1500, -140, 250, 20),
        ],

        "coins": [
            coin(360, -170),
            coin(430, -170),
            coin(760, -220),
            coin(1120, -250),
            coin(1220, -250),
            coin(1550, -190),
        ]
    },

    # ================= LEVEL 2 =================
    {
        "name": "Level 2",
        "world_width": 4500,
        "spawn": (100, 0),
        "goal": 4200,

        "platforms": [
            platform(300, -120, 200, 20),

            # 🔄 أفقي
            platform(
                800, -160, 200, 20,
                PLATFORM_MOVING,
                range=250,
                speed=200,
                axis="x"
            ),

            platform(1300, -200, 200, 20),

            # 🔄 عمودي
            platform(
                1800, -220, 200, 20,
                PLATFORM_MOVING,
                range=200,
                speed=180,
                axis="y"
            ),

            platform(2300, -160, 200, 20),
        ],

        "coins": [
            coin(360, -170),
            coin(520, -230),
            coin(840, -210),
            coin(900, -250),
            coin(1320, -250),
            coin(1810, -300),
            coin(1880, -300),
            coin(2360, -210),
        ]
    },

    # ================= LEVEL 3 =================
    {
        "name": "Level 3",
        "world_width": 5500,
        "spawn": (100, 0),
        "goal": 5200,

        "platforms": [
            platform(300, -120, 200, 20),
            platform(700, -170, 200, 20),

            platform(
                1200, -200, 200, 20,
                PLATFORM_MOVING,
                range=300,
                speed=220,
                axis="x"
            ),

            # ☠ مؤذي
            platform(1600, -120, 200, 20, PLATFORM_DEADLY),

            # ⚠ يسقط
            platform(2100, -170, 200, 20, PLATFORM_FALLING),

            platform(
                2600, -200, 200, 20,
                PLATFORM_MOVING,
                range=200,
                speed=160,
                axis="y"
            ),

            platform(3100, -160, 200, 20),
        ],

        "coins": [
            coin(360, -170),
            coin(720, -220),
            coin(860, -250),
            coin(1230, -260),
            coin(1320, -260),
            coin(1700, -190),
            coin(2120, -220),
            coin(2180, -220),
            coin(2640, -280),
            coin(2720, -280),
            coin(3150, -210),
            coin(3300, -240),
        ]
    },
]