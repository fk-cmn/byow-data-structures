"""Bake the native title screen's stonework and thorn garden (Pillow, NumPy)."""

from math import atan2, cos, hypot, pi, sin, sqrt
from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageDraw

W, H, SCALE = 1440, 900, 2
SIZE = (W * SCALE, H * SCALE)
rng = random.Random(41029)
noise_rng = np.random.default_rng(524)
image = Image.new("RGB", SIZE, (11, 15, 24))
draw = ImageDraw.Draw(image)


def points(vertices):
    return [(round(x * SCALE), round(y * SCALE)) for x, y in vertices]


def poly(vertices, color):
    draw.polygon(points(vertices), fill=color)


def line(vertices, color, width=1):
    draw.line(points(vertices), fill=color, width=max(1, round(width * SCALE)), joint="curve")


def oval(x, y, rx, ry, color):
    draw.ellipse(points([(x - rx, y - ry), (x + rx, y + ry)]), fill=color)


def bezier(a, b, c, d):
    return [
        tuple((1-t)**3 * a[i] + 3*t*(1-t)**2 * b[i] + 3*t*t*(1-t)*c[i] + t**3*d[i]
              for i in range(2))
        for t in (k / 42 for k in range(43))
    ]


def stone(x, y, w, h, shade):
    color = tuple(v + shade for v in (31, 36, 47))
    a, b, c, d = (x+3, y+2), (x+w-3, y+2), (x+w-2, y+h-4), (x+2, y+h-1)
    poly([a, b, c, d], color)
    line([d, a, b], tuple(v + 8 for v in color), 1.7)
    line([d, c, b], tuple(v - 12 for v in color), 2.1)
    for _ in range(3):
        sx, sy = x+rng.uniform(7, w-8), y+rng.uniform(5, h-9)
        line([(sx, sy), (sx+rng.uniform(1, 6), sy+rng.uniform(0, 3))],
             tuple(v - rng.randint(3, 9) for v in color), rng.uniform(.4, 1.6))


for row in range(13):
    for col in range(-1, 11):
        stone(col*155 + (row % 2)*74, row*59-22, 155, 59, rng.randint(-8, 9))


def arch(cx, spring, half, floor, steps=32):
    # Two circular arcs of an equilateral pointed arch.
    flank = []
    for k in range(steps + 1):
        dx = half * (1 - k / steps)
        y = spring - sqrt(max(0, (2*half)**2 - (half+dx)**2))
        flank.append((cx-dx, y))
    return [(cx-half, floor), *flank, *((2*cx-x, y) for x, y in reversed(flank[:-1])),
            (cx+half, floor)]


def doorway(cx, spring, half, floor, dark, layers):
    for inset, color in layers:
        poly(arch(cx, spring, half-inset, floor), color)
    inset = layers[-1][0] + 5
    poly(arch(cx, spring, half-inset, floor), dark)
    for i in range(1, 10):
        k = 1 - i/10
        for side in [-1, 1]:
            def cut(radius):
                return (cx+side*radius*k, spring-radius*sqrt(4-(1+k)**2))
            line([cut(half), cut(half-inset)], (24, 28, 36), 1.7)
    for side in [-1, 1]:
        for y in range(spring+25, floor, 47):
            line([(cx+side*half, y), (cx+side*(half-inset), y-1)], (23, 27, 36), 1.6)


doorway(720, 546, 312, 721, (10, 16, 27), [
    (0, (60, 68, 78)), (5, (32, 41, 52)), (18, (45, 57, 70)),
    (23, (22, 30, 44)), (39, (39, 48, 62)), (46, (17, 25, 39))])
doorway(720, 516, 225, 721, (8, 13, 23), [
    (0, (32, 44, 58)), (3, (21, 31, 47)), (16, (29, 41, 55))])
for cx in (259, 1181):
    doorway(cx, 492, 126, 727, (12, 18, 28), [
        (0, (55, 59, 64)), (4, (36, 41, 50)), (17, (56, 57, 61)),
        (20, (24, 31, 41)), (31, (42, 47, 57))])
    for dx in (-42, 0, 42):
        line([(cx+dx, 496), (cx+dx, 717)], (25, 34, 45), 4)
    for y in (554, 646):
        line([(cx-68, y), (cx+68, y)], (31, 39, 51), 4)

