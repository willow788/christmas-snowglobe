import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
from matplotlib import patches
import random


WIDTH, HEIGHT = 10, 15

# Heavier animated snowfall across the scene
NUMBER_OF_SNOWFLAKES = 600
FAR_FLAKES = 220
NEAR_FLAKES = 140

DAY_COLORS = ("#9ad6ff", "#e9f7ff")  # Softer sky gradient
NIGHT_COLORS = ("#0b1d3a", "#0c2f3a")


is_night = True

# Force multiplier when the globe is clicked
shake_force = 0

fig, ax = plt.subplots(figsize=(6, 8))
plt.subplots_adjust(bottom=0.18)
ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)
ax.axis('off')
ax.set_facecolor('none')

# Try to maximize the window for full-screen effect
try:
    mng = plt.get_current_fig_manager()
    if hasattr(mng, 'window'):
        try:
            mng.window.state('zoomed')  # Windows/TkAgg
        except Exception:
            pass
    else:
        try:
            mng.full_screen_toggle()
        except Exception:
            pass
except Exception:
    pass

bg = ax.imshow(
    np.zeros((2, 2)),
    extent=[0, WIDTH, 0, HEIGHT],
    origin="lower",
)

snow_x = np.random.uniform(0, WIDTH, NUMBER_OF_SNOWFLAKES)
snow_y = np.random.uniform(0, HEIGHT, NUMBER_OF_SNOWFLAKES)
snow_speed = np.random.uniform(0.02, 0.06, NUMBER_OF_SNOWFLAKES)

# Layered animated snow for depth
far_x = np.random.uniform(0, WIDTH, FAR_FLAKES)
far_y = np.random.uniform(0, HEIGHT, FAR_FLAKES)
far_speed = np.random.uniform(0.01, 0.03, FAR_FLAKES)

near_x = np.random.uniform(0, WIDTH, NEAR_FLAKES)
near_y = np.random.uniform(0, HEIGHT, NEAR_FLAKES)
near_speed = np.random.uniform(0.04, 0.08, NEAR_FLAKES)

pile_x = np.linspace(0, WIDTH, 300)
pile_h = np.zeros_like(pile_x)
pile_patch = [ax.fill_between(pile_x, 0, pile_h, color="white")]

# Glass base and shadow for a more polished globe
base_shadow = patches.Ellipse((5, 1.2), 7.5, 0.8, color="black", alpha=0.12, zorder=1)
base = patches.Ellipse((5, 1.5), 7.2, 0.9, color="#c5c9d6", alpha=0.35, zorder=2)
ax.add_patch(base_shadow)
ax.add_patch(base)

# Tree geometry (inverted) enlarged and lowered to meet trunk
tree_shapes = [
    np.array([[5, 13.5], [2.0, 9.5], [8.0, 9.5]]),  # wide top pointing down
    np.array([[5, 11.2], [3.0, 8.2], [7.0, 8.2]]),   # mid layer
    np.array([[5, 9.2], [3.8, 6.2], [6.2, 6.2]]),    # small bottom (touches trunk)
]
tree_layers = [
    ax.fill(*zip(*shape), color=color)[0]
    for shape, color in zip(tree_shapes, ["#0f8a5f", "#1aa36f", "#24c184"])
]

# Trunk (enlarged) and star (higher)
ax.add_patch(plt.Rectangle((4.5, 3.8), 1.0, 2.4, color="#4c2806"))  # top at y=6.2 to join bottom layer
ax.scatter(5, 14.3, s=140, c="gold", marker="*")

lx = np.random.uniform(3.2, 6.8, 50)
ly = np.random.uniform(7.0, 13.4, 50)
lights = ax.scatter(lx, ly, s=30, c="red", marker="o", zorder=4)
# Soft glow behind lights for cozy feel
light_glow = ax.scatter(lx, ly, s=120, c="red", alpha=0.25, zorder=3)

# Ornaments sprinkled across tree layers (sampled inside triangles)
def sample_points_in_triangle(tri: np.ndarray, n: int):
    # Barycentric sampling
    u = np.random.rand(n)
    v = np.random.rand(n)
    mask = u + v > 1
    u[mask] = 1 - u[mask]
    v[mask] = 1 - v[mask]
    w = 1 - u - v
    # tri: 3x2 vertices
    return u[:, None] * tri[0] + v[:, None] * tri[1] + w[:, None] * tri[2]

