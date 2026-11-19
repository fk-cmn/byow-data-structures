
from pathlib import Path
from functools import lru_cache
from math import sin, cos, tau, hypot
import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageColor

OUT = Path("build/qq-preview/eyes")
OUT.mkdir(parents=True, exist_ok=True)
S = 3
W, H = 240, 264
names = ("枝白", "焰尾", "晚铃", "霜绒", "柚星", "重音テト", "凛凛蝶", "天马")
slugs = ("twig", "ember", "bell", "fleece", "yuzu", "teto", "rin", "tenma")
styles = (
    ("#283332","#fff6e8","#dcd9c3","#fafbf0","#a4b784","#738d68","#71bab9","#b2eed0","#fff3e5"),
    ("#311f28","#4a353d","#271f2a","#806362","#cb484e","#952c42","#dd625b","#ffc971","#ffeadc"),
    ("#322538","#f697ab","#c66383","#ffcad0","#3e4059","#2e2c45","#af72eb","#f499c9","#ffece3"),
    ("#25313b","#edf4f4","#a8bdc6","#ffffff","#455665","#283d4c","#72b7c2","#fa779b","#ffefe8"),
    ("#313329","#f8eca9","#dbb458","#fff6d6","#56736c","#344d4c","#76b99e","#fbd277","#fff1d3"),
    ("#321d2c","#dc4267","#861f48","#ff9ca3","#7a314e","#43283b","#be244e","#ff97ae","#fff0e9"),
    ("#293048","#657a9b","#364460","#c6dbf5","#dedbed","#706180","#7969ba","#efb9de","#fff0eb"),
    ("#382331","#944462","#532740","#ee9b9b","#5d384c","#492937","#8664b7","#f7cc8d","#ffead9"),
)

class Paint:
    def __init__(self):
        self.im = Image.new("RGBA", (W*S,H*S))
        self.d = ImageDraw.Draw(self.im)
        self.dy = 0
    def position(self,x,y):
        return (round(x*S),round((y+self.dy)*S))
    def path(self, data, fill=None, stroke=None, width=2.8):
        tok = re.findall(r'[MLCQZ]|[-+]?(?:\d*\.)?\d+',data)
        p, start, pts, i = (0.,0.), (0.,0.), [], 0
        while i < len(tok):
            op=tok[i]
            i+=1
            if op=="Z":
                p=start
                pts.append(self.position(*p))
                continue
            n={"M":2,"L":2,"Q":4,"C":6}[op]
            a=list(map(float,tok[i:i+n]))
            i+=n
            if op in ("M","L"):
                p=tuple(a)
                if op=="M": start=p
                pts.append(self.position(*p))
                continue
            x,y=p
            for k in range(1,18):
                t=k/17
                u=1-t
                if op=="Q":
                    xi,yi=u*u*x+2*u*t*a[0]+t*t*a[2],u*u*y+2*u*t*a[1]+t*t*a[3]
                else:
                    xi=u**3*x+3*u*u*t*a[0]+3*u*t*t*a[2]+t**3*a[4]
                    yi=u**3*y+3*u*u*t*a[1]+3*u*t*t*a[3]+t**3*a[5]
                pts.append(self.position(xi,yi))
            p=tuple(a[-2:])
        if fill: self.d.polygon(pts,fill=fill)
        if stroke: self.d.line(pts,fill=stroke,width=max(1, round(width*S)),joint="curve")
        return pts
    def oval(self, box, fill, stroke=None, width=2):
        self.d.ellipse([self.position(*box[:2]),self.position(*box[2:])],fill=fill,outline=stroke,width=round(width*S))
    def star(self,x,y,r,c):
        self.path(f"M {x-r} {y} Q {x} {y-1} {x} {y-r} Q {x+1} {y} {x+r} {y} Q {x} {y+1} {x} {y+r} Q {x-1} {y} {x-r} {y} Z",c)
    def finish(self):
        return self.im.resize((W*2,H*2),Image.Resampling.LANCZOS)