for cx in (112, 398, 1042, 1328):
    poly([(cx-20, 0), (cx+26, 0), (cx+23, 708), (cx-23, 708)], (42, 47, 57))
    for dx, shade in [(-19, 50), (-12, 35), (-6, 42), (3, 54), (13, 43), (19, 34)]:
        line([(cx+dx, 0), (cx+dx, 718)], (shade, shade+5, shade+11), 5)
    for y in (91, 132, 667, 689, 716):
        poly([(cx-31, y), (cx+31, y), (cx+24, y+16), (cx-24, y+16)], (57, 60, 68))
        line([(cx-29, y+1), (cx+29, y+1)], (72, 74, 80), 2)

poly([(0, 719), (1440, 719), (1440, 900), (0, 900)], (34, 39, 49))
for y0, y1 in zip([722, 737, 762, 803, 865], [737, 762, 803, 865, 907]):
    for j in range(-7, 8):
        near = 37 + (y1-720)*.79
        far = 37 + (y0-720)*.79
        shade = rng.randint(24, 41)
        poly([(720+j*far, y0+1), (719+(j+1)*far, y0+1),
              (718+(j+1)*near, y1-2), (722+j*near, y1-2)], (shade, shade+6, shade+14))
    line([(0, y0), (1440, y0)], (19, 25, 35), 1.5)

CANDLES = [(291, 486), (309, 471), (326, 490), (1112, 484), (1131, 470), (1148, 491)]
for cx in (309, 1131):
    for sign in (-1, 1):
        line(bezier((cx, 542), (cx+sign*30, 551), (cx+sign*33, 521), (cx+sign*18, 514)),
             (16, 15, 21), 6)
        line(bezier((cx, 539), (cx+sign*26, 548), (cx+sign*30, 520), (cx+sign*18, 514)),
             (93, 67, 45), 2)
    poly([(cx-6, 521), (cx+6, 521), (cx+2, 575), (cx, 581), (cx-3, 567)], (64, 48, 39))

for x, y in CANDLES:
    end = y + (56 if x in (309, 1131) else 31)
    poly([(x-5, y+6), (x+4, y+6), (x+5, end), (x-5, end)], (167, 145, 112))
    line([(x-3, y+7), (x-3, min(end, y+27))], (215, 187, 139), 2)
    line([(x+3, y+8), (x+4, end)], (86, 65, 53), 2)
    oval(x, end, 8, 2.5, (82, 59, 42))

ROSES = []


def leaf(x, y, angle, size, tone):
    u = (cos(angle), sin(angle))
    v = (-u[1], u[0])

    def at(along, across):
        return (x+size*(u[0]*along+v[0]*across), y+size*(u[1]*along+v[1]*across))

    a, b = at(0, 0), at(1, 0)
    top = bezier(a, at(.25, -.46), at(.72, -.43), b)
    bottom = bezier(b, at(.64, .46), at(.23, .27), a)
    poly(top+bottom, (16+tone, 30+tone, 35+tone))
    poly(top+[a], (23+tone, 40+tone, 45+tone))
    line([a, at(.40, -.04), at(.79, -.01)], (38+tone, 54+tone, 57+tone), .65)


