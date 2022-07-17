from plane import Plane
from tkinter import *
from turtle import TurtleGraphicsError
from _tkinter import TclError

from tkinter import Canvas
from turtle import TurtleScreen, RawTurtle, TurtleGraphicsError


Map = {
    'Cape Town': (-700, 300),
    'New York': (0, 0),
    'Abu Dhabi': (-700, 1500),
    'Tokyo': (1200, 350)
}


class Game:
    def __init__(self):
        self.messages = []
        self.pln = Plane()
        self.tk = tk = Tk()
        tk.wm_title('Plane Simulator')
        tk.configure(bg='black')
        tk.bind('<Key-a>', lambda e: self.lean(-2))
        tk.bind('<Key-d>', lambda e: self.lean(+2))
        tk.bind('<Key-w>', lambda e: self.gear(+1))
        tk.bind('<Key-s>', lambda e: self.gear(-1))
        
        tk.bind('<Key-r>', lambda e: self.pull(+1))
        tk.bind('<Key-f>', lambda e: self.pull(-1))
        
        tk.bind('<Key-z>', lambda e:        self.win.set_zoom(.15))
        tk.bind('<KeyRelease-z>', lambda e: self.win.set_zoom(1))
        
        self.win = PWindow(tk, Map)
        
        self.sv = sv = Label(tk, font=('', 10), bg='black')
        sv.pack(pady=5)
        
        box = Frame(tk, bg='white')
        self.ful_ = Dial(box, 'Fuel (Km)', 'left', 75)
        self.att_ = Dial(box, 'Attitude', 'left')
        self.scr = Scrn(box, 'left')
        self.vew = Vew(box)
        self.fli_ = Dial(box, 'Flight (Km)', 'right', 75)
        self.spd_ = Dial(box, 'Gear', 'right')
        self.com = Compass(box, 'right')
        box.pack()

        Label(tk, text='◀\t\t\t\t▶', fg='white', bg='black').pack()
        
        while True:
            r = self.step()
            if isinstance(r, str):
                self.end(r); break
        
        tk.mainloop()
    
    def end(self, prob='Fuel ran off.'):
        etk = Tk()
        etk.wm_title('Game Over')
        etk.minsize(200, 50)
        Label(etk, bitmap='warning', fg='red', anchor='w').pack()
        Label(etk, text='Game Over', fg='red', anchor='w', font=('', 9, 'bold')).pack()
        Label(etk, text=prob).pack()
        
        def destroy(): etk.destroy(); self.tk.destroy()
        Button(etk, text='okay', command=destroy).pack()
        self.tk.bind('<Destroy>')
        etk.mainloop()

    def step(self):
        pln = self.pln
        resp = pln.step()
        if resp is not None: return resp
        try:
            self.win.show(pln); self.vew.show(pln)
            self.com.show(pln); self.scr.show(pln['hike'])

            self.ful_.show(int(pln['fuel'] / 100), alert=pln['fuel'] < 1000)
            self.att_.show(int(pln['at']),         alert=pln['at'] < 10)
            self.scr.show(pln['hike'])
            self.fli_.show(int(pln['travel'] / 100))
            self.spd_.show(int(pln['power']),      alert=not pln['power'])
            
            self.messages.clear()
            if pln['at'] < 18: self.messages.append(('Terrain, Pull Up! (R)', 'orange2'))
            if pln['fuel'] < 2500: self.messages.append(('Fuel is Running Low.', 'orange'))
            if pln['power'] <= 0: self.messages.append(('Engines turned off!', 'red'))
            
            if not self.messages: self.messages.append(('Good Flight!', 'green'))
            
            self.win.show_messages(self.messages)
            
        except TclError or TurtleGraphicsError:
            print(str(pln['travel'] / 100), 'Km Traveled')
            exit()
    
    def lean(self, x):
        self.pln['ang'] += x
    
    def gear(self, x):
        self.pln['power'] += x
    
    def pull(self, x):
        self.pln['hike'] += x