def spirit(p,x,y,c,ink,kind):
    if kind==0:
        p.path(f"M {x-6} {y+4} Q {x-27} {y-13} {x-10} {y-25} Q {x+4} {y-22} {x+4} {y-13} Q {x+19} {y-25} {x+21} {y-9} Q {x+19} {y+5} {x-6} {y+4} Z",c,ink,2)
        p.path(f"M {x-9} {y+2} Q {x+3} {y-5} {x+12} {y-12}",ink,ink,1.1)
    elif kind==3:
        p.path(f"M {x-13} {y+5} Q {x-24} {y-7} {x-14} {y-14} Q {x-16} {y-25} {x-6} {y-22} Q {x} {y-32} {x+9} {y-22} Q {x+22} {y-23} {x+19} {y-11} Q {x+28} {y-3} {x+17} {y+6} Z",c,ink,2.3)
        p.oval((x-10,y-11,x+12,y+5),"#bfc4cc",ink)
        p.oval((x-6,y-6,x-3,y-3),ink)
        p.oval((x+4,y-6,x+7,y-3),ink)
    else:
        p.path(f"M {x-13} {y+14} C {x-23} {y+7} {x-20} {y-8} {x-12} {y-13} L {x-18} {y-24} Q {x-6} {y-24} {x-3} {y-14} L {x+4} {y-14} Q {x+8} {y-25} {x+16} {y-24} L {x+15} {y-8} Q {x+28} {y+8} {x+11} {y+17} Z",c,ink,2.4)
        p.oval((x-7,y-2,x-3,y+3),"#ffe6ab")
        p.oval((x+5,y-2,x+9,y+3),"#ffe6ab")
        p.path(f"M {x-1} {y+8} Q {x+3} {y+11} {x+7} {y+7}",None,ink,1.1)

def blend(a, b, weight):
    return tuple(round(x+(y-x)*weight) for x,y in zip(a,b))

def ramp(lo, hi, x):
    t = min(1, max(0, (x-lo)/(hi-lo)))
    return t*t*(3-2*t)

# Outer corners, inner corners and eyelid arches use the same mirrored local
# coordinates. Changing the aperture for a blink leaves the iris round.
EYES = (
    (14.7, 6.6, 5.8, -0.4, .80, "#296f69", "#a7ecd5"),  # Twig: relaxed jade
    (14.3, 8.3, 6.6, -2.1, .60, "#9e3f48", "#ffba88"),
    (13.2, 9.2, 7.1, -0.6, .67, "#71479a", "#ebb9ff"),
    (14.5, 8.2, 6.2,  0.6, .75, "#427089", "#b6eaf5"),
    (14.0, 9.4, 6.8, -0.5, .59, "#4c8059", "#efe992"),
    (15.2, 8.8, 6.2, -2.8, .69, "#8e234b", "#fb819b"),
    (15.6, 7.0, 5.6, -1.1, .83, "#405f9a", "#a3ddc2"),
    (15.5, 8.3, 6.4, -2.0, .70, "#6a427d", "#d7a5ed"),
)