for side in (-1, 1):
    for branch in range(12):
        def point(x, y):
            return 720 + side*x, y

        start = point(rng.uniform(440, 810), rng.uniform(837, 975))
        joint = point(rng.uniform(400, 690), rng.uniform(452, 660))
        end = point(rng.uniform(356, 790), rng.uniform(-105, 480))
        elbow = point(rng.uniform(330, 740), joint[1]+rng.uniform(59, 199))
        tangent = (joint[0]+.72*(joint[0]-elbow[0]), joint[1]+.72*(joint[1]-elbow[1]))
        vine = bezier(start, point(rng.uniform(320, 830), rng.uniform(671, 941)), elbow, joint)
        vine += bezier(joint, tangent, point(rng.uniform(348, 804), rng.uniform(-145, 431)), end)[1:]
        width = rng.uniform(3.1, 8.8)
        for k in range(len(vine)-1):
            x, y = vine[k]
            taper = width * (1-k/len(vine))**.67
            line(vine[k:k+2], (7, 10, 16), taper + 1)
            if taper > 1.1:
                xx, yy = vine[k+1]
                line([(x+.8, y-.8), (xx+.8, yy-.8)], (22, 31, 39), taper*.27)
        for k in range(4, len(vine)-2, rng.choice((5, 6, 7))):
            x, y = vine[k]
            xx, yy = vine[k+1]
            angle = atan2(yy-y, xx-x)
            turn = rng.choice((-1, 1))
            size = rng.uniform(9, 23)
            tx, ty = x + cos(angle+turn*.95)*size, y + sin(angle+turn*.95)*size
            poly([(x, y), (tx, ty), (x+cos(angle)*4, y+sin(angle)*4),
                  (x-cos(angle)*4, y-sin(angle)*4)], (9, 13, 21))
            if rng.random() < .59:
                side_of_stem = -turn
                sweep = angle + side_of_stem*rng.uniform(.55, 1.38)
                length = rng.uniform(17, 38)
                ux, uy = cos(sweep), sin(sweep)
                tip = (x+ux*length, y+uy*length)
                twig = bezier((x, y), (x+ux*length*.25, y+uy*length*.18),
                              (x+ux*length*.76-uy*5, y+uy*length*.73+ux*5), tip)
                line(twig, (19, 31, 36), rng.uniform(.9, 2.1))
                for j, turn_dir in ((18, -1), (28, 1), (40, -1)):
                    lx, ly = twig[j]
                    leaf(lx, ly, sweep+turn_dir*rng.uniform(.35, 1.03), rng.uniform(7, 16), rng.randint(-4, 17))
        if branch % 3 != 0:
            x, y = vine[rng.randrange(8, len(vine)-9)]
            if 14 < x < 1426 and 18 < y < 899 and abs(x-720) > 405:
                ROSES.append((x, y, rng.uniform(10, 22)))

ROSES.extend([(100, 741, 28), (143, 789, 34), (52, 822, 23), (217, 865, 22), (82, 615, 18),
              (87, 228, 17), (196, 156, 13), (1336, 747, 31), (1298, 808, 28),
              (1384, 838, 21), (1245, 859, 24), (1361, 589, 19), (1348, 255, 19), (1275, 148, 14),
              (157, 536, 16), (246, 388, 12), (1264, 534, 15), (1175, 390, 12)])
for cx, cy, r in ROSES:
    sign = 1 if cx > 720 else -1
    stem = bezier((cx, cy), (cx+sign*r*.4, cy+r*.35), (cx+sign*r*.3, cy+r*.9),
                  (cx+sign*r*.85, cy+r*1.5))
    line(stem, (16, 32, 38), 1.8)
    leaf(*stem[27], 1.15 if sign > 0 else 2.75, r*.79, 10)
    leaf(*stem[34], .3 if sign > 0 else 1.66, r*.61, 5)

# Light the stone and silhouettes before painting the emitting petals.
yy, xx = np.ogrid[:SIZE[1], :SIZE[0]]
x, y = xx / SCALE, yy / SCALE
cloud = noise_rng.random((52, 84), dtype=np.float32)
grain = np.asarray(Image.fromarray(cloud).resize(SIZE, Image.Resampling.BICUBIC))
fine = noise_rng.normal(0, 1.5, (SIZE[1], SIZE[0])).astype(np.float32)
shade = np.clip(1.03 - .41*((x-720)/780)**2 - .25*((y-490)/610)**2, .33, 1.)
blue = np.exp(-(((x-720)/480)**2 + ((y-453)/565)**2)*1.3) * .38
warm = np.zeros((SIZE[1], SIZE[0]), dtype=np.float32)
for cx, cy in CANDLES[1::3]:
    warm += np.exp(-(((x-cx)/141)**2 + ((y-cy)/180)**2)*1.65).astype(np.float32)
for cx, cy, r in ROSES:
    blue += (r*.009)*np.exp(-(((x-cx)/(r*3.7))**2 + ((y-cy)/(r*3.1))**2))
mist = np.exp(-((y-759-17*np.sin(x/171))/64)**2) * (.09+grain*.18)
pixels = np.asarray(image).astype(np.float32)
for i, (cold, fire, haze) in enumerate(zip((15, 49, 81), (71, 38, 14), (27, 40, 54))):
    pixels[:, :, i] = pixels[:, :, i]*(shade + warm*.23) + blue*cold + warm*fire + mist*haze
    pixels[:, :, i] += (grain-.5)*13+fine