class PWindow(TurtleScreen):
    """ Big Wide Vew [map, compass, dir]
    """
    
    def __init__(self, master, _map=None):
        cv = Canvas(master, height=400, width=1100)
        cv.pack(anchor='center')
        super().__init__(cv, mode='logo')
        cv.configure(bg='black')
        self.delay(0)
        
        self.register_shape(
            'win dum',
            ((-1, 8), (-1, -7), (1, -7), (1, 8), (0, 9), (0, 0), (12, -2), (0, 0), (-12, -2), (0, 0), (0, -7), (-3, -9),
             (0, -7), (3, -9), (0, -7))
        )
        self.dum = RawTurtle(self, shape='win dum')
        
        self.grt1 = grt1 = RawTurtle(self, shape='square', visible=False)
        grt1.shapesize(.1)
        self.grt2 = RawTurtle(self, visible=False)
        self.grt3 = RawTurtle(self, visible=False)
        self.grt3.penup()
        self.zm = None
        self.scl = scl = RawTurtle(self, shape='square')
        scl.shapesize(outline=0)
        scl.pen(pendown=False, pencolor='gray95')
        scl.goto(0, 195)
        
        self.set_zoom(1)
        self._map = {} if _map is None else _map
    
    def show(self, plane: Plane):
        dr = plane['dir']
        self.tracer(0)
        try:
            dum = self.dum
            dum.clear()
            dum.write(str(int(dr)) + '°' + '\n\n', align='center')
            dum.pencolor('yellow' if not plane['ang'] else 'white')
            self._tracks(plane.poses)
        except TurtleGraphicsError:
            pass
        self.tracer(1)
    
    def show_messages(self, messages):
        self.tracer(0)
        self.grt3.goto(self.window_width()/2 - 20, -(self.window_height()/2 - 20))
        self.grt3.clear()
        for msg, color in messages:
            self.grt3.color(color)
            self.grt3.write(msg, align='right', font=('Consolas', 10, 'bold'))
            self.grt3.sety(self.grt3.ycor() + 25)
        self.tracer(1)
    
    def _tracks(self, posses):
        t = self.grt2
        t.pu()
        t.home()
        t.pen(pendown=True, pencolor='gray90')
        n = 0
        t.clear()
        for bnd, d_ in reversed(posses):
            t.back(d_ * self.zm)
            t.left(bnd)
            n += 1
            if n <= 98 * 2:
                t.pencolor('gray' + str(int(100 - n / 2)))
            elif n >= 99 * 2:
                t.penup()
        
        self._points(t.pos(), t.heading())
    
    def _points(self, cen, h):
        t = self.grt1
        t.clear()
        # make the rectangles for every location
        for name, (x, y) in self._map.items():
            t.pu()
            t.goto(cen)
            t.seth(h)
            t.forward(y * self.zm)
            t.right(90)
            t.forward(x * self.zm)
            t.pencolor('gray')
            self._block()
            t.pu()
            t.pencolor('white')
            if self._is_vis(*t.pos()): t.write(' ' + name, font=('', 7, ''))
            d = t.distance(0, 0)
            if (d < 170) or (d > 1000): continue
            t.seth(t.towards(0, 0))
            t.forward(d - 100)
            t.pd()
            t.forward(6)
    
    def set_zoom(self, z):
        self.zm = float(z)
        self.dum.shapesize(self.zm)
        self.scl.shapesize(self.zm * 5, .1)
    
    def _is_vis(self, x, y):
        h, w = (int(self.cv['height']) / 2), (int(self.cv['width']) / 2)
        return (-w < x < w) and (-h < y < h)
    
    def _block(self):
        t = self.grt1
        was = t.isdown()
        t.pendown()
        for _ in range(2):
            t.forward(50 * self.zm)
            t.right(90)
            t.forward(30 * self.zm)
            t.right(90)
        if not was: t.penup()


class Scrn(TurtleScreen):
    def __init__(self, master, side='left'):
        self.cv = cv = Canvas(master, height=(50), width=70)
        cv.pack(side=side, anchor='n')
        super().__init__(cv, mode='logo')
        cv.configure(relief='solid', bg='black', height=60)
        self.delay(0)
        
        self.register_shape('scrn dum',
                            ((0, 3), (-15, 3), (-20, 0), (-15, -3), (15, -3), (23, 3), (23, 12), (15, 3), (0, 3)))
        self.dum = dum = RawTurtle(self, shape='scrn dum')
        dum.pen(pencolor='gray70', fillcolor='gray70')
        dum.shapesize(.7)
        
        self.wt = wt = RawTurtle(self, visible=False)
        wt.pen(pendown=False, pencolor='white')
        wt.goto(0, -35)
    
    def show(self, hike):
        self.dum.settiltangle(hike)
        if hike > 0:
            self.dum.color("gray50")
            self.wt.color("#39FF14")
        elif not hike:
            self.dum.color("white")
            self.wt.color("white")
        else:
            self.dum.color("gray10")
            self.wt.color("orange")
        self.wt.clear()
        self.wt.write('⦣ ' + str(hike) + '°', font=('', 7, ''), align='center')