@lru_cache(maxsize=16)
def iris_tile(base, light):
    base, light = ImageColor.getrgb(base), ImageColor.getrgb(light)
    dusk = blend(base, (25, 28, 49), .70)
    pupil = blend(base, (31, 30, 47), .77)
    pearl = (255, 250, 232)
    size = 2*round(16*S)+1
    tile = Image.new("RGBA", (size, size))
    pixels = tile.load()
    for j in range(size):
        y=(j-size//2)/(12.9*S)
        for i in range(size):
            x=(i-size//2)/(11.8*S)
            radius=hypot(x,y)
            if radius >= 1.035:
                continue
            color=blend(dusk,base,ramp(-.96,-.36,y))
            color=blend(color,light,.86*ramp(-.24,.87,y))
            color=blend(color,dusk,.76*ramp(.84,1.015,radius))
            color=blend(color,pupil, .96*(1-ramp(.89,1.04,hypot(x/.53,(y+.27)/.64))))
            shine=hypot((x-.13+(y+.31)*.95)/.24,(y+.31)/.145)
            color=blend(color,pearl,1-ramp(.49,1.05,shine))
            lower_glint=hypot((x+.36)/.12,(y-.64)/.086)
            color=blend(color,pearl,.92*(1-ramp(.39,1.08,lower_glint)))
            pixels[i,j]=(*color,round(255*(1-ramp(.96,1.035,radius))))
    return tile

def draw_eyes(p,style,phase,moving,ink,skin):
    w,h,low,lift,blink_at,base,light=EYES[style]
    lid=blend(ImageColor.getrgb(ink),(65, 43, 48),.21)
    waterline=blend(ImageColor.getrgb(skin),(115, 86, 107),.61)
    for i,ex in enumerate((96,144)):
        direction=1 if i==0 else -1
        cy=114.3+(.6 if style==2 and i==0 else 0)
        b=1 if moving else ramp(.008,.083,abs(phase-blink_at))
        if style==5 and i==0 and not moving:
            b*=ramp(.013,.106,abs(phase-.25))
        def xy(x,y):
            return f"{ex+direction*x:.3f} {cy+y*b:.3f}"

        crown=h+3.0
        depth=low+5.7
        outer=xy(-w,lift-.9)
        inner=xy(w*.89,.5)
        if b<.12:
            p.path(f"M {ex+direction*w*.92} {cy+1} Q {ex} {cy+5} "
                   f"{ex-direction*w} {cy+lift} L {ex-direction*(w+3.5)} {cy+lift-1.7}",
                   None,lid,1.65)
            continue
        upper=(f"M {outer} C {xy(-w*.83,-crown*.52)} {xy(-w*.47,-crown*1.12)} {xy(.1,-crown)} "
               f"C {xy(w*.50,-crown*.96)} {xy(w*.77,-crown*.43)} {inner}")
        lower=(f"C {xy(w*.73,depth*.50)} {xy(w*.43,depth*.98)} {xy(-w*.11,depth)} "
               f"C {xy(-w*.69,depth*1.03)} {xy(-w*.96,depth*.51)} {outer}")
        outline=p.path(f"{upper} {lower} Z","#fff4ef")
        xs,ys=zip(*outline)
        x0,y0,x1,y1=min(xs),min(ys),max(xs)+1,max(ys)+1
        size=(x1-x0,y1-y0)
        mask=Image.new("L",size)
        ImageDraw.Draw(mask).polygon([(x-x0,y-y0) for x,y in outline],fill=255)
        # The cool shadow just under the upper lid gives the sclera depth.
        eye=Image.new("RGBA",size)
        eye_draw=ImageDraw.Draw(eye)
        for y in range(size[1]):
            eye_draw.line((0,y,size[0],y),fill=blend((200,182,199),(255,248,244),
                                                     ramp(0,.64,y/size[1])))
        center=p.position(ex-direction*1.15+sin(tau*phase+style*.58)*.55,cy-1.15)
        tint=("#778041","#efda8d") if style==7 and i==1 else (base,light)
        iris=iris_tile(*tint)
        eye.alpha_composite(iris,(center[0]-x0-iris.width//2,center[1]-y0-iris.height//2))
        p.im.paste(eye,(x0,y0),mask)
        p.path(f"M {inner} {lower}",None,waterline,.91)
        # A swept brush edge above the round aperture, with a split outer lash.
        p.path(f"{upper} C {xy(w*.77,-crown*.55)} {xy(w*.45,-crown*1.10-1.2)} {xy(.1,-crown-2.5)} "
               f"Q {xy(-w*.17,-crown-3.4)} {xy(-w*.24,-crown-5.1)} "
               f"Q {xy(-w*.38,-crown-3.1)} {xy(-w*.58,-crown-1.9)} "
               f"C {xy(-w*.82,-crown+.5)} {xy(-w-1.8,lift-4.7)} {xy(-w-4.4,lift-3.8)} "
               f"Q {xy(-w-3.8,lift+.1)} {outer} Z",lid)
        p.path(f"M {xy(-w+.8,lift-1.4)} Q {xy(-w-2.6,lift-1.4)} "
               f"{xy(-w-3.7,lift+.8)} Q {xy(-w-.9,lift+.1)} {outer} Z",lid)

def render(style, phase, moving=False):
    ink,hair,shade,shine,coat,dark,iris,accent,skin = styles[style]
    p=Paint()
    beat=sin(tau*phase)
    stride=sin(tau*phase) if moving else 0
    bob=-abs(stride)*3 if moving else beat*1.7
    wave=max(0,sin(tau*(phase-.10)))**2
    side=5*beat
    p.dy=bob
    if style<3:
        # Tail tips swing without moving the planted feet.
        tip=199+side*(2 if style==2 else 1)
        tip_y=(165 if style==1 else 195)+beat*6
        if style==0: tip=44+side*1.7; tip_y=224+beat*5
        p.path(f"M 146 175 C 166 190 166 206 {tip} {tip_y} C {tip+14} {tip_y+21} 189 239 144 236 Q 130 229 136 204 Z",shade,ink,3.3)
        p.path(f"M 146 230 Q 172 228 {tip} {tip_y} L {tip+8} {tip_y+6} Q 187 235 147 234 Z", shine if style!=2 else hair)
    if style in (0,1,2):
        wind=beat*(6 if style==1 else 3)
        p.path(f"M 86 131 Q 74 145 {61-wind} 203 L 83 219 L 111 209 L 133 219 L {179+wind} 210 Q 169 151 151 128 Z",coat,ink,3.2)
        p.path(f"M 150 142 Q 167 185 {169+wind} 207 L 141 211 L 133 187 Z",dark)
        p.path(f"M 83 159 Q 80 182 {73-wind} 200",None,accent,1.7)
        if style==0:
            p.path("M 75 170 Q 83 150 99 145 L 112 147 L 105 178 L 93 205 L 75 213 L 67 202 Z",hair,ink,2.4)
            p.path("M 143 143 L 157 155 L 169 199 L 159 212 L 141 207 L 131 181 Z",hair,ink,2.4)
    if style==5:
        for direction in (-1,1):
            ex=120+direction*48
            curl=beat*4*direction
            p.path(f"M {ex} 77 Q {ex+direction*38} {68+curl} {ex+direction*28} 106 Q {ex+direction*43} 124 {ex+direction*19} 139 Q {ex+direction*28} 159 {ex+direction*7} {178+curl} Q {ex-direction*19} 160 {ex-direction*8} 118 Z",hair,ink,3.2)
            for row in range(4):
                yy=96+16*row
                x0=ex+direction*(26-row*4)
                p.path(f"M {x0} {yy+curl} Q {ex+direction*9} {yy+8+curl} {ex-direction*5} {yy+2+curl}",None,shade,2.7)
            p.path(f"M {ex} 91 Q {ex+direction*17} {82+curl} {ex+direction*23} {87+curl}",None,shine,2.5)
    if style in (6,7):
        # Long locks with separate tips that lag behind the head.
        for direction in (-1,1):
            base=120+direction*39
            end=base+direction*(28 if style==6 else 43)+side
            tip=218+beat*5*direction
            p.path(f"M {base} 79 Q {base+direction*31} 92 {base+direction*27} 143 Q {base+direction*17} 184 {end} {tip} Q {end-direction*21} {tip-4} {base-direction*5} 192 Q {base-direction*22} 156 {base-direction*12} 112 Z",shade,ink,2.6)
            p.path(f"M {base+direction*11} 97 Q {base+direction*23} 141 {base+direction*17} 166 Q {base+direction*15} 198 {end-direction*4} {tip-8} Q {base+direction*7} 201 {base+direction*5} 174 Z",hair)
            p.path(f"M {base+direction*15} 109 Q {base+direction*21} 134 {base+direction*15} 157 Q {base+direction*12} 181 {end-direction*8} {tip-12}",None,shine,.95)
        if style==7:
            drift=beat*9
            for direction in (-1,1):
                x=120+direction*31
                p.path(f"M {x} 159 Q {x+direction*34} 142 {x+direction*70} {132+drift} Q {x+direction*61} {166+drift} {x+direction*35} 182 Q {x+direction*53} {175+drift} {x+direction*57} {178+drift} Q {x+direction*34} 211 {x} 195 Z","#d6b7b0",shade,1.7)
                p.path(f"M {x+direction*5} 186 Q {x+direction*27} 169 {x+direction*56} {146+drift}",None,"#ffe7b8",1.7)
    # Body, stockings and shoes.
    for cx, lift in ((106, max(0,stride)*12),(135,max(0,-stride)*12)):
        yy=238-lift
        stocking = skin if style in (1,2) else (hair if style==4 else dark)
        p.path(f"M {cx-10} 197 L {cx+11} 198 L {cx+9} {yy} Q {cx-1} {yy+6} {cx-10} {yy-1} Z",stocking,ink)
        p.path(f"M {cx-11} {yy-3} Q {cx} {yy+2} {cx+10} {yy-4} L {cx+12} {yy+4} Q {cx+15} {yy+13} {cx+2} {yy+14} L {cx-14} {yy+13} Q {cx-17} {yy+8} {cx-11} {yy-3} Z",dark if style in (2,4) else coat,ink)
        p.path(f"M {cx-12} {yy+8} Q {cx+2} {yy+10} {cx+9} {yy+6}",None,accent,2)
        p.path(f"M {cx-5} {yy-1} L {cx+5} {yy+4}",None,shine,1.4)
    p.path("M 94 177 Q 120 185 149 176 L 150 204 L 136 214 L 122 208 L 108 213 L 92 204 Z", dark,ink)
    if style in (2,4,6):
        p.path("M 94 181 L 146 181 L 154 205 L 143 210 L 133 205 L 122 212 L 112 206 L 99 210 L 87 203 Z",coat,ink)
        for offset in range(4):
            x=97+offset*13
            p.path(f"M {x} 192 L {x+7} 200 L {x+13} 193",None,shine,1.35)
    p.path("M 98 132 L 142 132 Q 153 139 151 165 L 146 189 Q 120 199 94 188 L 88 159 Q 85 143 98 132 Z",coat,ink,3)
    p.path("M 108 139 L 132 139 L 125 184 L 113 184 Z",hair,ink,1.8)
    p.path("M 94 174 Q 115 185 147 170 L 146 184 Q 118 196 95 185 Z",dark,ink,1.8)
    p.path("M 114 174 L 127 173 L 128 183 L 114 185 Z",accent,ink,1.6)
    p.path("M 118 177 L 124 176 L 124 180 L 118 181 Z",dark)
    # Sleeve eases up and back while the other arm stays near the waist.
    hr=147+wave*(16 if style in (1,5) else 8)+stride*5
    height=(32 if style in (1,2,5) else 15)*wave
    ry=181-height-(11*wave if style==6 else 0)
    p.path(f"M 140 140 Q 151 137 159 153 L {hr+12} {ry-5} Q {hr+9} {ry+9} {hr-5} {ry+9} Q 147 183 138 158 Z",dark,ink)
    p.oval((hr-2,ry-6,hr+14,ry+8),skin,ink)
    p.path(f"M {hr+5} {ry-4} Q {hr+1} {ry-1} {hr+5} {ry+2}",None,shade,1.2)
    ly=180+stride*5-(22*wave if style==7 else 0)
    p.path(f"M 98 138 Q 87 134 81 150 L 74 {ly-7} Q 77 {ly+9} 93 {ly+5} L 105 152 Z",coat,ink)
    p.oval((77,ly-7,94,ly+7),skin,ink)
    p.path(f"M 82 {ly-4} Q 86 {ly} 83 {ly+2}",None,shade,1.15)
    p.path("M 98 135 L 105 127 L 134 129 L 146 140 L 132 155 L 120 147 L 107 157 L 95 143 Z",hair,ink,2)
    p.path("M 120 144 L 127 152 L 120 162 L 114 152 Z",accent,ink,1.8)
    # Face silhouette, separate back hair and head pieces.
    if style==0:
        p.path("M 69 99 Q 54 130 49 151 L 72 146 L 65 168 Q 97 163 113 140 L 147 147 L 172 161 L 163 145 L 183 144 Q 160 114 172 89 Z",shade,ink)
    if style==2:
        p.path("M 119 65 Q 156 40 181 79 Q 192 113 205 118 L 190 124 Q 207 142 207 167 Q 191 167 182 157 Q 166 173 145 158 Z",dark,ink)
    p.path("M 57 102 Q 55 68 83 53 Q 121 33 156 54 Q 183 67 179 109 L 173 129 L 165 145 L 151 154 L 135 148 L 104 152 L 82 153 L 62 140 Z",shade,ink,3.1)
    if style<3:
        wobble=side if style==2 else side*.5
        p.path(f"M 62 91 Q 43 65 {56+wobble} 29 Q 82 39 96 61 L 86 89 Z",hair,ink,3.1)
        p.path(f"M 65 75 Q 54 59 {61+wobble} 40 Q 78 48 85 62 L 77 77 Z",dark,ink,1.3)
        p.path(f"M 148 61 Q 171 38 {185+wobble} 30 Q 197 58 177 93 L 152 86 Z",hair if style!=2 else dark,ink,3.1)
        p.path(f"M 164 64 Q 172 51 {183+wobble} 41 Q 187 56 173 74 L 165 77 Z",coat,ink,1.3)
    p.oval((62,102,83,131),skin,ink)
    p.oval((156,102,177,131),skin,ink)
    p.path("M 72 95 Q 79 64 119 66 Q 160 65 170 95 L 168 117 Q 165 142 146 150 Q 122 164 96 151 Q 79 145 73 122 Z",skin,ink,3.05)
    p.path("M 75 106 Q 92 80 115 81 Q 146 81 168 103 L 164 96 Q 148 66 119 69 Q 79 70 75 106 Z",shade)
    draw_eyes(p,style,phase,moving,ink,skin)
    for ex in (96,144):
        cheek=ex+(-8 if ex==96 else 8)
        p.oval((cheek-6,127,cheek+6,131),"#f0a8ac")
        p.path(f"M {cheek-3} 130 L {cheek-1} 128",None,skin,1)
    if style in (1,5):
        p.path(f"M 110 137 Q 120 144 132 {135-wave*2} Q 127 {146+wave*1.5} 120 146 Q 114 146 110 137 Z",ink)
        p.path("M 116 140 Q 122 141 128 138 L 125 144 L 122 142 L 119 144 Z","#fff6f1")
    elif style in (0,3,6,7):
        p.path("M 114 140 Q 119 145 126 139",None,ink,1.8)
    else:
        p.path(f"M 116 138 Q 120 {139+3*wave} 125 138 Q 124 146 120 146 Q 116 145 116 138 Z",ink)
    p.path("M 118 131 Q 121 129 123 131",None,"#d5968f",1.1)
    # Fringe designs are different for each character.
    fringes=(
        "M 58 110 Q 46 89 69 62 Q 90 40 124 50 Q 157 39 181 89 L 175 111 L 163 96 L 155 103 L 145 79 Q 141 99 125 115 L 130 88 Q 117 104 107 102 L 112 84 Q 101 111 75 120 L 79 102 L 61 120 Z",
        "M 53 105 Q 49 83 70 62 Q 100 38 128 53 Q 154 46 170 58 Q 185 77 178 105 L 167 98 L 158 112 L 150 89 L 143 95 L 137 81 L 127 118 Q 111 109 103 87 L 101 100 L 90 91 Q 80 109 71 111 L 75 95 Z",
        "M 56 107 Q 55 77 73 60 Q 102 36 135 55 Q 170 53 183 83 L 177 119 L 165 128 L 162 104 L 150 96 L 147 81 Q 137 112 102 119 L 110 100 L 85 113 L 76 130 L 69 108 L 57 122 Z",
        "M 59 111 Q 50 83 69 61 Q 96 37 128 51 Q 162 44 180 80 L 176 118 L 161 142 L 154 121 L 153 90 Q 146 105 133 102 L 141 84 Q 129 113 114 109 L 117 90 Q 102 106 85 107 L 93 90 L 75 105 L 72 139 L 61 130 Z",
        "M 56 114 Q 52 82 75 61 Q 97 40 131 52 Q 164 51 180 82 L 178 117 L 164 141 L 155 139 L 164 121 L 151 115 L 156 95 L 140 104 L 143 88 Q 132 103 120 105 L 121 88 Q 114 106 104 102 L 98 94 L 93 111 L 80 107 L 78 136 L 67 141 Z",
        "M 57 112 Q 49 81 66 59 Q 86 34 116 48 Q 146 36 170 62 Q 188 81 181 116 L 169 103 L 167 90 L 156 87 L 150 97 L 139 90 L 146 73 Q 131 92 119 102 L 119 85 Q 101 103 82 101 L 83 89 L 72 101 L 62 119 Z",
    )
    if style==6:
        p.path("M 56 111 Q 55 79 67 63 Q 86 43 119 46 Q 157 43 176 72 Q 185 88 177 117 L 169 107 Q 169 130 157 150 L 154 127 L 152 92 Q 135 105 128 105 L 132 88 Q 121 102 106 105 L 108 88 Q 98 102 83 104 L 85 90 Q 76 111 77 146 L 67 137 Q 59 123 62 106 Z",hair,ink,2.7)
    elif style==7:
        p.path("M 55 109 Q 52 69 85 55 Q 100 41 121 48 Q 151 37 174 66 Q 188 86 179 119 L 168 135 L 169 113 L 155 99 L 155 87 Q 140 99 131 109 Q 126 108 122 119 L 115 110 L 108 91 Q 102 105 84 111 L 88 94 Q 76 111 68 134 L 58 120 Z",hair,ink,2.7)
    else:
        p.path(fringes[style],hair,ink,2.8)

    # Tapered bands and fine strands follow each hairstyle's part.
    crown_curves=(
      ("M 66 90 Q 84 67 113 57 Q 99 69 83 77 Q 75 81 66 90 Z","M 124 58 Q 144 53 163 74 Q 152 67 142 66 Z","M 70 99 Q 87 91 101 77"),
      ("M 65 79 Q 89 54 113 58 Q 102 64 93 68 Q 75 70 65 79 Z","M 121 58 Q 148 50 170 75 Q 149 66 142 67 Z","M 127 67 Q 123 84 132 99"),
      ("M 62 92 Q 74 58 111 56 Q 102 64 91 68 Q 73 73 62 92 Z","M 117 60 Q 152 54 168 74 Q 151 69 139 68 Z","M 94 77 Q 87 97 76 110"),
      ("M 65 87 Q 76 56 110 55 Q 102 61 92 63 Q 74 71 65 87 Z","M 125 56 Q 149 49 171 75 Q 155 64 138 63 Z","M 76 85 Q 67 106 71 128"),
      ("M 66 91 Q 85 68 107 66 Q 100 74 87 78 Q 74 84 66 91 Z","M 125 60 Q 159 57 173 80 Q 155 72 142 72 Z","M 157 82 Q 169 95 171 109"),
      ("M 63 89 Q 76 56 103 55 Q 96 62 85 64 Q 71 74 63 89 Z","M 120 56 Q 149 48 172 76 Q 149 64 134 64 Z","M 106 67 Q 94 85 82 91"),
      ("M 65 86 Q 87 58 114 54 Q 104 61 95 65 Q 81 70 65 86 Z","M 117 54 Q 154 49 170 76 Q 155 65 139 63 Z","M 107 69 Q 104 86 99 96"),
      ("M 64 87 Q 85 57 115 54 Q 102 62 96 68 Q 78 71 64 87 Z","M 127 54 Q 154 46 173 77 Q 154 62 139 62 Z","M 117 65 Q 117 88 125 104"),
    )
    broad_left,broad_right,fine=crown_curves[style]
    def mix(a,b,k):
        return tuple(round(x+(y-x)*k) for x,y in zip(ImageColor.getrgb(a),ImageColor.getrgb(b)))
    p.path(broad_left,mix(hair,shine,.65))
    p.path(broad_right,mix(hair,shine,.58))
    p.path(fine,None,mix(shade,hair,.30),1.02)
    p.path("M 79 70 Q 90 60 101 59",None,mix(hair,shine,.83),.92)
    p.path("M 137 58 Q 151 58 159 65",None,mix(hair,shine,.88),.81)
    p.path("M 155 72 Q 168 85 170 97",None,mix(hair,shade,.61),.95)
    if style==0:
        p.path(f"M 93 54 Q 103 {29-beat*2} 126 25 Q 122 49 103 56 Z",accent,ink,2.5)
        p.path("M 98 51 Q 109 43 118 34",None,coat,1.4)
        p.path("M 87 53 Q 93 38 81 32 Q 72 47 87 53 Z",coat,ink,1.7)
        spirit(p,48,161+beat*7,accent,ink,style)
        p.star(36,134+beat*4,4,accent)
    elif style==1:
        p.path(f"M 90 49 L 82 {29+beat*3} L 96 {34+beat*3} L 104 {20+beat*3} L 112 {33+beat*3} L 127 {24+beat*3} L 123 45 Z",accent,ink,2.5)
        p.path("M 96 42 Q 109 38 120 40",None,shine,1.7)
        for x,y,r in ((183,130,5),(195,146,3),(188,118,2.7)):
            if wave>.16: p.star(x+beat*4,y-wave*11,r*wave,accent)
    elif style==2:
        p.path(f"M 141 38 Q {157+side} 10 {183+side} 19 Q {201+side} 31 180 49",None,accent,3)
        p.star(183+side,20,5,shine)
        p.path("M 77 102 Q 69 124 60 145 Q 66 155 78 148 Q 92 136 95 113",hair,ink,2)
        p.path("M 67 139 L 78 146 L 67 158 L 56 151 Z",accent,ink,2)
        p.oval((58,154,67,164),accent,ink,1.6)
    elif style==3:
        for x,y,size in ((77,74,9),(92,68,8),(151,70,9),(162,82,6)):
            p.path(f"M {x-size} {y} L {x} {y-size} L {x+size} {y} L {x} {y+size} Z",accent)
        p.path("M 152 119 L 146 127 L 155 128 L 149 136",None,accent,1.55)
        spirit(p,54,190+beat*6,hair,ink,style)
        p.path("M 69 192 Q 75 181 80 182",None,ink,1.7)
    elif style==4:
        tilt=beat*4
        p.path(f"M 65 75 Q 83 64 90 40 Q 118 12 {162+tilt} 25 Q {186+tilt} 30 181 66 Q 198 70 202 81 Q 187 98 159 80 Q 115 62 60 94 Q 43 94 53 82 Z",coat,ink,3.15)
        p.path(f"M 80 65 Q 131 41 {181+tilt} 58 L 178 69 Q 134 54 72 78 Z",dark,ink,1.8)
        p.path(f"M 116 50 Q 95 45 {97-tilt} 26 Q 111 28 123 45 Q {134+tilt} 27 150 30 Q 150 45 126 55 Z","#eda68b",ink,2)
        p.star(121,50,7,accent)
        p.star(151,92,5,accent)
        spirit(p,187,157+beat*9,dark,ink,style)
    elif style==5:
        p.path("M 86 62 Q 97 54 116 53 Q 114 57 107 61 L 99 60 Z",shine)
        p.path("M 145 60 Q 156 64 162 74",None,"#ffa2a9",2.2)
        p.path("M 87 92 Q 94 92 101 97",None,ink,1.7)
        p.path("M 139 97 Q 146 91 155 91",None,ink,1.7)
        p.path("M 119 149 L 126 155 L 120 164 L 114 155 Z",iris,ink,1.8)
        p.star(121,156,3,accent)
        p.path("M 73 75 L 81 68 L 85 72 L 77 80 Z","#ffe4b6",ink,1.15)
    elif style==6:
        for direction in (-1,1):
            x=120+direction*49
            p.path(f"M {x} 107 Q {x+direction*10} 139 {x+direction*2} 165 Q {x-direction*3} 182 {x+direction*9+side} 196 Q {x-direction*12} 187 {x-direction*9} 162 Q {x-direction*3} 131 {x-direction*5} 105 Z",hair,ink,1.4)
            p.path(f"M {x} 121 Q {x+direction*4} 145 {x-direction*1} 161 Q {x-direction*4} 177 {x+direction*4+side} 189",None,shine,1.15)
        for angle in range(5):
            x=167+cos(tau*angle/5)*7
            y=70+sin(tau*angle/5)*7
            p.oval((x-4,y-4,x+4,y+4),accent,shade,.85)
        p.oval((164,67,170,73),"#fff4cc",shade,.7)
        bx=184+sin(tau*phase)*20
        by=131+cos(tau*phase)*13
        flap=6+5*abs(sin(phase*tau*3))
        for direction in (-1,1):
            p.path(f"M {bx} {by} Q {bx+direction*flap} {by-16} {bx+direction*flap} {by-3} Q {bx+direction*flap} {by+6} {bx} {by+4} Z",accent,shade,1)
        p.path(f"M {bx} {by-1} L {bx} {by+6}",None,shine,1.35)
        p.star(bx+14,by+9,2.1,shine)
    else:
        p.path("M 140 66 Q 158 55 173 61 L 171 67 Q 156 64 143 72 Z",accent,shade,1.15)
        p.star(165,67,7,accent)
        for direction in (-1,1):
            x=120+direction*49
            p.path(f"M {x} 105 Q {x+direction*10} 139 {x+direction*5} 168 Q {x+direction*1} 196 {x+direction*17+side} 208 Q {x-direction*10} 199 {x-direction*8} 171 Q {x-direction*3} 143 {x-direction*5} 109 Z",hair,ink,1.8)
            p.path(f"M {x+direction*2} 121 Q {x+direction*8} 147 {x+direction*1} 168 Q {x+direction*1} 190 {x+direction*9+side} 198",None,shine,1.5)
        p.path("M 120 151 L 131 159 L 120 170 L 109 159 Z",dark,ink,1.4)
        p.star(120,160,5,accent)
        p.star(56-beat*8,166-wave*12,4+wave*3,accent)
        p.star(200+beat*7,157+wave*9,3+wave*2,shine)
    return p.finish()

def gif(path, frames, clear=False, delay=90):
    if clear:
        mapped=[]
        for frame in frames:
            alpha=frame.getchannel("A")
            pal=frame.convert("RGB").quantize(colors=255,method=Image.Quantize.MEDIANCUT)
            pal.paste(255,mask=alpha.point(lambda a: 255 if a<115 else 0))
            mapped.append(pal)
        mapped[0].save(path,save_all=True,append_images=mapped[1:],duration=delay,loop=0,
                       disposal=2,transparency=255,optimize=False)
    else:
        frames[0].save(path,save_all=True,append_images=frames[1:],duration=delay,loop=0,disposal=2)

def strip(path,frames,size,columns):
    rows=(len(frames)+columns-1)//columns
    atlas=Image.new("RGBA",(columns*size[0],rows*size[1]))
    for i,f in enumerate(frames):
        atlas.paste(f.resize(size,Image.Resampling.LANCZOS),(i%columns*size[0],i//columns*size[1]))
    atlas.save(path,optimize=True)

idle=[]
for i,slug in enumerate(slugs):
    still=[render(i,j/24) for j in range(24)]
    idle.append(still)
    gif(OUT/(slug+".gif"),still,clear=True)
    strip(OUT/(slug+"-idle.png"),still,(480,528),6)
    strip(OUT/(slug+"-walk.png"),[render(i,j/8,True) for j in range(8)],(96,106),4)

vw,vh=1120,740
base=Image.new("RGB",(vw,vh))
draw=ImageDraw.Draw(base)
for y in range(vh):
    k=y/vh
    draw.line((0,y,vw,y),fill=(int(16+8*k),int(26+9*k),int(37+10*k)))
font=os.environ.get("BYOW_PREVIEW_FONT")
if not font:
    system_font = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
    font = str(system_font if system_font.is_file() else Path("assets/ruins-zh.ttf"))
title=ImageFont.truetype(font,30)
label=ImageFont.truetype(font,23)
sub=ImageFont.truetype(font,14)
draw.text((560,40),"花神遗迹 · 角色预览",font=title,fill="#f6db9e",anchor="mm")
actions=("叶片轻摆","挥手与火星","摇尾与铃结","羊团轻跳","小使魔飞舞","眨眼与卷发摇动","蝶翼轻拍","羽披浮动")
for i in range(len(names)):
    l=33+i%4*270
    y=i//4*322
    accent=ImageColor.getrgb(styles[i][7])
    draw.rounded_rectangle((l,76+y,l+245,384+y),radius=17,fill="#22313e",outline=tuple(int(v*.58) for v in accent),width=2)
    draw.ellipse((l+73,309+y,l+173,319+y),fill="#192733")
    draw.text((l+123,344+y),names[i],font=label,fill=accent,anchor="mm")
    draw.text((l+123,367+y),actions[i],font=sub,fill="#b9c8d0",anchor="mm")
composite=[]
for j in range(24):
    f=base.copy()
    for i in range(len(names)):
        l=33+i%4*270
        y=i//4*322
        actor=idle[i][(j+i*4)%24].resize((219,241),Image.Resampling.LANCZOS)
        f.paste(actor,(l+13,77+y),actor)
    composite.append(f)
gif(OUT/"characters.gif",composite)
composite[3].save(OUT/"characters.png")