image = Image.fromarray(np.uint8(np.clip(pixels, 0, 255)))
draw = ImageDraw.Draw(image)


PALETTES = [
    ((10, 24, 66), (43, 82, 159), (104, 161, 229)),
    ((12, 39, 73), (44, 113, 178), (137, 199, 247)),
    ((24, 57, 91), (88, 160, 215), (190, 232, 254)),
    ((16, 32, 78), (67, 100, 182), (147, 168, 233)),
]


def mix(a, b, weight):
    return tuple(round(v0+(v1-v0)*weight) for v0, v1 in zip(a, b))


def rose(cx, cy, r, form, palette):
    shadow, mid, shine = palette
    if form == "bud":
        lean = rng.choice((-1, 1))*r*.38
        top, foot = (cx+lean, cy-r*.84), (cx, cy+r*.74)
        left = bezier(foot, (cx-r*.85, cy+r*.08), (cx-r*.60, cy-r*.74), top)
        right = bezier(top, (cx+r*.67, cy-r*.97), (cx+r*.66, cy+r*.25), foot)
        poly(left+right, shadow)
        fold = bezier(top, (cx+r*.43, cy-r*.31), (cx-r*.37, cy+r*.24), foot)
        poly(left+fold, mix(shadow, mid, .75))
        line(fold[3:32], mix(mid, shine, .56), r*.047)
        line(right[4:24], mix(mid, shine, .46), r*.041)
        poly([foot, (cx-r*.51, cy+r*.17), (cx-r*.19, cy+r*.23),
              (cx+r*.09, cy+r*.48), (cx+r*.47, cy+r*.12)], (22, 53, 65))
        return

    layers = ([(7, .53, .44), (6, .36, .38), (5, .20, .29), (3, .07, .20)]
              if form == "cup" else [(10, .68, .47), (8, .44, .40), (6, .25, .31), (4, .09, .21)])
    flatten = .62 if form == "cup" else rng.uniform(.72, .94)
    for layer, (n, distance, breadth) in enumerate(layers):
        start = rng.uniform(0, 2*pi)
        for i in range(n):
            a = start + i * 2*pi/n
            u, v = (cos(a), sin(a)), (-sin(a), cos(a))

            def at(out, across):
                dy = r*(u[1]*out+v[1]*across)*flatten
                return (cx+r*(u[0]*out+v[0]*across), cy+dy-(layer*r*.075 if form == "cup" else 0))

            bend = rng.uniform(.90, 1.15)
            lip = bezier(at(distance-.07, -breadth*.72), at(distance+.44*bend, -breadth*.85),
                         at(distance+.37*bend, breadth*.75), at(distance-.04, breadth*.79))
            back = bezier(lip[-1], at(distance-.48, breadth*.48),
                          at(distance-.48, -breadth*.26), lip[0])
            value = rng.uniform(.16, .69) + layer*.072
            poly(lip+back, mix(shadow, mid, min(.96, value*.78)))
            for k in range(4):
                ink = mix(mid, shine, min(.91, value*(.48+k*.11)))
                inner = [(px*(1-k*.09)+cx*k*.09, py*(1-k*.09)+cy*k*.09) for px, py in lip]
                line(inner[3+k:37-k], ink, max(.6, r*.032))
            line(lip[12:28], mix(mid, shine, min(.96, value*.92)), max(.6, r*.034))
    if r > 20:
        oval(cx+r*.06, cy-r*.04, r*.043, r*.036, (166, 218, 244))


for i, bloom in enumerate(sorted(ROSES, key=lambda bloom: bloom[2])):
    form = ("bud", "cup", "open")[i % 3] if bloom[2] < 25 else ("cup" if i % 4 == 0 else "open")
    rose(*bloom, form, PALETTES[i % len(PALETTES)])
for _ in range(70):
    x, y, r = rng.choice(ROSES)
    px, py = x + rng.gauss(0, r), y + rng.gauss(0, r)*1.24
    oval(px, py, rng.uniform(.35, 1.2), .6, rng.choice([(72, 132, 168), (96, 152, 182)]))

root = Path(__file__).resolve().parents[1]
image.save(root / "assets/gothic-hall.jpg", quality=94, subsampling=0, optimize=True)