class Compass(TurtleScreen):
    def __init__(self, master, side='left'):
        self.cv = cv = Canvas(master, height=50, width=70)
        cv.pack(side=side, anchor='n')
        super().__init__(cv, mode='logo')
        cv.configure(relief='solid', bg='black', height=60)
        self.delay(0)
        
        self.t = t = RawTurtle(self, visible=False)
        t.pen(pencolor='white', pensize=3)
    
    def show(self, plane: Plane):
        self.tracer(0)
        t = self.t
        t.clear()
        t.goto(0, 0)
        t.seth(-plane['dir'])
        t.pencolor('red')
        for _ in ['red', 'white', 'white', 'white']:
            t.pencolor(_)
            t.pu()
            t.forward(10)
            t.pd()
            t.forward(9)
            t.pu()
            t.back(10 + 9)
            t.right(90)
        
        t.goto(0, -35)
        t.write('❌ ' + str(int(plane['dir'])) + '°', font=('', 7, ''), align='center')
        self.tracer(1)


class Vew(TurtleScreen):
    """ Small Vew [bend]
    """
    
    def __init__(self, master):
        self.cv = cv = Canvas(master, height=60, width=130)
        cv.pack(side='left')
        super().__init__(cv, mode='logo')
        cv.configure(relief='solid', bg='black')
        self.delay(0)
        
        self.register_shape(
            'vew pl',
            ((0, 0), (0, 2), (-1, 1.73), (-1.73, 1), (-2, 0), (-1.73, -1), (-1, -1.73), (-0, -2), (1, -1.73), (1.73, -1),
             (2, -0), (1.73, 1), (1, 1.73), (0, 2), (-20, 2), (20, 2), (0, 2), (0, 10))
        )
        
        self.pl = pl = RawTurtle(self, shape='vew pl')
        pl.goto(0, -7)
        
        self.wrt = wrt = RawTurtle(self, visible=False)
        wrt.pen(pendown=False, pencolor='white')
        wrt.goto(0, 10)
        
        self.grt = grt = RawTurtle(self, shape='square', visible=False)
        grt.shapesize(9, .001)
        grt.pen(pendown=False, pencolor='grey20', outline=0)
    
    def show(self, plane: Plane):
        self.tracer(0)
        b = plane['ang']
        self.tracer(0)
        pl = self.pl
        try:
            pl.seth(b)
            pl.color('white' if (not b) else 'orange')
            
            if b > 0:
                a = 'left';   txt = ' ' * 8 + str(b) + ' -'
            elif b < 0:
                a = 'right';  txt = '- ' + str(abs(b)) + ' ' * 8
            else:
                a = 'center'; txt = '0'
            
            pl.clear()
            pl.write(txt + '\n', align=a, font=('', 9, 'bold'))
            
            bar = self.grt
            bar.clear()
            at = plane['at']
            for i in [80, 60, 40, 20, 0, -1, -2]:
                bar.sety(pl.ycor() - at + i)
                bar.stamp()
        
        except TurtleGraphicsError:
            pass
        self.tracer(1)


class Dial(TurtleScreen):
    def __init__(self, master, title, side, width=50):
        self.cv = cv = Canvas(master, height=40, width=width)
        cv.pack(side=side, anchor='n')
        cv.bind('<Enter>', lambda _: cv.configure(height=40, bg='white'))
        cv.bind('<Leave>', lambda _: cv.configure(height=40, bg='gray90'))
        
        super().__init__(cv)
        self.delay(0)
        cv.configure(bg='gray90')
        
        cv.create_text(0, -10, text=title, font=('', 7))
        self.wt = wt = RawTurtle(self, visible=False)
        wt.pen(pendown=False, pencolor='black')
        wt.goto(0, -16)
    
    def show(self, value, alert=False):
        value = int(value)
        self.tracer(0)
        
        self.wt.clear()
        self.wt.pencolor('red' if alert else 'black')
        self.wt.write(value, align='center', font=('Segoe UI Semibold', 12, 'bold'))
        self.tracer(1)


if __name__ == '__main__':
    Game()