orn_points = []
for tri in tree_shapes:
    orn_points.append(sample_points_in_triangle(tri, 18))
orn_points = np.vstack(orn_points)
orn_colors_palette = ["#c0392b", "#d35400", "#f1c40f", "#1abc9c", "#9b59b6"]
orn_colors = np.random.choice(orn_colors_palette, size=orn_points.shape[0])
ornaments = ax.scatter(orn_points[:, 0], orn_points[:, 1], s=20, c=orn_colors, zorder=5)

ax.text(
    5,
    14,
    "Merry Christmas!",
    ha="center",
    color="white",
    fontsize=18,
    fontweight="bold",
)

ax_slider = plt.axes([0.22, 0.06, 0.58, 0.05], facecolor="#14243a")
snow_slider = Slider(ax_slider, "Snowfall", 0.5, 3.0, valinit=1.2, valstep=0.1, color="#79d2ff")

# Day/Night toggle button
ax_toggle = plt.axes([0.82, 0.06, 0.13, 0.05])
toggle_btn = Button(ax_toggle, "Day / Night", color="#1f3a5f", hovercolor="#29507c")


def set_background_img():
    """Update the background gradient based on day/night toggle."""
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    bg.set_data(gradient.T)
    bg.set_cmap(plt.cm.Purples if is_night else plt.cm.Blues)
    fig.patch.set_facecolor("#081a2f" if is_night else "#bfe3ff")
    ax.set_facecolor('none')

    # Soft vignette stars for night, clouds tint for day
    if is_night:
        star_x = np.random.uniform(0, WIDTH, 40)
        star_y = np.random.uniform(8, HEIGHT + 1, 40)
        ax.scatter(star_x, star_y, s=np.random.uniform(5, 20, 40), c="white", alpha=0.6, zorder=0)
    else:
        cloud_x = np.linspace(1, 9, 6)
        cloud_y = np.linspace(10, 14, 6)
        cx, cy = np.meshgrid(cloud_x, cloud_y)
        ax.scatter(cx.ravel(), cy.ravel(), s=180, c="#ffffff", alpha=0.08, zorder=0)

    # Update control styling for visibility in both modes
    style_controls()

def style_controls():
    # Slider axis background and text
    ax_slider.set_facecolor("#14243a" if is_night else "#e3f2ff")
    snow_slider.label.set_color("white" if is_night else "#0b1d3a")
    snow_slider.valtext.set_color("white" if is_night else "#0b1d3a")

    # Toggle button background and label
    btn_bg = "#1f3a5f" if is_night else "#b3d9ff"
    btn_hover = "#29507c" if is_night else "#9cc8ff"
    ax_toggle.set_facecolor(btn_bg)
    toggle_btn.label.set_color("white" if is_night else "#0b1d3a")
    try:
        toggle_btn.color = btn_bg
        toggle_btn.hovercolor = btn_hover
    except Exception:
        pass


def on_click(event):
    global shake_force
    shake_force = 1.0


def on_key(event):
    global is_night
    if event.key == "n":
        is_night = not is_night
        set_background_img()


def on_toggle(event):
    global is_night
    is_night = not is_night
    set_background_img()


def update(frame):
    """Main animation step for snowfall, tree sway, and lights."""
    global shake_force

    # Snowfall (main layer)
    snow_y[:] -= snow_speed * snow_slider.val
    snow_y[:] += np.random.uniform(-0.02, 0.02, NUMBER_OF_SNOWFLAKES) * shake_force
    snow_x[:] += np.random.uniform(-0.02, 0.02, NUMBER_OF_SNOWFLAKES) * shake_force

    landed = snow_y < 0
    if landed.any():
        for x in snow_x[landed]:
            idx = (np.abs(pile_x - x)).argmin()
            pile_h[idx] += 0.1

    snow_y[landed] = HEIGHT
    snow_x[:] = np.mod(snow_x, WIDTH)
    snow.set_offsets(np.c_[snow_x, snow_y])

    # Far layer snowfall (gentle)
    far_y[:] -= far_speed * (0.6 * snow_slider.val)
    far_x[:] += np.random.uniform(-0.01, 0.01, FAR_FLAKES) * shake_force
    far_y[far_y < 0] = HEIGHT
    far_x[:] = np.mod(far_x, WIDTH)
    snow_far.set_offsets(np.c_[far_x, far_y])

    # Near layer snowfall (pronounced)
    near_y[:] -= near_speed * (1.2 * snow_slider.val)
    near_x[:] += np.random.uniform(-0.02, 0.02, NEAR_FLAKES) * shake_force
    near_y[near_y < 0] = HEIGHT
    near_x[:] = np.mod(near_x, WIDTH)
    snow_near.set_offsets(np.c_[near_x, near_y])

    # Update snow pile (re-create patch for simplicity)
    pile_patch[0].remove()
    pile_patch[0] = ax.fill_between(pile_x, 0, pile_h, color="white", zorder=2)

    # Tree sway
    sway = np.sin(frame / 5) * shake_force * 0.12
    for layer, base_shape in zip(tree_layers, tree_shapes):
        layer.set_xy(base_shape + np.array([sway, 0]))

    # Lights pulse and recolor + glow animation
    beat = (np.sin(frame / 3) + 1) / 2
    colors = np.random.choice(["#ff5c5c", "#ffd166", "#8be9fd", "#ffb3ff", "#c7ff6b"], size=30)
    lights.set_color(colors)
    light_count = lights.get_offsets().shape[0]
    lights.set_sizes(np.full(light_count, 25 + 25 * beat))

    glow_count = light_glow.get_offsets().shape[0]
    light_glow.set_color(colors)
    light_glow.set_sizes(np.full(glow_count, 100 + 100 * beat))
    light_glow.set_alpha(0.2 + 0.2 * beat)

    # Ornament gentle shimmer
    orn_count = ornaments.get_offsets().shape[0]
    ornaments.set_sizes(np.full(orn_count, 16 + 10 * beat))
    lights.set_alpha(0.5 + 0.5 * beat)

    shake_force *= 0.9

    return snow, lights


snow = ax.scatter(snow_x, snow_y, s=10, c="white", alpha=0.8, zorder=3)

# Add layered snowflakes for depth
snow_far = ax.scatter(
    far_x,
    far_y,
    s=6,
    c="#d7e9ff",
    alpha=0.45,
    zorder=1,
)
snow_near = ax.scatter(
    near_x,
    near_y,
    s=18,
    c="#ffffff",
    alpha=0.9,
    zorder=5,
)

set_background_img()

# Add a translucent dome for a prettier globe look
circle = plt.Circle((5, 7.5), 7.5, color="white", alpha=0.08, zorder=5)
ax.add_patch(circle)

# Add a glass highlight arc for a shinier globe
highlight = patches.Arc((5, 8.5), 10, 10, theta1=70, theta2=110, color="white", lw=2, alpha=0.25, zorder=6)
ax.add_patch(highlight)

# Globe outline ring for a finished look
ring = patches.Circle((5, 7.5), 7.5, edgecolor="white", facecolor="none", lw=1.2, alpha=0.25, zorder=6)
ax.add_patch(ring)

# Presents at the base
present_specs = [
    ((3.4, 2.0), (1.1, 0.8), "#ff7675", "#d63031"),
    ((5.1, 1.9), (1.2, 0.9), "#74b9ff", "#0984e3"),
    ((6.7, 2.0), (1.0, 0.8), "#fdcb6e", "#e17055"),
]
for (x, y), (w, h), body, ribbon in present_specs:
    ax.add_patch(patches.Rectangle((x, y), w, h, color=body, zorder=4))
    ax.add_patch(patches.Rectangle((x + w/2 - 0.05, y), 0.1, h, color=ribbon, zorder=5))
    ax.add_patch(patches.Rectangle((x, y + h/2 - 0.05), w, 0.1, color=ribbon, zorder=5))

fig.canvas.mpl_connect("button_press_event", on_click)
fig.canvas.mpl_connect("key_press_event", on_key)
toggle_btn.on_clicked(on_toggle)

ani = FuncAnimation(fig, update, interval=50)

plt.show()
